import json
from collections import defaultdict
from symtable import Class
import time

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Prefetch

from .exam_data import EXAM_DATA, students_data, student_exercises
from django.views.generic import TemplateView, CreateView, DetailView, ListView, FormView
from django.conf import settings
from django.db import transaction
from .forms import AnalysisBundleCreateForm, ExamForm, QuestionHasSubFormSet, QuestionSubCountForm, QuestionSubCountFormSet, QuestionHasSubForm, ExamStudentForm, StudentQuestionResultForm, StudentQuestionResultFormSet
from .models import AnalysisBundle, AnalysisResult, PromptTemplate, Exam, Question, SubQuestion, ExamParticipation, StudentQuestionResult, ExamSnapShot
import inspect
import importlib
from .mixins import TeacherRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from .models import ChatRequest
from .tasks import process_analysis_bundle, process_chat_request
from .services.background import enqueue_after_commit
from Profile.models import TeacherUser, Student
from ai_asistant_with_sina.query_cache import (
    CachedBundleDetailMixin, CachedListMixin, cached_value,
)


def cached_exam_questions(exam, teacher_id, *, allow_in_atomic=False):
    return cached_value(
        'exam-questions', (teacher_id, exam.pk), ('questions', 'exams'), 1800,
        lambda: list(exam.questions.order_by('number', 'pk').prefetch_related(
            Prefetch('subquestions', queryset=SubQuestion.objects.order_by('number', 'pk'))
        )),
        allow_in_atomic=allow_in_atomic,
    )




class ChatTestView(LoginRequiredMixin, View):
    def get(self, request):
        chat = None
        request_id = request.GET.get("request")
        if request_id:
            if not request_id.isdecimal():
                return JsonResponse({"error": "Invalid request ID"}, status=400)
            chat = get_object_or_404(ChatRequest, pk=request_id, user=request.user)
        return render(request, "questions/chat_test_1.html", {"chat": chat})

    def post(self, request):
        prompt = (request.POST.get("q") or "").strip()
        if not prompt:
            return render(request, "questions/chat_test_1.html", {"error": "لطفاً متن سوال را وارد کنید."})
        with transaction.atomic():
            chat = ChatRequest.objects.create(user=request.user, prompt=prompt)
            enqueue_after_commit(process_chat_request, chat)
        return redirect(f"{reverse('chat')}?request={chat.pk}")


class ChatRequestStatusView(LoginRequiredMixin, View):
    def get(self, request, pk):
        chat = get_object_or_404(ChatRequest, pk=pk, user=request.user)
        response = JsonResponse({"statuses": {str(chat.pk): chat.status}})
        response["Cache-Control"] = "no-store"
        return response


class BundleStatusView(LoginRequiredMixin, TeacherRequiredMixin, View):
    def get(self, request):
        ids = request.GET.get("ids", "").split(",")
        if len(ids) > 20 or any(not value.isdecimal() for value in ids):
            return JsonResponse({"error": "Invalid bundle IDs"}, status=400)
        statuses = AnalysisBundle.objects.filter(
            pk__in=ids, teacher=request.user, exam__teacher=request.user,
        ).values_list("pk", "status")
        response = JsonResponse({"statuses": {str(pk): status for pk, status in statuses}})
        response["Cache-Control"] = "no-store"
        return response


class ExamQuestionListView(LoginRequiredMixin, TemplateView):
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


class AnalyzeStudentsView(LoginRequiredMixin, TemplateView):
    template_name = "questions/analyze_students.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        for student in students_data["students"]:


            student["issues"] = [
                issue for issue in student.get("issues", [])
                if issue.get("student_answer") != issue.get("correct_answer")
            ]

        context["students_analysis"] = students_data["students"]
        return context



class AssignExercisesView(LoginRequiredMixin, TemplateView):
    template_name = "questions/assign_exercise.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # برای هر دانش‌آموز تمرین‌ها رو از فایل پایتون جداگانه می‌گیریم
        for student in student_exercises["students"]:
            # بدون تغییر، داده‌ها رو به شکل ساده در context قرار می‌دهیم
            student["exercises"] = student.get("exercises", [])

        context["students_exercises"] = student_exercises["students"]
        return context


class AnalysisBundleCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = AnalysisBundle
    form_class = AnalysisBundleCreateForm
    template_name = "questions/bundle_create.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        with transaction.atomic():
            bundle = form.save(commit=False)
            bundle.teacher = self.request.user
            bundle.status = AnalysisBundle.STATUS_PENDING
            bundle.stage = AnalysisBundle.STAGE_ONE
            bundle.save()
            enqueue_after_commit(process_analysis_bundle, bundle)
        return redirect("bundle_detail", pk=bundle.pk)


