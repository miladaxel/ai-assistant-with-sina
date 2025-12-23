import json
from symtable import Class
import time
from django.views import View
from django.shortcuts import render, redirect
from .exam_data import EXAM_DATA, students_data, student_exercises
from django.views.generic import TemplateView, CreateView, DetailView
from openai import OpenAI
from django.conf import settings
from django.db import transaction
from .forms import AnalysisBundleCreateForm
from .models import AnalysisBundle, AnalysisResult, PromptTemplate
from question.services.openai_client import OpenAIAnalyzer
import inspect
import importlib





class ChatTestView(View):
    def get(self, request):
        q = (request.GET.get("q") or "").strip()

        if not q:
            return render(request, "questions/chat_test_1.html")

        try:
            client = OpenAI(
                api_key=settings.OPENAI_API_KEY
            )

            resp = client.responses.create(
                model="gpt-5.2",
                input=q,
            )

            # برای اطمینان
            answer_text = resp.output_text
            if not answer_text:
                answer_text = str(resp)

            response = {
                "choices": [
                    {
                        "message": {
                            "content": answer_text
                        }
                    }
                ]
            }

            return render(
                request,
                "questions/chat_test_1.html",
                {"response": response}
            )

        except Exception as e:
            return render(
                request,
                "questions/chat_test_1.html",
                {"error": str(e)}
            )



class ExamQuestionListView(TemplateView):
        template_name = "questions/exam_question_list.html"

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)

            normalized_questions = []
            for raw_q in EXAM_DATA.get("questions", []):
                q = raw_q.copy()

                q_type = q.get("question_type")

                # فلگ‌ها برای راحتی در تمپلیت
                q["is_conversation"] = (q_type == "conversation_completion")
                q["is_spelling"] = (q_type == "spelling")
                q["is_matching"] = bool(q.get("pairs"))

                # آماده‌سازی correct_answer
                ca = q.get("correct_answer")
                if isinstance(ca, dict):
                    # مثلاً برای مکالمه (first_blank / second_blank)
                    q["correct_answer_items"] = list(ca.items())
                else:
                    q["correct_answer_items"] = None

                # آماده‌سازی pairs (برای matching)
                pairs = q.get("pairs")
                if isinstance(pairs, dict):
                    q["pairs_items"] = list(pairs.items())
                else:
                    q["pairs_items"] = None

                normalized_questions.append(q)

            context["exam"] = EXAM_DATA
            context["questions"] = normalized_questions
            return context


class AnalyzeStudentsView(TemplateView):
    template_name = "questions/analyze_students.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        for student in students_data["students"]:


            student["issues"] = [
                issue for issue in student.get("issues", [])
                if issue.get("student_answer") != issue.get("correct_answer")
            ]

        # چاپ context برای بررسی
        print("Context Data:", context)  # اینجا چاپ می‌کنیم که مطمئن بشیم داده‌ها در context هست

        context["students_analysis"] = students_data["students"]
        return context



class AssignExercisesView(TemplateView):
    template_name = "questions/assign_exercise.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # برای هر دانش‌آموز تمرین‌ها رو از فایل پایتون جداگانه می‌گیریم
        for student in student_exercises["students"]:
            # بدون تغییر، داده‌ها رو به شکل ساده در context قرار می‌دهیم
            student["exercises"] = student.get("exercises", [])

        # چاپ داده‌ها برای بررسی
        print("Context Data:", context)  # اینجا چاپ می‌کنیم که مطمئن بشیم داده‌ها در context هستند

        context["students_exercises"] = student_exercises["students"]
        return context


class AnalysisBundleCreateView(CreateView):
    model = AnalysisBundle
    form_class = AnalysisBundleCreateForm
    template_name = "questions/bundle_create.html"

    def form_valid(self, form):
        prompt = PromptTemplate.objects.filter(is_active=True).order_by("-version").first()
        if not prompt:
            form.add_error(None, "No active PromptTemplate found. Create one in admin.")
            return self.form_invalid(form)

        with transaction.atomic():
            bundle: AnalysisBundle = form.save(commit=False)
            bundle.prompt_template = prompt
            bundle.status = AnalysisBundle.STATUS_PENDING
            bundle.save()

        analyzer = OpenAIAnalyzer()
        try:
            textbook_file_id = analyzer.upload_pdf(bundle.lesson_pdf.path)
            exam_file_id = analyzer.upload_pdf(bundle.example_pdf.path)

            bundle.openai_lesson_file_id = textbook_file_id
            bundle.openai_exam_file_id = exam_file_id
            bundle.save(update_fields=["openai_lesson_file_id", "openai_example_file_id"])

            out = analyzer.analyze(
                model=bundle.model_name,
                instructions=prompt.instruction_text,
                json_schema=prompt.schema_json,
                textbook_file_id=textbook_file_id,
                exam_file_id=exam_file_id,
            )

            AnalysisResult.objects.create(
                bundle=bundle,
                result_json=out.parsed_json,
                raw_output_text=out.raw_output_text,
                openai_response_id=out.response_id,
                usage_json=out.usage,
            )

            bundle.status = AnalysisBundle.STATUS_SUCCESS
            bundle.save(update_fields=["status"])

        except Exception as e:
            bundle.status = AnalysisBundle.STATUS_FAILURE
            bundle.error_message = str(e)
            bundle.save(update_fields=["status", "error_message"])

        return redirect("bundle_detail", pk=bundle.pk)


class AnalysisBundleDetailView(DetailView):
    model = AnalysisBundle
    template_name = "questions/bundle_detail.html"
    context_object_name = "bundle"