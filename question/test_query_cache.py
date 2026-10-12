"""Exercise real request/cache cycles outside TestCase's implicit transaction."""

from unittest.mock import patch

from django.core.cache import cache
from django.db import connection, transaction
from django.http import Http404
from django.test import RequestFactory, TransactionTestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import resolve, reverse
from redis.exceptions import ConnectionError as RedisConnectionError

from Profile.models import SchoolClass, Student, TeacherUser, Users
from ai_asistant_with_sina.query_cache import cached_value
from question.forms import AnalysisBundleCreateForm
from question.models import (
    AnalysisBundle, AnalysisResult, Exam, ExamParticipation, ExamSnapShot,
    PromptTemplate, Question, StudentQuestionResult, SubQuestion,
)


@override_settings(
    QUERY_CACHE_ENABLED=True,
    CACHES={'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'query-cache-isolated-tests',
    }},
)
class QueryCacheTests(TransactionTestCase):
    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)
        self.user = Users.objects.create_user(username='cache-teacher', role='teacher')
        self.other_user = Users.objects.create_user(username='cache-other', role='teacher')
        self.teacher = TeacherUser.objects.create(user=self.user, first_name='Teacher', last_name='One', subject='English')
        TeacherUser.objects.create(user=self.other_user, first_name='Teacher', last_name='Two', subject='English')
        student_user = Users.objects.create_user(username='cache-student', role='student')
        self.student = Student.objects.create(
            user=student_user, full_name='Cache Student', national_code='cache-1', id_card_number='cache-1',
        )
        self.teacher.students.add(self.student)
        self.school_class = SchoolClass.objects.create(teacher=self.teacher, number=1, subject='English')
        self.student.classes.add(self.school_class)
        self.exam = Exam.objects.create(teacher=self.user, name='Cached exam', total_question=1)
        self.question = Question.objects.create(exam=self.exam, number=1)
        ExamParticipation.objects.create(exam=self.exam, student=self.student)
        self.answer = StudentQuestionResult.objects.create(
            exam=self.exam, student=self.student, question=self.question, is_correct=False,
        )
        self.prompt = PromptTemplate.objects.create(name='Cache prompt', instruction_text='test', stage='stage1')
        self.bundle = AnalysisBundle.objects.create(
            teacher=self.user, exam=self.exam, prompt_template=self.prompt,
            stage='stage1', status='success', title='Cached analysis',
        )
        self.result = AnalysisResult.objects.create(bundle=self.bundle, result_json={'revision': 1})

    def get_page(self, name, kwargs=None, *, user=None, query=None):
        path = reverse(name, kwargs=kwargs or {})
        request = RequestFactory().get(path, query or {})
        # A new user instance avoids masking request-to-request profile queries.
        request.user = Users.objects.get(pk=(user or self.user).pk)
        request.session = {}
        request._messages = []
        match = resolve(path)
        with CaptureQueriesContext(connection) as queries:
            response = match.func(request, **match.kwargs)
            if hasattr(response, 'render'):
                response.render()
        self.assertEqual(response.status_code, 200)
        return response, list(queries)

    def exam_page(self, name):
        return self.get_page(name, {'exam_id': self.exam.pk})

    def test_repeated_summary_shares_structure_with_correction(self):
        cold, cold_queries = self.exam_page('exam_summary')
        warm, warm_queries = self.exam_page('exam_summary')
        self.assertEqual(cold.content, warm.content)
        self.assertEqual(len(warm_queries), 1)  # Live ownership check.
        self.assertLess(len(warm_queries), len(cold_queries))
        self.assertIn(reverse('exam_correction', kwargs={
            'exam_id': self.exam.pk, 'student_id': self.student.pk,
        }).encode(), warm.content)
        _, queries = self.get_page('exam_correction', {
            'exam_id': self.exam.pk, 'student_id': self.student.pk,
        })
        self.assertFalse(any('FROM "question_question"' in q['sql'] for q in queries))
        self.assertFalse(any('FROM "question_subquestion"' in q['sql'] for q in queries))

    def test_structure_invalidates_on_bulk_writes(self):
        self.exam_page('exam_summary')
        Question.objects.bulk_create([Question(exam=self.exam, number=2)])
        response, _ = self.exam_page('exam_summary')
        self.assertEqual(response.context_data['total_questions'], 2)
        self.question.has_subquestion = True
        self.question.subquestion_count = 2
        Question.objects.bulk_update([self.question], ['has_subquestion', 'subquestion_count'])
        SubQuestion.objects.bulk_create([
            SubQuestion(question=self.question, number=1),
            SubQuestion(question=self.question, number=2),
        ])
        response, _ = self.exam_page('exam_summary')
        self.assertEqual(response.context_data['total_subquestions'], 2)
        self.assertEqual(len(response.context_data['questions'][0].subquestions.all()), 2)

    def test_cached_report_reflects_grading_post_immediately(self):
        _, cold_queries = self.exam_page('exam_results_report')
        _, warm_queries = self.exam_page('exam_results_report')
        self.assertEqual(len(warm_queries), 1)
        self.assertLess(len(warm_queries), len(cold_queries))
        path = reverse('exam_correction', kwargs={'exam_id': self.exam.pk, 'student_id': self.student.pk})
        request = RequestFactory().post(path, {f'result_{self.answer.pk}': 'on'})
        request.user = self.user
        match = resolve(path)
        self.assertEqual(match.func(request, **match.kwargs).status_code, 302)
        response, _ = self.exam_page('exam_results_report')
        groups = response.context_data['student_question_groups'][self.student]
        self.assertTrue(groups[0]['is_correct'])

    def test_report_reflects_admin_save_and_delete(self):
        self.exam_page('exam_results_report')
        self.answer.is_correct = True
        self.answer.save(update_fields=['is_correct'])
        response, _ = self.exam_page('exam_results_report')
        self.assertTrue(response.context_data['student_question_groups'][self.student][0]['is_correct'])
        self.answer.delete()
        response, _ = self.exam_page('exam_results_report')
        self.assertEqual(response.context_data['student_question_groups'], {})

    def test_dashboard_hit_and_membership_invalidation(self):
        _, cold_queries = self.get_page('teacher panel')
        response, warm_queries = self.get_page('teacher panel')
        self.assertEqual(len(warm_queries), 1)
        self.assertLess(len(warm_queries), len(cold_queries))
        self.assertEqual(response.context_data['student_count'], 1)
        self.teacher.students.clear()
        response, _ = self.get_page('teacher panel')
        self.assertEqual(response.context_data['student_count'], 0)
        SchoolClass.objects.bulk_create([SchoolClass(teacher=self.teacher, number=2, subject='English')])
        response, _ = self.get_page('teacher panel')
        self.assertEqual(response.context_data['class_count'], 2)

    def test_dashboard_reflects_bundle_status_update(self):
        self.get_page('teacher panel')
        AnalysisBundle.objects.filter(pk=self.bundle.pk).update(status='failure')
        response, _ = self.get_page('teacher panel')
        self.assertEqual(response.context_data['analysis_count'], 0)

    def test_classes_invalidate_for_student_edit_and_reverse_clear(self):
        _, cold_queries = self.get_page('teacher_classes')
        _, warm_queries = self.get_page('teacher_classes')
        self.assertLess(len(warm_queries), len(cold_queries))
        Student.objects.filter(pk=self.student.pk).update(full_name='Updated student')
        response, _ = self.get_page('teacher_classes')
        self.assertIn(b'Updated student', response.content)
        self.school_class.students.clear()
        response, _ = self.get_page('teacher_classes')
        self.assertNotIn(b'Updated student', response.content)

    def test_exam_list_cache_is_owner_specific_and_counts_stay_fresh(self):
        _, cold_queries = self.get_page('exam_list')
        response, warm_queries = self.get_page('exam_list')
        self.assertLess(len(warm_queries), len(cold_queries))
        self.assertEqual(len(warm_queries), 0)
        self.assertEqual(response.context_data['exams'][0].participants_count, 1)
        other_response, _ = self.get_page('exam_list', user=self.other_user)
        self.assertEqual(list(other_response.context_data['exams']), [])
        ExamParticipation.objects.filter(exam=self.exam).delete()
        response, _ = self.get_page('exam_list')
        self.assertEqual(response.context_data['exams'][0].participants_count, 0)

    def test_list_cache_preserves_page_boundaries_and_count_invalidation(self):
        AnalysisBundle.objects.bulk_create([
            AnalysisBundle(teacher=self.user, exam=self.exam, prompt_template=self.prompt, stage='stage1', title=f'Item {i}')
            for i in range(20)
        ])
        first, _ = self.get_page('my_bundles')
        second, _ = self.get_page('my_bundles', query={'page': 2})
        self.assertEqual(len(first.context_data['bundles']), 20)
        self.assertEqual(len(second.context_data['bundles']), 1)
        self.assertTrue(set(b.pk for b in first.context_data['bundles']).isdisjoint(b.pk for b in second.context_data['bundles']))
        _, queries = self.get_page('my_bundles', query={'page': 2})
        self.assertEqual(len(queries), 0)
        self.bundle.delete()
        response, _ = self.get_page('my_bundles')
        self.assertEqual(response.context_data['paginator'].count, 20)

    def test_successful_detail_is_cached_but_ownership_is_always_live(self):
        kwargs = {'pk': self.bundle.pk}
        self.get_page('bundle_detail', kwargs)
        response, queries = self.get_page('bundle_detail', kwargs)
        self.assertEqual(len(queries), 1)
        self.assertEqual(response.context_data['bundle'].result.result_json, {'revision': 1})
        with self.assertRaises(Http404):
            self.get_page('bundle_detail', kwargs, user=self.other_user)
        self.result.result_json = {'revision': 2}
        self.result.save(update_fields=['result_json'])
        response, _ = self.get_page('bundle_detail', kwargs)
        self.assertEqual(response.context_data['bundle'].result.result_json, {'revision': 2})
        Exam.objects.filter(pk=self.exam.pk).update(teacher=self.other_user)
        with self.assertRaises(Http404):
            self.get_page('bundle_detail', kwargs)

    def test_pending_detail_never_caches_status(self):
        self.bundle.status = 'pending'
        self.bundle.save(update_fields=['status'])
        _, first_queries = self.get_page('bundle_detail', {'pk': self.bundle.pk})
        response, second_queries = self.get_page('bundle_detail', {'pk': self.bundle.pk})
        self.assertEqual(len(first_queries), len(second_queries))
        self.assertEqual(response.context_data['bundle'].status, 'pending')

    def test_stage2_and_stage3_list_and_detail_cache_invalidation(self):
        for stage, list_name, detail_name in [
            ('stage2', 'analysis:stage2_result', 'analysis:stage2_student_detail'),
            ('stage3', 'exercise_generate:stage3_list', 'exercise_generate:stage3_detail'),
        ]:
            with self.subTest(stage=stage):
                bundle = AnalysisBundle.objects.create(
                    teacher=self.user, exam=self.exam, prompt_template=self.prompt,
                    stage=stage, status='success', title=f'Cached {stage}',
                )
                result = AnalysisResult.objects.create(bundle=bundle, result_json={'revision': 1}, stage=stage)
                list_kwargs = {'exam_id': self.exam.pk} if stage == 'stage2' else {}
                _, cold_queries = self.get_page(list_name, list_kwargs)
                response, warm_queries = self.get_page(list_name, list_kwargs)
                self.assertLess(len(warm_queries), len(cold_queries))
                self.assertEqual([b.pk for b in response.context_data['bundles']], [bundle.pk])
                self.get_page(detail_name, {'pk': bundle.pk})
                response, queries = self.get_page(detail_name, {'pk': bundle.pk})
                self.assertEqual(len(queries), 1)
                self.assertEqual(response.context_data['bundle'].result.result_json, {'revision': 1})
                with self.assertRaises(Http404):
                    self.get_page(detail_name, {'pk': bundle.pk}, user=self.other_user)
                result.result_json = {'revision': 2}
                result.save(update_fields=['result_json'])
                response, _ = self.get_page(detail_name, {'pk': bundle.pk})
                self.assertEqual(response.context_data['bundle'].result.result_json, {'revision': 2})
                bundle.title = f'Updated {stage}'
                bundle.save(update_fields=['title'])
                response, _ = self.get_page(list_name, list_kwargs)
                self.assertEqual(response.context_data['bundles'][0].title, f'Updated {stage}')

    def test_invalidation_waits_for_commit(self):
        self.exam_page('exam_results_report')
        old_generation = cache.get('query-cache:v1:g:grades')
        with transaction.atomic():
            StudentQuestionResult.objects.filter(pk=self.answer.pk).update(is_correct=True)
            self.assertEqual(cache.get('query-cache:v1:g:grades'), old_generation)
        self.assertNotEqual(cache.get('query-cache:v1:g:grades'), old_generation)
        response, _ = self.exam_page('exam_results_report')
        self.assertTrue(response.context_data['student_question_groups'][self.student][0]['is_correct'])

    def test_prompt_choices_are_cached_but_validation_uses_live_database(self):
        list(AnalysisBundleCreateForm(user=self.user).fields['prompt_template'].choices)
        with self.assertNumQueries(0):
            list(AnalysisBundleCreateForm(user=self.user).fields['prompt_template'].choices)
        self.prompt.is_active = False
        self.prompt.save(update_fields=['is_active'])
        field = AnalysisBundleCreateForm(user=self.user).fields['prompt_template']
        self.assertNotIn(self.prompt.pk, [value for value, label in field.choices])
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            field.clean(self.prompt.pk)

    def test_snapshot_summary_and_list_reflect_new_snapshot(self):
        run = lambda: self.get_page('analysis:stage2_run', query={'exam': self.exam.pk})
        response, _ = run()
        self.assertFalse(response.context_data['snapshot_info']['exists'])
        first = ExamSnapShot.objects.create(exam=self.exam, data={'students': [{}]})
        response, _ = run()
        self.assertEqual(response.context_data['snapshot_info']['snapshot_id'], first.pk)
        self.exam_page('exam_snapshot_list')
        latest = ExamSnapShot.objects.create(exam=self.exam, data={'students': [{}, {}]})
        response, _ = run()
        self.assertEqual(response.context_data['snapshot_info']['snapshot_id'], latest.pk)
        self.assertEqual(response.context_data['snapshot_info']['student_count'], 2)
        response, _ = self.exam_page('exam_snapshot_list')
        self.assertEqual(response.context_data['paginator'].count, 2)

    def test_rollback_does_not_publish_or_invalidate_cached_data(self):
        self.exam_page('exam_results_report')
        try:
            with transaction.atomic():
                StudentQuestionResult.objects.filter(pk=self.answer.pk).update(is_correct=True)
                response, _ = self.exam_page('exam_results_report')
                self.assertTrue(response.context_data['student_question_groups'][self.student][0]['is_correct'])
                raise RuntimeError('rollback')
        except RuntimeError:
            pass
        response, queries = self.exam_page('exam_results_report')
        self.assertEqual(len(queries), 1)
        self.assertFalse(response.context_data['student_question_groups'][self.student][0]['is_correct'])

    def test_cache_outage_falls_back_to_database(self):
        with patch('ai_asistant_with_sina.query_cache.cache.get_many', side_effect=RedisConnectionError('offline')):
            with self.assertLogs('ai_asistant_with_sina.query_cache', level='WARNING'):
                response, _ = self.exam_page('exam_results_report')
        self.assertEqual(len(response.context_data['student_question_groups']), 1)

    def test_missing_generation_cannot_resurrect_stale_values(self):
        cached_value('test', (), ('test-group',), 60, lambda: 'old')
        cache.delete('query-cache:v1:g:test-group')
        self.assertEqual(cached_value('test', (), ('test-group',), 60, lambda: 'new'), 'new')

    @override_settings(QUERY_CACHE_ENABLED=False)
    def test_disabled_cache_keeps_reads_live(self):
        self.exam_page('exam_results_report')
        response, queries = self.exam_page('exam_results_report')
        self.assertGreater(len(queries), 1)
        self.assertEqual(response.status_code, 200)