class AnalysisBundleDetailView(LoginRequiredMixin, TeacherRequiredMixin, CachedBundleDetailMixin, DetailView):
    model = AnalysisBundle
    template_name = "questions/bundle_detail.html"
    context_object_name = "bundle"

    def get_queryset(self):
        return AnalysisBundle.objects.filter(
            teacher=self.request.user,
            exam__teacher=self.request.user,
        ).select_related("prompt_template", "result")


class MyAnalysisBundlesView(LoginRequiredMixin, TeacherRequiredMixin, CachedListMixin, ListView):
    model = AnalysisBundle
    template_name = "questions/my_bundles.html"
    context_object_name = 'bundles'
    paginate_by = 20

    def get_queryset(self):
        return (
            AnalysisBundle.objects.filter(
                teacher=self.request.user,
                exam__teacher=self.request.user,
                stage=AnalysisBundle.STAGE_ONE,
            ).select_related("exam").defer("input_json").order_by('-created_at', '-pk')
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
        if not request.user.is_authenticated:
            return self.handle_no_permission()
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

        changed_questions = formset.save(commit=False)
        if changed_questions:
            Question.objects.bulk_update(changed_questions, ["has_subquestion"])
        return redirect('exam_sub_question_setup', exam_id=self.exam.pk)

class ExamSubQuestionsSetupView(LoginRequiredMixin, TemplateView):
    template_name = "questions/exam_subquestions_setup.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
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

        questions = formset.save(commit=False)
        existing_by_question = defaultdict(list)
        for sub in SubQuestion.objects.filter(question__in=questions).order_by("number", "pk"):
            existing_by_question[sub.question_id].append(sub)

        new_subquestions = []
        delete_ids = []
        for q in questions:
            desired = q.subquestion_count or 0
            existing = existing_by_question[q.pk]
            existing_count = len(existing)

            if desired > existing_count:
                start = existing_count + 1
                new_subquestions.extend([
                    SubQuestion(question=q, number=i) for i in range(start, desired + 1)
                ])
            elif desired < existing_count:
                delete_ids.extend(sub.pk for sub in existing[desired:])

        if questions:
            Question.objects.bulk_update(questions, ["subquestion_count"])
        if delete_ids:
            SubQuestion.objects.filter(pk__in=delete_ids).delete()
        if new_subquestions:
            SubQuestion.objects.bulk_create(new_subquestions)

        return redirect('exam_summary', exam_id=self.exam.pk)

class ExamSummaryView(LoginRequiredMixin, TeacherRequiredMixin, DetailView):
    model = Exam
    template_name = "questions/exam_summary.html"
    context_object_name = "exam"
    pk_url_kwarg = "exam_id"

    def test_func(self):
        return self.request.user.role == "teacher"

    def get_queryset(self):
        return Exam.objects.filter(teacher=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        questions = cached_exam_questions(self.object, self.request.user.pk)
        participants = (
            self.object.participations
            .select_related("student")
            .only(
                "exam_id",
                "student_id",
                "student__full_name",
                "student__national_code",
            )
            .order_by("student__full_name")
        )

        ctx["questions"] = questions
        ctx["exam_id"] = self.object.pk
        ctx["total_questions"] = len(questions)
        ctx["total_subquestions"] = sum(
            question.subquestion_count for question in questions
        )
        ctx["participants"] = cached_value(
            'exam-participants', (self.request.user.pk, self.object.pk),
            ('participants', 'people', 'exams'), 300, lambda: list(participants),
        )
        return ctx


class ExamListView(LoginRequiredMixin, TeacherRequiredMixin, CachedListMixin, ListView):
    cache_groups = ('exams', 'participants')
    cache_timeout = 120
    model = Exam
    template_name = "questions/exam_list.html"
    context_object_name = "exams"
    paginate_by = 12

    def get_queryset(self):
        return (
            Exam.objects
            .filter(teacher=self.request.user)
            .annotate(participants_count=Count("students", distinct=True))
            .order_by("-created_at")
        )


class ExamSelectStudentsView(LoginRequiredMixin, TemplateView):
    template_name = 'questions/exam_select_students.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
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

        existing_ids = set(ExamParticipation.objects.filter(exam=self.exam, student__in=selected_students).values_list('student_id', flat=True))

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
        return cached_value(
            'exam-participation-list', (self.request.user.pk, self.exam.pk),
            ('participants', 'people', 'exams'), 300,
            lambda: list(ExamParticipation.objects.filter(exam=self.exam).select_related('student')),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exam'] = self.exam
        return context

class ExamCorrectionView(LoginRequiredMixin, View):
    template_name = 'questions/exam_correction.html'

    @transaction.atomic
    def get(self, request, exam_id, student_id):
        exam = get_object_or_404(Exam.objects.select_for_update(), id=exam_id, teacher=request.user)
        student = get_object_or_404(Student, id=student_id)
        get_object_or_404(ExamParticipation, exam=exam, student=student)

        questions = cached_exam_questions(exam, request.user.pk, allow_in_atomic=True)
        result_qs = StudentQuestionResult.objects.filter(exam=exam, student=student)
        existing = {
            (r.question_id, r.subquestion_id): r
            for r in result_qs.select_related("question", "subquestion__question").order_by("pk")
        }
        targets = []
        missing = []
        for q in questions:
            if q.has_subquestion:
                keys = [(None, sub.pk) for sub in q.subquestions.all()]
            else:
                keys = [(q.pk, None)]
            for key in keys:
                targets.append(key)
                if key not in existing:
                    missing.append(StudentQuestionResult(
                        exam=exam, student=student,
                        question_id=key[0], subquestion_id=key[1],
                    ))

        if missing:
            StudentQuestionResult.objects.bulk_create(missing)
            existing = {
                (r.question_id, r.subquestion_id): r
                for r in result_qs.select_related("question", "subquestion__question").order_by("pk")
            }
        results = [existing[key] for key in targets]

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

        selected_ids = [
            int(key[7:]) for key in request.POST
            if key.startswith("result_") and key[7:].isascii() and key[7:].isdigit()
            and len(key[7:]) <= 19
        ]
        selected_ids = [pk for pk in selected_ids if 0 < pk <= 9223372036854775807]
        all_results = StudentQuestionResult.objects.filter(exam=exam, student=student)
        all_results.filter(pk__in=selected_ids).update(is_correct=True)
        all_results.exclude(pk__in=selected_ids).update(is_correct=False)

        return redirect('exam_summary', exam_id=exam.id)



class ExamResultsReportView(LoginRequiredMixin, TeacherRequiredMixin, TemplateView):
    template_name = "questions/exam_result_report.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        self.exam = get_object_or_404(
            Exam,
            id=kwargs["exam_id"],
            teacher=request.user
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(cached_value(
            'exam-report', (self.request.user.pk, self.exam.pk),
            ('grades', 'questions', 'participants', 'people', 'exams'), 300,
            self._load_report_data,
        ))
        # Keep this optional context lazy; the current report renders groups only.
        ctx['participants'] = (
            ExamParticipation.objects.filter(exam=self.exam)
            .select_related('student').order_by('student__full_name')
        )
        return ctx

    def _load_report_data(self):

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

        student_results = {}
        grouped_results = {}
        for r in results:
            student_results.setdefault(r.student, []).append(r)
            question = r.subquestion.question if r.subquestion_id else r.question
            if question is None:
                continue
            student_groups = grouped_results.setdefault(r.student, {})
            group = student_groups.setdefault(question.pk, {
                "number": question.number,
                "is_correct": True,
                "subresults": [],
            })
            group["is_correct"] = group["is_correct"] and r.is_correct
            if r.subquestion_id:
                group["subresults"].append(r)

        student_question_groups = {}
        for student, groups in grouped_results.items():
            ordered_groups = sorted(groups.values(), key=lambda group: group["number"])
            for group in ordered_groups:
                group["subresults"].sort(key=lambda r: (r.subquestion.number, r.pk))
            student_question_groups[student] = ordered_groups

        return {
            'exam': self.exam,
            'student_results': student_results,
            'student_question_groups': student_question_groups,
        }


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

        participations = ExamParticipation.objects.filter(exam=exam).select_related('student')
        answers_by_student = defaultdict(list)
        answers = (
            StudentQuestionResult.objects.filter(
                exam=exam,
                student_id__in=participations.values("student_id"),
            )
            .select_related('question', 'subquestion__question')
            .order_by('question__number', 'subquestion__question__number', 'subquestion__number', 'id')
        )
        for answer in answers:
            answers_by_student[answer.student_id].append(answer)
        for p in participations:
            student = p.student
            student_data = {"student_id": student.id, "full_name": student.full_name, "results": []}
            for ans in answers_by_student[student.id]:
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

        return redirect('teacher panel')


class ExamSnapShotListView(LoginRequiredMixin, TeacherRequiredMixin, CachedListMixin, ListView):
    cache_groups = ('snapshots', 'exams')
    cache_timeout = 300
    model = ExamSnapShot
    template_name = 'questions/snapshot_list.html'
    context_object_name = 'snapshots'
    paginate_by = 10

    def get_queryset(self):
        self.exam = get_object_or_404(Exam, id=self.kwargs['exam_id'], teacher=self.request.user)
        return self.exam.snapshots.all().order_by('-created_at', '-pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exam'] = self.exam
        return context
