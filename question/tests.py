from django.test import TestCase
from django.urls import reverse

from Profile.models import Users
from question.models import AnalysisBundle, Exam, PromptTemplate


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

    def test_bundle_create_form_only_accepts_logged_in_teachers_exams(self):
        response = self.client.get(reverse("bundle_create"))

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["form"].fields["exam"].queryset,
            [self.own_exam],
        )
