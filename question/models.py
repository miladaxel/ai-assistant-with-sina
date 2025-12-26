from django.db import models
from django.conf import settings

class PromptTemplate(models.Model):
    name = models.CharField(max_length=120)
    version = models.PositiveIntegerField(default=1)
    instruction_text = models.TextField()
    schema_json = models.JSONField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

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

    title = models.CharField(max_length=120, blank=True, default='')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='analysis_bundles', blank=True, null=True)
    prompt_template = models.ForeignKey(PromptTemplate, on_delete=models.PROTECT, related_name="bundles")
    lesson_pdf = models.FileField(upload_to='lessons_pdfs/', blank=True, null=True)
    example_pdf = models.FileField(upload_to='example_pdfs/', blank=True, null=True)

    openai_lesson_file_id = models.CharField(max_length=120, blank=True, default='')
    openai_example_file_id = models.CharField(max_length=120, blank=True, default='')
    model_name = models.CharField(max_length=120, blank=True, default='gpt-4o-mini')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    error_message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bundle {self.id} - {self.status}"


class AnalysisResult(models.Model):
    bundle = models.OneToOneField(AnalysisBundle, on_delete=models.CASCADE, related_name='result')
    result_json = models.JSONField()
    raw_output_text = models.TextField(blank=True, default='')
    openai_response_id = models.CharField(max_length=120, blank=True, default='')
    usage_json = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bundle {self.bundle.id} - {self.bundle.status}"

