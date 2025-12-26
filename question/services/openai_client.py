from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

from django.conf import settings
from openai import OpenAI


@dataclass
class OpenAIAnalysisResponse:
    response_id: str
    parsed_json: Dict[str, Any]
    raw_output_text: str
    usage: Optional[Dict[str, Any]]


class OpenAIAnalyzer:
    def __init__(self) -> None:
        api_key = getattr(settings, "OPENAI_API_KEY", None)
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")
        self.client = OpenAI(api_key=api_key, timeout=3000)

    def _ensure_client(self) -> None:
        if not hasattr(self, "client") or self.client is None:
            raise RuntimeError("OpenAI client is not initialized. Did init run?")

    def upload_pdf(self, file_path: str) -> str:
        self._ensure_client()
        with open(file_path, "rb") as f:
            uploaded = self.client.files.create(file=f, purpose="user_data")
        return uploaded.id

    def analyze(
        self,
        *,
        model: str,
        instructions: str,
        json_schema: Dict[str, Any],
        textbook_file_id: str,
        exam_file_id: str,
    ) -> OpenAIAnalysisResponse:
        response = self.client.responses.create(
            model=model,
            instructions=instructions,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "Textbook File:"},
                        {"type": "input_file", "file_id": textbook_file_id},
                        {"type": "input_text", "text": "Exam File:"},
                        {"type": "input_file", "file_id": exam_file_id}
                    ],
                }
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "lesson_exam_analysis",
                    "schema": json_schema,
                    "strict": True
                }
            },
        )

        raw_text = getattr(response, "output_text", "") or ""

        # تلاش برای استخراج JSON از content
        parsed = None
        for item in getattr(response, "output", []) or []:
            for c in getattr(item, "content", []) or []:
                # معمولاً به صورت متن JSON برمی‌گرده
                if getattr(c, "type", None) in ("output_text", "text"):
                    try:
                        parsed = json.loads(c.text)
                        break
                    except Exception:
                        pass
            if parsed is not None:
                break

        if parsed is None:
            raise ValueError("Could not parse JSON from model output.")

        usage = getattr(response, "usage", None)
        usage_dict = usage.model_dump() if hasattr(usage, "model_dump") else (usage if isinstance(usage, dict) else None)

        return OpenAIAnalysisResponse(
            response_id=response.id,
            parsed_json=parsed,
            raw_output_text=raw_text,
            usage=usage_dict,
        )