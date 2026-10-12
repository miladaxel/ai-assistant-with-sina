from django.test import TestCase, override_settings
from django.urls import reverse

from django.db import connection
from django.contrib import admin
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext

from Profile.models import SchoolClass, Student, TeacherUser, Users
from question.forms import QuestionHasSubFormSet, QuestionSubCountFormSet
from question.mixins import TeacherRequiredMixin
from question.models import (
    AnalysisBundle, AnalysisResult, Exam, ExamParticipation, ExamSnapShot,
    PromptTemplate, Question, StudentQuestionResult, SubQuestion,
)


@override_settings(QUERY_CACHE_ENABLED=False)
class TeacherObjectIsolationTests(TestCase):
    def setUp(self):
        self.teacher = Users.objects.create_user(
            username="teacher_one", password="test-pass", role="teacher"
        )
        self.other_teacher = Users.objects.create_user(
            username="teacher_two", password="test-pass", role="teacher"
        )
        self.own_exam = Exam.objects.create(
            teacher=self.teacher, name="Own exam", total_question=1
        )
        self.other_exam = Exam.objects.create(
            teacher=self.other_teacher, name="Other exam", total_question=1
        )
        self.prompt = PromptTemplate.objects.create(
            name="Stage one prompt",
            version=1,
            instruction_text="test",
            schema_json={},
            stage=PromptTemplate.STAGE_ONE,
        )
        self.own_bundle = AnalysisBundle.objects.create(
            teacher=self.teacher,
            exam=self.own_exam,
            prompt_template=self.prompt,
            stage=AnalysisBundle.STAGE_ONE,
            status=AnalysisBundle.STATUS_SUCCESS,
        )
        self.other_bundle = AnalysisBundle.objects.create(
            teacher=self.other_teacher,
            exam=self.other_exam,
            prompt_template=self.prompt,
            stage=AnalysisBundle.STAGE_ONE,
            status=AnalysisBundle.STATUS_SUCCESS,
        )
        self.client.force_login(self.teacher)

    def test_exam_and_bundle_lists_only_show_logged_in_teachers_objects(self):
        exam_response = self.client.get(reverse("exam_list"))
        bundle_response = self.client.get(reverse("my_bundles"))

        self.assertEqual(exam_response.status_code, 200)
        self.assertQuerySetEqual(exam_response.context["exams"], [self.own_exam])
        self.assertEqual(bundle_response.status_code, 200)
        self.assertQuerySetEqual(bundle_response.context["bundles"], [self.own_bundle])

    def test_other_teachers_exam_and_bundle_detail_return_404(self):
        exam_response = self.client.get(
            reverse("exam_summary", kwargs={"exam_id": self.other_exam.pk})
        )
        bundle_response = self.client.get(
            reverse("bundle_detail", kwargs={"pk": self.other_bundle.pk})
        )

        self.assertEqual(exam_response.status_code, 404)
        self.assertEqual(bundle_response.status_code, 404)

    def test_exam_summary_uses_six_uncached_queries_and_calculates_totals(self):
        Question.objects.create(
            exam=self.own_exam,
            number=1,
            has_subquestion=True,
            subquestion_count=2,
        )
        Question.objects.create(
            exam=self.own_exam,
            number=2,
            has_subquestion=True,
            subquestion_count=3,
        )

        # The shared structure also preloads subquestions for correction pages.
        with self.assertNumQueries(6):
            response = self.client.get(
                reverse("exam_summary", kwargs={"exam_id": self.own_exam.pk})
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_questions"], 2)
        self.assertEqual(response.context["total_subquestions"], 5)
        self.assertEqual(
            [question.number for question in response.context["questions"]],
            [1, 2],
        )
        self.assertContains(response, 'src="/static/js/exam.js"')

    def test_bundle_create_form_only_accepts_logged_in_teachers_exams(self):
        response = self.client.get(reverse("bundle_create"))

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["form"].fields["exam"].queryset,
            [self.own_exam],
        )


