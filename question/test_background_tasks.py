import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection, transaction
from django.test import Client, TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from kombu.exceptions import OperationalError

from Profile.models import Users
from question.models import AnalysisBundle, AnalysisResult, ChatRequest, Exam, ExamSnapShot, PromptTemplate
from question.services.background import enqueue_after_commit
from question.tasks import process_analysis_bundle, process_chat_request


def response():
    return SimpleNamespace(
        parsed_json={'answer': 'ready'}, raw_output_text='{"answer":"ready"}',
        response_id='response-test', usage={'total_tokens': 10},
    )


class BackgroundFixtures:
    def setUp(self):
        super().setUp()
        self.media = tempfile.TemporaryDirectory()
        self.addCleanup(self.media.cleanup)
        config = override_settings(MEDIA_ROOT=self.media.name)
        config.enable()
        self.addCleanup(config.disable)
        self.teacher = Users.objects.create_user(username='background-teacher', role='teacher')
        self.exam = Exam.objects.create(teacher=self.teacher, name='Background exam')
        self.prompts = {
            stage: PromptTemplate.objects.create(
                name=stage, stage=stage, instruction_text='{{STAGE2_JSON}} {{EXAM_MAP_JSON}} {{STUDENT_ANSWERS}}',
                schema_json={'type': 'object'},
            ) for stage in ['stage1', 'stage2', 'stage3']
        }
        self.client.force_login(self.teacher)

    def bundle(self, stage='stage1', **kwargs):
        return AnalysisBundle.objects.create(
            teacher=self.teacher, exam=self.exam, prompt_template=self.prompts[stage],
            stage=stage, status='pending', **kwargs,
        )

    def completed_bundle(self, stage):
        bundle = self.bundle(stage)
        bundle.status = 'success'
        bundle.save(update_fields=['status'])
        AnalysisResult.objects.create(bundle=bundle, result_json={'source': stage}, stage=stage)
        return bundle

    def pdf(self, name='test.pdf'):
        return SimpleUploadedFile(name, b'%PDF-1.4 test', content_type='application/pdf')


