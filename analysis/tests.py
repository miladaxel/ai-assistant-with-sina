from django.test import TestCase
from django.urls import reverse

from Profile.models import Users
from question.models import AnalysisBundle, Exam, PromptTemplate


class Stage2TeacherIsolationTests(TestCase):
    def setUp(self):
        self.teacher = Users.objects.create_user(
            username="stage2_teacher_one", password="test-pass", role="teacher"
        )
        self.other_teacher = Users.objects.create_user(
            username="stage2_teacher_two", password="test-pass", role="teacher"
        )
        self.own_exam = Exam.objects.create(
            teacher=self.teacher, name="Own exam", total_question=1
        )
        self.other_exam = Exam.objects.create(
            teacher=self.other_teacher, name="Other exam", total_question=1
        )
        self.stage1_prompt = PromptTemplate.objects.create(
            name="Stage one",
            version=1,
            instruction_text="test",
            schema_json={},
            stage=PromptTemplate.STAGE_ONE,
        )
        self.stage2_prompt = PromptTemplate.objects.create(
            name="Stage two",
            version=1,
            instruction_text="test",
            schema_json={},
            stage=PromptTemplate.STAGE_TWO,
        )
        self.own_stage1 = self._bundle(
            self.teacher, self.own_exam, AnalysisBundle.STAGE_ONE, self.stage1_prompt
        )
        self.other_stage1 = self._bundle(
            self.other_teacher,
            self.other_exam,
            AnalysisBundle.STAGE_ONE,
            self.stage1_prompt,
        )
        self.other_stage2 = self._bundle(
            self.other_teacher,
            self.other_exam,
            AnalysisBundle.STAGE_TWO,
            self.stage2_prompt,
        )
        self.client.force_login(self.teacher)

    @staticmethod
    def _bundle(teacher, exam, stage, prompt):
        return AnalysisBundle.objects.create(
            teacher=teacher,
            exam=exam,
            prompt_template=prompt,
            stage=stage,
            status=AnalysisBundle.STATUS_SUCCESS,
        )

    def test_stage2_run_only_exposes_own_exams_and_stage1_bundles(self):
        response = self.client.get(
            reverse("analysis:stage2_run"), {"exam": self.own_exam.pk}
        )

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["form"].fields["exam"].queryset,
            [self.own_exam],
        )
        self.assertQuerySetEqual(
            response.context["stage1_bundles"],
            [self.own_stage1],
        )

    def test_other_teachers_stage2_results_and_detail_return_404(self):
        results_response = self.client.get(
            reverse(
                "analysis:stage2_result",
                kwargs={"exam_id": self.other_exam.pk},
            )
        )
        detail_response = self.client.get(
            reverse(
                "analysis:stage2_student_detail",
                kwargs={"pk": self.other_stage2.pk},
            )
        )

        self.assertEqual(results_response.status_code, 404)
        self.assertEqual(detail_response.status_code, 404)

    def test_forged_stage1_bundle_id_is_rejected(self):
        response = self.client.post(
            reverse("analysis:stage2_run"),
            {
                "exam": self.own_exam.pk,
                "stage1_bundle_id": self.other_stage1.pk,
                "stage2_prompt": self.stage2_prompt.pk,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            AnalysisBundle.objects.filter(
                teacher=self.teacher,
                stage=AnalysisBundle.STAGE_TWO,
            ).exists()
        )
