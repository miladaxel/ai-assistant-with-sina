import json
from symtable import Class
import time
from django.views import View
from django.shortcuts import render
from .exam_data import EXAM_DATA, students_data, student_exercises
from django.views.generic import TemplateView
from openai import OpenAI
from django.conf import settings




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


# class ChatTestView(View):
#     def get(self, request):
#         fake_response = {
#             "id": "chatcmpl-abc123",
#             "object": "chat.completion",
#             "created": 1732879200,
#             "model": "gpt-5.1-mini",
#             "choices": [
#                 {
#                     "index": 0,
#                     "message": {
#                         "role": "assistant",
#                         "content": "سلام 👋 من یک پاسخ تستی از سمت ChatGPT هستم تا بتونی فرمت API رو توی جنگو نمایش بدی."
#                     },
#                     "finish_reason": "stop",
#                 }
#             ],
#             "usage": {
#                 "prompt_tokens": 12,
#                 "completion_tokens": 24,
#                 "total_tokens": 36,
#             },
#         }
#         return render(request, "questions/chat_test.html", {"response": fake_response})



class ExamQuestionListView(TemplateView):
    # template_name = "questions/exam_question_list.html"
    #
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #
    #     context['exam'] = EXAM_DATA
    #     context['questions'] = EXAM_DATA.get(['questions', []])
    #     return context
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