@override_settings(QUERY_CACHE_ENABLED=False)
class QueryOptimizationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher = Users.objects.create_user(username="query-teacher", role="teacher")
        cls.profile = TeacherUser.objects.create(
            user=cls.teacher, subject="English", first_name="Query", last_name="Teacher",
        )
        cls.exam = Exam.objects.create(teacher=cls.teacher, name="Query exam")
        cls.students = []
        for i in range(4):
            user = Users.objects.create_user(username=f"query-student-{i}", role="student")
            student = Student.objects.create(
                user=user, full_name=f"Student {i}", fathers_name="Father",
                national_code=f"n{i}", id_card_number=f"i{i}",
                birth_date="2000-01-01", birth_place="Tehran",
                home_phone_number="", transition="",
            )
            cls.students.append(student)
            ExamParticipation.objects.create(exam=cls.exam, student=student)
        cls.simple = Question.objects.create(exam=cls.exam, number=1)
        cls.parent = Question.objects.create(
            exam=cls.exam, number=2, has_subquestion=True, subquestion_count=2,
        )
        cls.subquestions = [
            SubQuestion.objects.create(question=cls.parent, number=i) for i in (1, 2)
        ]
        cls.prompt = PromptTemplate.objects.create(
            name="Query prompt", version=1, instruction_text="test", schema_json={},
        )
        cls.bundles = [
            AnalysisBundle.objects.create(
                teacher=cls.teacher, exam=cls.exam, prompt_template=cls.prompt,
                title=f"Bundle {i}", stage=AnalysisBundle.STAGE_ONE,
            ) for i in range(5)
        ]

    def setUp(self):
        self.client.force_login(self.teacher)

    def correction_url(self, student=None):
        return reverse("exam_correction", kwargs={
            "exam_id": self.exam.pk,
            "student_id": (student or self.students[0]).pk,
        })

    def test_bundle_list_and_detail_have_fixed_query_counts(self):
        with self.assertNumQueries(4):
            response = self.client.get(reverse("my_bundles"))
        self.assertContains(response, "Query exam", count=5)
        AnalysisResult.objects.create(bundle=self.bundles[0], result_json={})
        with self.assertNumQueries(3):
            response = self.client.get(reverse("bundle_detail", kwargs={"pk": self.bundles[0].pk}))
        self.assertEqual(response.status_code, 200)

    def test_participant_list_has_no_per_student_queries(self):
        with self.assertNumQueries(4):
            response = self.client.get(reverse("exam_participation_list", kwargs={"exam_id": self.exam.pk}))
        for student in self.students:
            self.assertContains(response, student.full_name)

    def test_correction_preserves_grades_and_creates_missing_rows_once(self):
        existing = StudentQuestionResult.objects.create(
            exam=self.exam, student=self.students[0], question=self.simple, is_correct=True,
        )
        response = self.client.get(self.correction_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["results"]), 3)
        existing.refresh_from_db()
        self.assertTrue(existing.is_correct)
        first_ids = [r.pk for r in response.context["results"]]
        response = self.client.get(self.correction_url())
        self.assertEqual(first_ids, [r.pk for r in response.context["results"]])
        self.assertEqual(StudentQuestionResult.objects.count(), 3)

    def test_correction_read_queries_do_not_grow_with_question_count(self):
        self.client.get(self.correction_url())
        with CaptureQueriesContext(connection) as small:
            self.client.get(self.correction_url())
        Question.objects.bulk_create([
            Question(exam=self.exam, number=i) for i in range(3, 23)
        ])
        self.client.get(self.correction_url())
        with CaptureQueriesContext(connection) as large:
            response = self.client.get(self.correction_url())
        self.assertEqual(len(small), len(large))
        self.assertEqual(len(large), 10)
        self.assertEqual(len(response.context["results"]), 23)
        self.assertEqual(sum(q["sql"].startswith("SELECT") for q in large), 8)

    def test_grading_uses_two_updates_and_cannot_modify_another_student(self):
        self.client.get(self.correction_url())
        own_results = list(StudentQuestionResult.objects.filter(student=self.students[0]))
        original_graded_at = own_results[0].graded_at
        foreign = StudentQuestionResult.objects.create(
            exam=self.exam, student=self.students[1], question=self.simple, is_correct=False,
        )
        with CaptureQueriesContext(connection) as queries:
            response = self.client.post(self.correction_url(), {
                f"result_{own_results[0].pk}": "on",
                f"result_{foreign.pk}": "on",
                "result_9999999999999999999": "on",
            })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(sum(q["sql"].startswith("UPDATE") for q in queries), 2)
        own_results[0].refresh_from_db()
        self.assertTrue(own_results[0].is_correct)
        self.assertEqual(own_results[0].graded_at, original_graded_at)
        self.assertFalse(StudentQuestionResult.objects.filter(
            student=self.students[0], is_correct=True,
        ).exclude(pk=own_results[0].pk).exists())
        foreign.refresh_from_db()
        self.assertFalse(foreign.is_correct)

    def test_snapshot_reads_all_students_answers_in_six_queries(self):
        for student in self.students:
            StudentQuestionResult.objects.create(
                exam=self.exam, student=student, question=self.simple, is_correct=True,
            )
            StudentQuestionResult.objects.create(
                exam=self.exam, student=student, subquestion=self.subquestions[0], is_correct=False,
            )
        with self.assertNumQueries(6):
            response = self.client.post(reverse("exam_snapshot_create", kwargs={"exam_id": self.exam.pk}))
        self.assertEqual(response.status_code, 302)
        snapshot = ExamSnapShot.objects.get(exam=self.exam)
        self.assertEqual(len(snapshot.data["students"]), 4)
        for student in snapshot.data["students"]:
            self.assertEqual(len(student["results"]), 2)
            self.assertEqual({r["type"] for r in student["results"]}, {"question", "subquestion"})

    def test_subquestion_setup_can_grow_and_shrink_in_one_submission(self):
        extra = Question.objects.create(
            exam=self.exam, number=3, has_subquestion=True, subquestion_count=1,
        )
        SubQuestion.objects.create(question=extra, number=1)
        response = self.client.post(reverse("exam_sub_question_setup", kwargs={"exam_id": self.exam.pk}), {
            "form-TOTAL_FORMS": "2", "form-INITIAL_FORMS": "2",
            "form-MIN_NUM_FORMS": "0", "form-MAX_NUM_FORMS": "1000",
            "form-0-id": str(self.parent.pk), "form-0-subquestion_count": "1",
            "form-1-id": str(extra.pk), "form-1-subquestion_count": "3",
        })
        self.assertEqual(response.status_code, 302)
        self.parent.refresh_from_db()
        extra.refresh_from_db()
        self.assertEqual(self.parent.subquestion_count, 1)
        self.assertEqual(extra.subquestion_count, 3)
        self.assertEqual(list(self.parent.subquestions.values_list("number", flat=True)), [1])
        self.assertEqual(list(extra.subquestions.order_by("number").values_list("number", flat=True)), [1, 2, 3])

    def test_report_groups_subquestions_and_marks_mixed_answers_incorrect(self):
        for sub, is_correct in zip(self.subquestions, (True, False)):
            StudentQuestionResult.objects.create(
                exam=self.exam, student=self.students[0], subquestion=sub, is_correct=is_correct,
            )
        with self.assertNumQueries(4):
            response = self.client.get(reverse("exam_results_report", kwargs={"exam_id": self.exam.pk}))
        groups = response.context["student_question_groups"][self.students[0]]
        self.assertEqual(len(groups), 1)
        self.assertFalse(groups[0]["is_correct"])
        self.assertEqual(len(groups[0]["subresults"]), 2)
        self.assertContains(response, '<div class="q-title">سوال 2</div>', count=1)

    def test_optimized_writes_still_reject_other_teachers(self):
        other = Users.objects.create_user(username="other-query-teacher", role="teacher")
        self.client.force_login(other)
        response = self.client.get(self.correction_url())
        self.assertEqual(response.status_code, 404)
        response = self.client.post(self.correction_url(), {})
        self.assertEqual(response.status_code, 404)
        response = self.client.post(reverse("exam_snapshot_create", kwargs={"exam_id": self.exam.pk}))
        self.assertEqual(response.status_code, 404)

    def test_question_formsets_validate_many_rows_with_one_query(self):
        questions = list(Question.objects.filter(exam=self.exam))
        for formset_class, field, value in (
            (QuestionHasSubFormSet, "has_subquestion", "on"),
            (QuestionSubCountFormSet, "subquestion_count", "3"),
        ):
            data = {
                "form-TOTAL_FORMS": str(len(questions)),
                "form-INITIAL_FORMS": str(len(questions)),
                "form-MIN_NUM_FORMS": "0", "form-MAX_NUM_FORMS": "1000",
            }
            for i, question in enumerate(questions):
                data[f"form-{i}-id"] = str(question.pk)
                data[f"form-{i}-{field}"] = value
            with self.assertNumQueries(1):
                formset = formset_class(data, queryset=Question.objects.filter(exam=self.exam))
                self.assertTrue(formset.is_valid(), formset.errors)

    def test_formsets_reject_question_id_outside_the_exam(self):
        other_exam = Exam.objects.create(teacher=self.teacher, name="Other exam")
        other_question = Question.objects.create(exam=other_exam, number=1)
        formset = QuestionSubCountFormSet({
            "form-TOTAL_FORMS": "1", "form-INITIAL_FORMS": "1",
            "form-MIN_NUM_FORMS": "0", "form-MAX_NUM_FORMS": "1000",
            "form-0-id": str(other_question.pk), "form-0-subquestion_count": "3",
        }, queryset=Question.objects.filter(exam=self.exam))
        self.assertFalse(formset.is_valid())
        self.assertIn("id", formset.errors[0])

    def test_student_detail_prefetches_class_list_once(self):
        self.profile.students.add(self.students[0])
        school_class = SchoolClass.objects.create(teacher=self.profile, number=1, subject="English")
        self.students[0].classes.add(school_class)
        with self.assertNumQueries(5):
            response = self.client.get(reverse("student_detail", kwargs={"pk": self.students[0].pk}))
        self.assertContains(response, "English")

    def test_admin_string_representations_do_not_trigger_per_row_queries(self):
        StudentQuestionResult.objects.create(
            exam=self.exam, student=self.students[0], subquestion=self.subquestions[0],
        )
        ExamSnapShot.objects.create(exam=self.exam, data={})
        req = RequestFactory().get("/admin/")
        req.user = self.teacher
        for model in (Question, SubQuestion, StudentQuestionResult, ExamSnapShot):
            model_admin = admin.site._registry[model]
            changelist = model_admin.get_changelist_instance(req)
            with self.assertNumQueries(1):
                for obj in changelist.queryset:
                    self.assertTrue(str(obj))

    def test_admin_question_choice_labels_load_relations_once(self):
        req = RequestFactory().get("/admin/")
        req.user = self.teacher
        model_admin = admin.site._registry[StudentQuestionResult]
        for field_name in ("question", "subquestion"):
            field = model_admin.formfield_for_foreignkey(
                StudentQuestionResult._meta.get_field(field_name), req,
            )
            with self.assertNumQueries(1):
                for value, label in field.choices:
                    self.assertTrue(str(label))

    def test_result_lists_have_navigation_to_the_remaining_rows(self):
        for stage, url in (
            (AnalysisBundle.STAGE_TWO, reverse("analysis:stage2_result", kwargs={"exam_id": self.exam.pk})),
            (AnalysisBundle.STAGE_THREE, reverse("exercise_generate:stage3_list")),
        ):
            AnalysisBundle.objects.bulk_create([
                AnalysisBundle(teacher=self.teacher, exam=self.exam, prompt_template=self.prompt, stage=stage)
                for _ in range(21)
            ])
            response = self.client.get(url)
            self.assertEqual(len(response.context["bundles"]), 20)
            self.assertContains(response, '?page=2')
            page_two = self.client.get(url, {"page": 2})
            self.assertEqual(len(page_two.context["bundles"]), 1)
        ExamSnapShot.objects.bulk_create([
            ExamSnapShot(exam=self.exam, data={}) for _ in range(11)
        ])
        url = reverse("exam_snapshot_list", kwargs={"exam_id": self.exam.pk})
        response = self.client.get(url)
        self.assertEqual(len(response.context["snapshots"]), 10)
        self.assertContains(response, '?page=2')
        self.assertEqual(len(self.client.get(url, {"page": 2}).context["snapshots"]), 1)

    def test_stage3_detail_handles_missing_and_wrong_stage_results(self):
        bundle = AnalysisBundle.objects.create(
            teacher=self.teacher, exam=self.exam, prompt_template=self.prompt,
            stage=AnalysisBundle.STAGE_THREE,
        )
        url = reverse("exercise_generate:stage3_detail", kwargs={"pk": bundle.pk})
        with self.assertNumQueries(3):
            response = self.client.get(url)
        self.assertIsNone(response.context["result"])
        result = AnalysisResult.objects.create(bundle=bundle, result_json={}, stage=AnalysisResult.STAGE_TWO)
        self.assertIsNone(self.client.get(url).context["result"])
        result.stage = AnalysisResult.STAGE_THREE
        result.save(update_fields=["stage"])
        with self.assertNumQueries(3):
            response = self.client.get(url)
        self.assertEqual(response.context["result"], result)

    def test_teacher_mixin_skips_profile_query_without_changing_fallback(self):
        req = RequestFactory().get("/")
        req.user = Users.objects.get(pk=self.teacher.pk)
        mixin = TeacherRequiredMixin()
        mixin.request = req
        with self.assertNumQueries(0):
            self.assertTrue(mixin.test_func())
        Users.objects.filter(pk=self.teacher.pk).update(role="")
        req.user = Users.objects.get(pk=self.teacher.pk)
        with self.assertNumQueries(1):
            self.assertTrue(mixin.test_func())

    def test_saving_unchanged_profile_does_not_update_user_role(self):
        with CaptureQueriesContext(connection) as queries:
            self.profile.first_name = "Updated"
            self.profile.save(update_fields=["first_name"])
        self.assertEqual(sum(q["sql"].startswith("UPDATE") for q in queries), 1)
