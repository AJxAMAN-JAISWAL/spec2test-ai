
import json
from urllib import response

from google import genai
from google.genai import types
from pydantic import ValidationError

from app.core.config import settings
from app.prompts.v1_test_plan import build_test_plan_prompt
from app.schemas.generated_plans import GeneratedPlanContent
from app.schemas.test_plan import GenerateTestPlanRequest


class GeminiServiceError(Exception):
    """Base error for Gemini generation failures."""


class GeminiConfigurationError(GeminiServiceError):
    """Raised when Gemini configuration is missing."""


class InvalidModelOutputError(GeminiServiceError):
    """Raised when the model returns invalid output."""


def generate_plan_content(
    request: GenerateTestPlanRequest,
) -> GeneratedPlanContent:
    if not settings.gemini_api_key:
        raise GeminiConfigurationError(
            "GEMINI_API_KEY is not configured."
        )

    prompt = build_test_plan_prompt(request)
    client = genai.Client(api_key=settings.gemini_api_key)

    try:
        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=GeneratedPlanContent,
            ),
        )
    except Exception as exc:
        raise GeminiServiceError(
            f"Gemini request failed ({type(exc).__name__})."
        ) from exc

    
    
    if response.parsed is not None:
        try:
            plan = GeneratedPlanContent.model_validate(
                response.parsed
            )
        except ValidationError as exc:
            raise InvalidModelOutputError(
                "Gemini returned content that failed validation."
            ) from exc

        return _validate_criterion_references(plan, request)

    if not response.text:
        raise InvalidModelOutputError(
            "Gemini returned an empty response."
        )

    try:
        data = json.loads(response.text)
        plan = GeneratedPlanContent.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise InvalidModelOutputError(
            "Gemini returned invalid JSON or an invalid test plan."
        ) from exc

    return _validate_criterion_references(plan, request)




def _validate_criterion_references(
    plan: GeneratedPlanContent,
    request: GenerateTestPlanRequest,
) -> GeneratedPlanContent:
    valid_criterion_ids = {
        criterion.criterion_id
        for criterion in request.acceptance_criteria
    }

    for test_case in plan.test_cases:
        unknown_refs = (
            set(test_case.acceptance_criteria_refs)
            - valid_criterion_ids
        )

        if unknown_refs:
            invalid_ids = ", ".join(sorted(unknown_refs))
            raise InvalidModelOutputError(
                "Gemini referenced unknown acceptance criterion "
                f"ID(s): {invalid_ids}."
            )

    return plan
