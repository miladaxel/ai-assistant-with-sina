"""Background tasks discovered by the project's Celery application."""

from celery import shared_task
from django.db import transaction
from openai import OpenAI
from django.conf import settings

from analysis.services.stage2 import fill_stage2_prompt
from .models import AnalysisBundle, AnalysisResult, ChatRequest
from .services.openai_client import OpenAIAnalyzer

import json
import logging

logger = logging.getLogger(__name__)


@shared_task
def ping():
    """Verify that the broker, worker and result backend work end to end."""
    return 'pong'


def _upload(analyzer, bundle, field, file):
    file_id = getattr(bundle, field)
    if not file_id:
        file_id = analyzer.upload_pdf(file.path)
        setattr(bundle, field, file_id)
        bundle.save(update_fields=[field])
    return file_id


@shared_task(ignore_result=True)
def process_analysis_bundle(bundle_id):
    # Claim with one short SQL update. Duplicate deliveries must not call the API.
    claimed = AnalysisBundle.objects.filter(
        pk=bundle_id, status=AnalysisBundle.STATUS_PENDING,
    ).update(status=AnalysisBundle.STATUS_PROCESSING, error_message='')
    if not claimed:
        return

    try:
        bundle = AnalysisBundle.objects.select_related('prompt_template').get(pk=bundle_id)
        analyzer = OpenAIAnalyzer()
        inputs = bundle.input_json or {}
        if bundle.stage == AnalysisBundle.STAGE_ONE:
            lesson_id = _upload(analyzer, bundle, 'openai_lesson_file_id', bundle.lesson_pdf)
            exam_id = _upload(analyzer, bundle, 'openai_example_file_id', bundle.example_pdf)
            response = analyzer.analyze(
                model=bundle.model_name, temperature=0,
                instructions=bundle.prompt_template.instruction_text,
                json_schema=bundle.prompt_template.schema_json,
                textbook_file_id=lesson_id, exam_file_id=exam_id,
            )
        elif bundle.stage == AnalysisBundle.STAGE_TWO:
            prompt_text = fill_stage2_prompt(
                bundle.prompt_template.instruction_text,
                exam_map_json=inputs['EXAM_MAP_JSON'],
                student_answers=inputs['STUDENT_ANSWERS'],
            )
            response = analyzer.analyze_text(
                model=bundle.model_name, prompt_text=prompt_text, temperature=0.2,
            )
        elif bundle.stage == AnalysisBundle.STAGE_THREE:
            schema = bundle.prompt_template.schema_json
            if not schema:
                raise ValueError('Stage3 prompt schema_json is empty.')
            file_id = _upload(analyzer, bundle, 'openai_lesson_file_id', bundle.lesson_pdf)
            bundle.openai_example_file_id = file_id
            bundle.save(update_fields=['openai_example_file_id'])
            instructions = bundle.prompt_template.instruction_text.replace(
                '{{STAGE2_JSON}}', json.dumps(inputs['STAGE2_JSON'], ensure_ascii=False),
            )
            response = analyzer.analyze(
                model=bundle.model_name, instructions=instructions, json_schema=schema,
                textbook_file_id=file_id, exam_file_id=file_id, temperature=0.2,
            )
        else:
            raise ValueError('Unsupported analysis stage.')

        # API calls and uploads happen outside database transactions.
        with transaction.atomic():
            # The claim already prevents duplicates. Insert first so SQLite does
            # not have to upgrade a read transaction while the web app writes.
            AnalysisResult.objects.create(
                bundle=bundle,
                result_json=response.parsed_json,
                raw_output_text=response.raw_output_text,
                openai_response_id=response.response_id or '',
                usage_json=response.usage,
                stage=bundle.stage,
            )
            AnalysisBundle.objects.filter(pk=bundle_id).update(
                status=AnalysisBundle.STATUS_SUCCESS, error_message='',
            )
    except Exception as exc:
        logger.exception('Analysis bundle %s failed', bundle_id)
        AnalysisBundle.objects.filter(pk=bundle_id).update(
            status=AnalysisBundle.STATUS_FAILURE, error_message=str(exc),
        )


@shared_task(ignore_result=True)
def process_chat_request(request_id):
    claimed = ChatRequest.objects.filter(
        pk=request_id, status=AnalysisBundle.STATUS_PENDING,
    ).update(status=AnalysisBundle.STATUS_PROCESSING)
    if not claimed:
        return
    try:
        chat = ChatRequest.objects.get(pk=request_id)
        client = OpenAI(api_key=settings.OPENAI_API_KEY, timeout=3000)
        response = client.responses.create(model='gpt-5.2', input=chat.prompt)
        ChatRequest.objects.filter(pk=request_id).update(
            answer=response.output_text or str(response),
            status=AnalysisBundle.STATUS_SUCCESS, error_message='',
        )
    except Exception as exc:
        logger.exception('Chat request %s failed', request_id)
        ChatRequest.objects.filter(pk=request_id).update(
            status=AnalysisBundle.STATUS_FAILURE, error_message=str(exc),
        )