@override_settings(QUERY_CACHE_ENABLED=False, DJANGO_DEBUG=False)
class BackgroundSubmissionTests(BackgroundFixtures, TestCase):
    @patch('question.tasks.OpenAIAnalyzer')
    @patch('question.tasks.process_analysis_bundle.apply_async')
    def test_stage_one_returns_before_api_and_queues_after_commit(self, submit, analyzer):
        with self.captureOnCommitCallbacks(execute=True):
            result = self.client.post(reverse('bundle_create'), {
                'title': 'Queued', 'exam': self.exam.pk,
                'prompt_template': self.prompts['stage1'].pk,
                'lesson_pdf': self.pdf('lesson.pdf'), 'example_pdf': self.pdf('exam.pdf'),
            })
            submit.assert_not_called()
        bundle = AnalysisBundle.objects.get(title='Queued')
        self.assertRedirects(result, reverse('bundle_detail', args=[bundle.pk]))
        submit.assert_called_once_with(args=[bundle.pk], retry=False)
        analyzer.assert_not_called()
        self.assertEqual(bundle.status, 'pending')
        self.assertTrue(Path(bundle.lesson_pdf.path).exists())

    @patch('question.tasks.process_analysis_bundle.apply_async')
    def test_stage_two_queues_a_job_for_each_student_with_frozen_inputs(self, submit):
        first = self.completed_bundle('stage1')
        snapshot = ExamSnapShot.objects.create(exam=self.exam, data={'students': [
            {'student_id': 10, 'full_name': 'First'}, {'student_id': 11, 'full_name': 'Second'},
        ]})
        with self.captureOnCommitCallbacks(execute=True):
            result = self.client.post(reverse('analysis:stage2_run'), {
                'exam': self.exam.pk, 'stage1_bundle_id': first.pk,
                'stage2_prompt': self.prompts['stage2'].pk,
            })
            submit.assert_not_called()
        self.assertEqual(result.status_code, 302)
        bundles = list(AnalysisBundle.objects.filter(stage='stage2').order_by('pk'))
        self.assertEqual(len(bundles), 2)
        self.assertEqual(submit.call_count, 2)
        self.assertEqual(bundles[0].input_json['SNAPSHOT_ID'], snapshot.pk)
        self.assertEqual(bundles[0].input_json['STUDENT_ANSWERS']['student_id'], 10)
        self.assertTrue(all(bundle.status == 'pending' for bundle in bundles))

    @patch('question.tasks.process_analysis_bundle.apply_async')
    def test_stage_three_saves_pdf_before_dispatch(self, submit):
        second = self.completed_bundle('stage2')
        with self.captureOnCommitCallbacks(execute=True):
            result = self.client.post(reverse('exercise_generate:stage3_run'), {
                'stage2_bundle': second.pk, 'stage3_prompt': self.prompts['stage3'].pk,
                'question_bank_pdf': self.pdf(),
            })
        bundle = AnalysisBundle.objects.get(stage='stage3')
        self.assertRedirects(result, reverse('exercise_generate:stage3_detail', args=[bundle.pk]))
        self.assertTrue(Path(bundle.lesson_pdf.path).exists())
        self.assertEqual(bundle.input_json['STAGE2_JSON'], {'source': 'stage2'})
        self.assertEqual(bundle.model_name, 'gpt-4.1-mini')
        submit.assert_called_once_with(args=[bundle.pk], retry=False)

    @patch('question.tasks.process_chat_request.apply_async')
    def test_chat_post_redirects_and_refresh_never_resubmits(self, submit):
        with self.captureOnCommitCallbacks(execute=True):
            result = self.client.post(reverse('chat'), {'q': 'hello'})
        chat = ChatRequest.objects.get(user=self.teacher)
        submit.assert_called_once_with(args=[chat.pk], retry=False)
        for _ in range(2):
            page = self.client.get(result.url)
            self.assertContains(page, 'data-job-id')
        self.assertEqual(submit.call_count, 1)
        self.assertEqual(ChatRequest.objects.count(), 1)

    def test_queue_outage_persists_failure(self):
        bundle = self.bundle()
        task = Mock()
        task.apply_async.side_effect = OperationalError('offline')
        with self.assertLogs('question.services.background', level='ERROR'):
            with self.captureOnCommitCallbacks(execute=True):
                enqueue_after_commit(task, bundle)
        bundle.refresh_from_db()
        self.assertEqual(bundle.status, 'failure')
        self.assertTrue(bundle.error_message)

    def test_rollback_does_not_publish(self):
        task = Mock()
        with self.captureOnCommitCallbacks(execute=True):
            with self.assertRaises(ValueError):
                with transaction.atomic():
                    enqueue_after_commit(task, self.bundle())
                    raise ValueError('rollback')
        task.apply_async.assert_not_called()
        self.assertFalse(AnalysisBundle.objects.exists())

    def test_status_is_fresh_and_other_users_records_are_private(self):
        bundle = self.bundle()
        other = Users.objects.create_user(username='another-background-teacher', role='teacher')
        other_exam = Exam.objects.create(teacher=other)
        foreign = AnalysisBundle.objects.create(teacher=other, exam=other_exam, prompt_template=self.prompts['stage1'])
        url = reverse('bundle_status') + f'?ids={bundle.pk},{foreign.pk}'
        result = self.client.get(url)
        self.assertEqual(result.json()['statuses'], {str(bundle.pk): 'pending'})
        self.assertEqual(result['Cache-Control'], 'no-store')
        AnalysisBundle.objects.filter(pk=bundle.pk).update(status='success')
        self.assertEqual(self.client.get(url).json()['statuses'], {str(bundle.pk): 'success'})
        chat = ChatRequest.objects.create(user=other, prompt='private')
        self.assertEqual(self.client.get(reverse('chat_request_status', args=[chat.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse('chat') + f'?request={chat.pk}').status_code, 404)

    def test_invalid_status_ids_and_empty_chat_are_handled(self):
        self.assertEqual(self.client.get(reverse('bundle_status'), {'ids': 'invalid'}).status_code, 400)
        self.assertEqual(self.client.get(reverse('chat') + '?request=invalid').status_code, 400)
        self.assertEqual(self.client.post(reverse('chat'), {'q': '  '}).status_code, 200)
        self.assertFalse(ChatRequest.objects.exists())

    def test_chat_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.teacher)
        self.assertEqual(client.post(reverse('chat'), {'q': 'test'}).status_code, 403)

    def test_processing_pages_have_status_polling_and_no_false_failure(self):
        for stage, route in [
            ('stage1', 'bundle_detail'), ('stage2', 'analysis:stage2_student_detail'),
            ('stage3', 'exercise_generate:stage3_detail'),
        ]:
            with self.subTest(stage=stage):
                bundle = self.bundle(stage)
                bundle.status = 'processing'
                bundle.save(update_fields=['status'])
                page = self.client.get(reverse(route, args=[bundle.pk]))
                self.assertContains(page, 'job-status.js')
                self.assertContains(page, 'data-job-status="processing"')
                self.assertContains(page, 'پاسخ در حال آماده‌سازی')
                self.assertNotContains(page, '> ناموفق</span>')


@override_settings(QUERY_CACHE_ENABLED=False)
class BackgroundWorkerTests(BackgroundFixtures, TransactionTestCase):
    @patch('question.tasks.OpenAIAnalyzer')
    def test_all_stages_persist_results_without_holding_api_transactions(self, analyzer_class):
        analyzer = analyzer_class.return_value
        analyzer.upload_pdf.return_value = 'file-test'

        def answer(**kwargs):
            self.assertFalse(connection.in_atomic_block)
            return response()

        analyzer.analyze.side_effect = answer
        analyzer.analyze_text.side_effect = answer
        for stage in ['stage1', 'stage2', 'stage3']:
            with self.subTest(stage=stage):
                bundle = self.bundle(
                    stage, lesson_pdf=self.pdf('lesson.pdf'), example_pdf=self.pdf('exam.pdf'),
                    input_json={'EXAM_MAP_JSON': {'map': 1}, 'STUDENT_ANSWERS': {'student_id': 1}, 'STAGE2_JSON': {'level': 'weak'}},
                )
                process_analysis_bundle.run(bundle.pk)
                bundle.refresh_from_db()
                self.assertEqual(bundle.status, 'success')
                self.assertEqual(bundle.result.stage, stage)
                self.assertEqual(bundle.result.result_json, {'answer': 'ready'})
                self.assertEqual(bundle.result.openai_response_id, 'response-test')
                if stage == 'stage3':
                    self.assertEqual(bundle.openai_example_file_id, 'file-test')

    @patch('question.tasks.OpenAIAnalyzer')
    def test_duplicate_delivery_does_not_repeat_paid_request(self, analyzer_class):
        analyzer_class.return_value.analyze_text.return_value = response()
        bundle = self.bundle('stage2', input_json={'EXAM_MAP_JSON': {}, 'STUDENT_ANSWERS': {}})
        process_analysis_bundle.run(bundle.pk)
        process_analysis_bundle.run(bundle.pk)
        analyzer_class.return_value.analyze_text.assert_called_once()
        self.assertEqual(AnalysisResult.objects.filter(bundle=bundle).count(), 1)

    @patch('question.tasks.OpenAIAnalyzer')
    def test_api_failure_is_saved_and_visible(self, analyzer_class):
        analyzer_class.return_value.analyze_text.side_effect = RuntimeError('API failed')
        bundle = self.bundle('stage2', input_json={'EXAM_MAP_JSON': {}, 'STUDENT_ANSWERS': {}})
        with self.assertLogs('question.tasks', level='ERROR'):
            process_analysis_bundle.run(bundle.pk)
        bundle.refresh_from_db()
        self.assertEqual(bundle.status, 'failure')
        self.assertEqual(bundle.error_message, 'API failed')
        self.assertFalse(AnalysisResult.objects.filter(bundle=bundle).exists())

    @patch('question.tasks.OpenAIAnalyzer')
    def test_missing_stage_three_schema_fails_before_upload(self, analyzer_class):
        self.prompts['stage3'].schema_json = {}
        self.prompts['stage3'].save()
        bundle = self.bundle('stage3', lesson_pdf=self.pdf(), input_json={'STAGE2_JSON': {}})
        with self.assertLogs('question.tasks', level='ERROR'):
            process_analysis_bundle.run(bundle.pk)
        bundle.refresh_from_db()
        self.assertEqual(bundle.status, 'failure')
        analyzer_class.return_value.upload_pdf.assert_not_called()

    @patch('question.tasks.OpenAI')
    def test_chat_worker_persists_answer_and_ignores_duplicate(self, client):
        client.return_value.responses.create.return_value = SimpleNamespace(output_text='answer')
        chat = ChatRequest.objects.create(user=self.teacher, prompt='hello')
        process_chat_request.run(chat.pk)
        process_chat_request.run(chat.pk)
        chat.refresh_from_db()
        self.assertEqual(chat.status, 'success')
        self.assertEqual(chat.answer, 'answer')
        client.return_value.responses.create.assert_called_once_with(model='gpt-5.2', input='hello')

    @patch('question.tasks.OpenAI')
    def test_chat_worker_saves_api_failure(self, client):
        client.return_value.responses.create.side_effect = RuntimeError('chat failed')
        chat = ChatRequest.objects.create(user=self.teacher, prompt='hello')
        with self.assertLogs('question.tasks', level='ERROR'):
            process_chat_request.run(chat.pk)
        chat.refresh_from_db()
        self.assertEqual(chat.status, 'failure')
        self.assertEqual(chat.error_message, 'chat failed')
