from django.test import TestCase
from django.urls import reverse

from Profile.models import Users
from question.models import AnalysisBundle, Exam, PromptTemplate


class Stage3TeacherIsolationTests(TestCase):
    def setUp(self):
        self.teacher = Users.objects.create_user(
            username="stage3_teacher_one", password="test-pass", role="teacher"
        )
        self.other_teacher = Users.objects.create_user(
            username="stage3_teacher_two", password="test-pass", role="teacher"
        )
        self.own_exam = Exam.objects.create(
            teacher=self.teacher, name="Own exam", total_question=1
        )
        self.other_exam = Exam.objects.create(
            teacher=self.other_teacher, name="Other exam", total_question=1
        )
        self.stage2_prompt = PromptTemplate.objects.create(
            name="Stage two",
            version=1,
            instruction_text="test",
            schema_json={},
            stage=PromptTemplate.STAGE_TWO,
        )
        self.stage3_prompt = PromptTemplate.objects.create(
            name="Stage three",
            version=1,
            instruction_text="test",
            schema_json={},
            stage=PromptTemplate.STAGE_THREE,
        )
        self.own_stage2 = self._bundle(
            self.teacher, self.own_exam, AnalysisBundle.STAGE_TWO
        )
        self.other_stage2 = self._bundle(
            self.other_teacher, self.other_exam, AnalysisBundle.STAGE_TWO
        )
        self.other_stage3 = self._bundle(
            self.other_teacher, self.other_exam, AnalysisBundle.STAGE_THREE
        )
        self.client.force_login(self.teacher)

    def _bundle(self, teacher, exam, stage):
        prompt = self.stage2_prompt if stage == AnalysisBundle.STAGE_TWO else self.stage3_prompt
        return AnalysisBundle.objects.create(
            teacher=teacher,
            exam=exam,
            prompt_template=prompt,
            stage=stage,
            status=AnalysisBundle.STATUS_SUCCESS,
        )

    def test_stage3_form_only_shows_logged_in_teachers_stage2_bundles(self):
        response = self.client.get(reverse("exercise_generate:stage3_run"))

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["form"].fields["stage2_bundle"].queryset,
            [self.own_stage2],
        )

    def test_other_teachers_stage3_detail_returns_404(self):
        response = self.client.get(
            reverse(
                "exercise_generate:stage3_detail",
                kwargs={"pk": self.other_stage3.pk},
            )
        )

        self.assertEqual(response.status_code, 404)
