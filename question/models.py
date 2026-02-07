from django.db import models
from django.conf import settings
from Profile.models import Student, TeacherUser
from django.core.exceptions import ValidationError

class PromptTemplate(models.Model):
    STAGE_ONE = 'stage1'
    STAGE_TWO = 'stage2'
    STAGE_THREE = 'stage3'

    STAGE_CHOICES = [
        (STAGE_ONE, 'Stage 1'),
        (STAGE_TWO, 'Stage 2'),
        (STAGE_THREE, 'Stage 3'),
    ]

    name = models.CharField(max_length=120)
    version = models.PositiveIntegerField(default=1)
    instruction_text = models.TextField()
    schema_json = models.JSONField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    stage = models.CharField(max_length=30, choices=STAGE_CHOICES, default=STAGE_ONE, blank=True, null=True)

    class Meta:
        unique_together = ('name', 'version')

    def __str__(self):
        return f"{self.name} (v{self.version})"


class AnalysisBundle(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_SUCCESS = 'success'
    STATUS_FAILURE = 'failure'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SUCCESS, 'Success'),
        (STATUS_FAILURE, 'Failure'),
    ]

    STAGE_ONE = 'stage1'
    STAGE_TWO = 'stage2'
    STAGE_THREE = 'stage3'

    STAGE_CHOICES = [
        (STAGE_ONE, 'Stage 1'),
        (STAGE_TWO, 'Stage 2'),
        (STAGE_THREE, 'Stage 3'),
    ]

    title = models.CharField(max_length=120, blank=True, default='')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='analysis_bundles', blank=True, null=True)
    prompt_template = models.ForeignKey(PromptTemplate, on_delete=models.PROTECT, related_name="bundles")
    lesson_pdf = models.FileField(upload_to='lessons_pdfs/', blank=True, null=True)
    example_pdf = models.FileField(upload_to='example_pdfs/', blank=True, null=True)
    input_json = models.JSONField(blank=True, null=True)
    stage = models.CharField(max_length=120, blank=True, choices=STAGE_CHOICES, default=STAGE_ONE)
    exam = models.ForeignKey('Exam', on_delete=models.SET_NULL, related_name='analysis_bundles', blank=True, null=True)

    openai_lesson_file_id = models.CharField(max_length=120, blank=True, default='')
    openai_example_file_id = models.CharField(max_length=120, blank=True, default='')
    model_name = models.CharField(max_length=120, blank=True, default='gpt-4o-mini')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_FAILURE)
    error_message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bundle {self.id} - {self.status}"


class AnalysisResult(models.Model):
    STAGE_ONE = 'stage1'
    STAGE_TWO = 'stage2'
    STAGE_THREE = 'stage3'

    STAGE_CHOICES = [
        (STAGE_ONE, 'Stage 1'),
        (STAGE_TWO, 'Stage 2'),
        (STAGE_THREE, 'Stage 3'),
    ]


    bundle = models.OneToOneField(AnalysisBundle, on_delete=models.CASCADE, related_name='result')
    result_json = models.JSONField()
    raw_output_text = models.TextField(blank=True, default='')
    openai_response_id = models.CharField(max_length=120, blank=True, default='')
    usage_json = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    stage = models.CharField(max_length=30, choices=STAGE_CHOICES, default=STAGE_ONE, blank=True, null=True)

    def __str__(self):
        return f"Bundle {self.bundle.id} - {self.bundle.status}"

class Exam(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exams', null=True, blank=True)
    name = models.CharField(max_length=120, blank=True, default='')
    total_question = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    students = models.ManyToManyField(Student,through="ExamParticipation" ,related_name='taken_exams', blank=True)

    def __str__(self):
        return self.name


class ExamParticipation(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='participations')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_participations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('exam', 'student')

    def __str__(self):
        return f"{self.student.full_name} - {self.exam.name}"

class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    number = models.PositiveIntegerField(default=0)
    has_subquestion = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    subquestion_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"exam {self.exam.name} - question {self.number} - {self.subquestion_count}"


class SubQuestion(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='subquestions')
    number = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"exam {self.question.exam.name} - subquestion {self.number} of question {self.question.number}"


class StudentQuestionResult(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='student_answers')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', null=True, blank=True)
    subquestion = models.ForeignKey(SubQuestion, on_delete=models.CASCADE, related_name='answers', null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    graded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('exam', 'student', 'question', 'subquestion')

    def clean(self):
        if self.question and self.subquestion:
            raise ValidationError("Only one of question or subquestion allowed")
        if not self.question and not self.subquestion:
            raise ValidationError("Question or subquestion is required")

    def __str__(self):
        target = self.subquestion or self.question
        return f"{self.student.full_name} - {target} - {'✔' if self.is_correct else '✘'}"


class ExamSnapShot(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='snapshots')
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Snapshot for Exam {self.exam.name} at {self.created_at}"