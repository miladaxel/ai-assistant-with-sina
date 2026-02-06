import json
from symtable import Class
import time

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404

from .exam_data import EXAM_DATA, students_data, student_exercises
from django.views.generic import TemplateView, CreateView, DetailView, ListView, FormView
from openai import OpenAI
from django.conf import settings
from django.db import transaction
from .forms import AnalysisBundleCreateForm, ExamForm, QuestionHasSubFormSet, QuestionSubCountForm, QuestionSubCountFormSet, QuestionHasSubForm, ExamStudentForm, StudentQuestionResultForm, StudentQuestionResultFormSet
from .models import AnalysisBundle, AnalysisResult, PromptTemplate, Exam, Question, SubQuestion, ExamParticipation, StudentQuestionResult, ExamSnapShot
from question.services.openai_client import OpenAIAnalyzer
import inspect
import importlib
from .mixins import TeacherRequiredMixin
from django.urls import reverse_lazy
from Profile.models import TeacherUser, Student
from django.db.models import Sum




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


class AnalysisBundleCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = AnalysisBundle
    form_class = AnalysisBundleCreateForm
    template_name = "questions/bundle_create.html"

    def form_valid(self, form):
        analyzer = OpenAIAnalyzer()

        with transaction.atomic():
            bundle: AnalysisBundle = form.save(commit=False)
            selected_prompt = form.cleaned_data["prompt_template"]
            bundle.prompt_template = selected_prompt
            bundle.teacher = self.request.user
            bundle.status = AnalysisBundle.STATUS_PENDING
            bundle.exam = form.cleaned_data["exam"]
            bundle.stage = 'stage1_exam_map'
            bundle.save()

        try:
            textbook_file_id = analyzer.upload_pdf(bundle.lesson_pdf.path)
            exam_file_id = analyzer.upload_pdf(bundle.example_pdf.path)

            bundle.openai_lesson_file_id = textbook_file_id
            bundle.openai_example_file_id = exam_file_id
            bundle.save(update_fields=["openai_lesson_file_id", "openai_example_file_id"])

            out = analyzer.analyze(
                model=bundle.model_name,
                instructions=selected_prompt.instruction_text,
                json_schema=selected_prompt.schema_json,
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


class AnalysisBundleDetailView(LoginRequiredMixin, TeacherRequiredMixin ,DetailView):
    model = AnalysisBundle
    template_name = "questions/bundle_detail.html"
    context_object_name = "bundle"


class MyAnalysisBundlesView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    model = AnalysisBundle
    template_name = "questions/my_bundles.html"
    context_object_name = 'bundles'
    paginate_by = 20

    def get_queryset(self):
        return (
            AnalysisBundle.objects.filter(teacher=self.request.user).order_by('-created_at')
        )


class ExamCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Exam
    form_class = ExamForm
    template_name = 'questions/create_exam.html'

    @transaction.atomic
    def form_valid(self, form):
        exam: Exam = form.save(commit=False)
        exam.teacher = self.request.user
        exam.save()

        total_question = exam.total_question
        Question.objects.bulk_create(
            [Question(exam=exam, number=i) for i in range(1, total_question + 1)],
            ignore_conflicts=True,
        )
        return redirect('exam_question_setup', exam_id=exam.pk)



class ExamQuestionsSetupView(LoginRequiredMixin, TemplateView):
    template_name = "questions/exam_questions_setup.html"

    def dispatch(self, request, *args, **kwargs):
        self.exam = get_object_or_404(Exam, id=kwargs["exam_id"], teacher=request.user,)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return (Question.objects.filter(exam=self.exam).order_by('number'))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        formset = kwargs.get("formset") or QuestionHasSubFormSet(queryset=self.get_queryset())
        ctx["exam"] = self.exam
        ctx["formset"] = formset
        return ctx

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        formset = QuestionHasSubFormSet(request.POST, queryset=self.get_queryset())
        if not formset.is_valid():
            return self.render_to_response(self.get_context_data(formset=formset))

        formset.save()
        return redirect('exam_sub_question_setup', exam_id=self.exam.pk)

class ExamSubQuestionsSetupView(LoginRequiredMixin, TemplateView):
    template_name = "questions/exam_subquestions_setup.html"

    def dispatch(self, request, *args, **kwargs):
        self.exam = get_object_or_404(Exam, id=kwargs["exam_id"], teacher=request.user,)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return (Question.objects.filter(exam=self.exam, has_subquestion=True).exclude(number=0).order_by('number'))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        formset = kwargs.get("formset") or QuestionSubCountFormSet(queryset=self.get_queryset())
        ctx["exam"] = self.exam
        ctx["formset"] = formset
        return ctx

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        formset = QuestionSubCountFormSet(request.POST, queryset=self.get_queryset())
        if not formset.is_valid():
            return self.render_to_response(self.get_context_data(formset=formset))

        question = formset.save(commit=False)
        for q in question :
            desired = q.subquestion_count or 0
            q.save(update_fields=["subquestion_count"])
            existing_qs = q.subquestions.order_by('number')
            existing_count = existing_qs.count()

            if desired > existing_count:
                start = existing_count + 1
                SubQuestion.objects.bulk_create([
                    SubQuestion(question=q, number=i) for i in range(start, desired + 1)
                ])
            elif desired < existing_count:
                q.subquestions.order_by('-number')[:existing_count - desired].delete()

        return redirect('exam_summary', exam_id=self.exam.pk)

class ExamSummaryView(LoginRequiredMixin, TeacherRequiredMixin, TemplateView):
    template_name = "questions/exam_summary.html"

    def dispatch(self, request, *args, **kwargs):
        self.exam = get_object_or_404(Exam, id=kwargs["exam_id"], teacher=request.user,)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        questions = (Question.objects.filter(exam=self.exam).order_by('number'))

        total_sub = questions.aggregate(total=Sum('subquestion_count'))
        participants = (ExamParticipation.objects.filter(exam=self.exam).select_related('student').order_by('student__full_name'))

        ctx["exam"] = self.exam
        ctx["questions"] = questions
        ctx["total_questions"] = questions.count()
        ctx["total_subquestions"] = total_sub
        ctx["participants"] = participants
        return ctx


class ExamSelectStudentsView(LoginRequiredMixin, TemplateView):
    template_name = 'questions/exam_select_students.html'

    def dispatch(self, request, *args, **kwargs):
        self.exam = get_object_or_404(Exam, id=kwargs["exam_id"], teacher=request.user,)
        self.teacher_profile = get_object_or_404(TeacherUser, user=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_students_qs(self):
        return self.teacher_profile.students.all().order_by('full_name')

    def get_initial_selected(self):
        return ExamParticipation.objects.filter(exam=self.exam).values_list('student_id', flat=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        form = kwargs.get('form') or ExamStudentForm(
            students_qs=self.get_students_qs(),
            initial={'students': self.get_initial_selected()}
        )
        ctx['exam'] = self.exam
        ctx['form'] = form
        return ctx

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = ExamStudentForm(request.POST, students_qs=self.get_students_qs())
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(form=form))

        selected_students = form.cleaned_data['students']

        ExamParticipation.objects.filter(exam=self.exam).exclude(student__in=selected_students).delete()

        existing_ids = ExamParticipation.objects.filter(exam=self.exam, student__in=selected_students).values_list('student_id', flat=True)

        new_rows = [ExamParticipation(exam=self.exam, student=s) for s in selected_students if s.id not in existing_ids]
        if new_rows:
            ExamParticipation.objects.bulk_create(new_rows)

        return redirect('exam_summary', exam_id=self.exam.pk)


class StudentParticipationListView(LoginRequiredMixin,TeacherRequiredMixin ,ListView):
    model = ExamParticipation
    template_name = 'questions/exam_participation_list_students.html'
    context_object_name = 'students'

    def get_queryset(self):
        self.exam = get_object_or_404(Exam, id=self.kwargs['exam_id'], teacher=self.request.user,)
        return ExamParticipation.objects.filter(exam=self.exam)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exam'] = self.exam
        return context

class ExamCorrectionView(LoginRequiredMixin, View):
    template_name = 'questions/exam_correction.html'

    def get(self, request, exam_id, student_id):
        exam = get_object_or_404(Exam, id=exam_id, teacher=request.user)
        student = get_object_or_404(Student, id=student_id)
        get_object_or_404(ExamParticipation, exam=exam, student=student)

        # آماده‌سازی نتایج اولیه اگر وجود ندارند
        results = []
        for q in exam.questions.all():
            if q.has_subquestion:
                for sub in q.subquestions.all():
                    result, created = StudentQuestionResult.objects.get_or_create(
                        exam=exam, student=student, subquestion=sub
                    )
                    results.append(result)
            else:
                result, created = StudentQuestionResult.objects.get_or_create(
                    exam=exam, student=student, question=q
                )
                results.append(result)

        context = {
            'exam': exam,
            'student': student,
            'results': results,
        }
        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request, exam_id, student_id):
        exam = get_object_or_404(Exam, id=exam_id, teacher=request.user)
        student = get_object_or_404(Student, id=student_id)
        get_object_or_404(ExamParticipation, exam=exam, student=student)

        # ذخیره نتایج بر اساس checkbox
        all_results = StudentQuestionResult.objects.filter(exam=exam, student=student)
        for r in all_results:
            # اگر checkbox ارسال شده → True، در غیر اینصورت → False
            r.is_correct = f'result_{r.id}' in request.POST
            r.save()

        return redirect('exam_summary', exam_id=exam.id)



class ExamResultsReportView(LoginRequiredMixin, TeacherRequiredMixin, TemplateView):
    template_name = "questions/exam_result_report.html"

    def dispatch(self, request, *args, **kwargs):
        self.exam = get_object_or_404(
            Exam,
            id=kwargs["exam_id"],
            teacher=request.user
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        participations = (
            ExamParticipation.objects
            .filter(exam=self.exam)
            .select_related('student')
            .order_by('student__full_name')
        )

        results = (
            StudentQuestionResult.objects
            .filter(exam=self.exam)
            .select_related(
                'student',
                'question',
                'subquestion',
                'subquestion__question'
            )
            .order_by('student__full_name')
        )

        # گروه‌بندی نتایج بر اساس دانش‌آموز
        student_results = {}
        for r in results:
            student_results.setdefault(r.student, []).append(r)

        ctx["exam"] = self.exam
        ctx["student_results"] = student_results
        ctx["participants"] = participations

        return ctx


class ExamSnapShotCreateView(LoginRequiredMixin, TeacherRequiredMixin, View):
    template_name = "questions/exam_snapshot_create.html"
    def get(self, request, exam_id):
        exam = get_object_or_404(Exam, id=exam_id, teacher=request.user)

        return render(request, self.template_name, {'exam': exam})

    def post(self, request, exam_id):
        exam = get_object_or_404(Exam, id=exam_id, teacher=request.user)

        snap_shot = {
            "exam" : {
                "id": exam.id,
                "name": exam.name,
                "teacher_id": exam.teacher_id,
                "created_at": exam.created_at.isoformat()
            },
            "students": []
        }

        seen_students = set()
        participations = ExamParticipation.objects.filter(exam=exam).select_related('student')
        for p in participations:
            student = p.student
            if student.id in seen_students:
                continue
            seen_students.add(student.id)
            answers = StudentQuestionResult.objects.filter(exam=exam, student=student).select_related('question', 'subquestion', 'subquestion__question').order_by('question__number', 'subquestion__question__number', 'subquestion__number','id')
            student_data = {"student_id": student.id, "full_name": student.full_name, "results": []}
            for ans in answers:
                if ans.question:
                    student_data["results"].append({
                        "type": 'question',
                        "question_id": ans.question.id,
                        "question_number": ans.question.number,
                        "is_correct": ans.is_correct,
                    })
                else:
                    student_data["results"].append({
                        "type": 'subquestion',
                        "subquestion_id": ans.subquestion.id,
                        "question_number": ans.subquestion.question.number,
                        "subquestion_number": ans.subquestion.number,
                        "is_correct": ans.is_correct,
                    })
            snap_shot["students"].append(student_data)
        ExamSnapShot.objects.create(exam=exam, data=snap_shot)

        return redirect('exam_snapshot_list', exam_id=exam_id)


class ExamSnapShotListView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    model = ExamSnapShot
    template_name = 'questions/snapshot_list.html'
    context_object_name = 'snapshots'

    def get_queryset(self):
        self.exam = get_object_or_404(Exam, id=self.kwargs['exam_id'], teacher=self.request.user)
        return self.exam.snapshots.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exam'] = self.exam
        return context