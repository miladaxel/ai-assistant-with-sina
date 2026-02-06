import json
from typing import Dict, Any

from question.services.openai_client import OpenAIAnalyzer


def fill_stage2_prompt(
    template_text: str,
    *,
    exam_map_json: Dict[str, Any],
    student_answers: Dict[str, Any],
) -> str:
    """
    Stage2 prompt placeholders:
      - {{EXAM_MAP_JSON}}
      - {{STUDENT_ANSWERS}}
    """
    return (
        template_text
        .replace("{{EXAM_MAP_JSON}}", json.dumps(exam_map_json, ensure_ascii=False))
        .replace("{{STUDENT_ANSWERS}}", json.dumps(student_answers, ensure_ascii=False))
    )


def run_stage2_for_student(*, bundle) -> dict:
    """
    bundle.input_json must include:
      - EXAM_MAP_JSON
      - STUDENT_ANSWERS
    Uses OpenAIAnalyzer.analyze_text to get parsed JSON safely.
    """
    exam_map_json = bundle.input_json.get("EXAM_MAP_JSON")
    student_answers = bundle.input_json.get("STUDENT_ANSWERS")

    if exam_map_json is None:
        raise ValueError("bundle.input_json['EXAM_MAP_JSON'] is missing")
    if student_answers is None:
        raise ValueError("bundle.input_json['STUDENT_ANSWERS'] is missing")

    prompt_text = fill_stage2_prompt(
        bundle.prompt_template.instruction_text,
        exam_map_json=exam_map_json,
        student_answers=student_answers,
    )

    analyzer = OpenAIAnalyzer()
    resp = analyzer.analyze_text(
        model=bundle.model_name or "gpt-4o-mini",
        prompt_text=prompt_text,
    )

    return {
        "result_json": resp.parsed_json,
        "raw_output_text": resp.raw_output_text,
        "openai_response_id": resp.response_id,
        "usage_json": resp.usage,
    }