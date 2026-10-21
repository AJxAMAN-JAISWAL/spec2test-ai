
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from app.schemas.test_plan import (
    AcceptanceCriterion,
    GenerateTestPlanRequest,
)
from app.services import llm_service


@pytest.fixture
def valid_request():
    return GenerateTestPlanRequest(
        title="Password reset",
        user_story=(
            "As a user, I want to reset my password "
            "so that I can regain access to my account."
        ),
        acceptance_criteria=[
            AcceptanceCriterion(
                criterion_id="AC-1",
                description=(
                    "The user can request a password reset "
                    "using a registered email address."
                ),
            )
        ],
    )


@pytest.fixture
def valid_plan_data():
    return {
        "summary": "Test the password reset request flow.",
        "test_cases": [
            {
                "title": "Reset password with registered email",
                "scenario_type": "positive",
                "priority": "high",
                "preconditions": ["The user has a registered account."],
                "steps": [
                    {
                        "action": "Enter a registered email address.",
                        "expected_result": "The email is accepted.",
                    }
                ],
                "expected_result": (
                    "A password reset confirmation is displayed."
                ),
                "acceptance_criteria_refs": ["AC-1"],
                "unmapped_reason": None,
            }
        ],
        "assumptions": [],
        "clarification_questions": [],
        "automation_draft": None,
    }


@pytest.fixture
def mock_settings(monkeypatch):
    monkeypatch.setattr(
        llm_service,
        "settings",
        SimpleNamespace(
            gemini_api_key="test-api-key",
            gemini_model="gemini-2.5-flash",
        ),
    )


def test_generate_plan_content_success(
    monkeypatch,
    mock_settings,
    valid_request,
    valid_plan_data,
):
    client = MagicMock()
    client.models.generate_content.return_value = SimpleNamespace(
        parsed=valid_plan_data,
        text=None,
    )

    monkeypatch.setattr(
        llm_service.genai,
        "Client",
        lambda **kwargs: client,
    )

    result = llm_service.generate_plan_content(valid_request)

    assert result.summary == valid_plan_data["summary"]
    assert len(result.test_cases) == 1
    assert result.test_cases[0].acceptance_criteria_refs == ["AC-1"]

    client.models.generate_content.assert_called_once()


def test_missing_api_key_raises_configuration_error(
    monkeypatch,
    valid_request,
):
    monkeypatch.setattr(
        llm_service,
        "settings",
        SimpleNamespace(
            gemini_api_key="",
            gemini_model="gemini-2.5-flash",
        ),
    )

    with pytest.raises(llm_service.GeminiConfigurationError):
        llm_service.generate_plan_content(valid_request)


def test_gemini_api_error_is_wrapped(
    monkeypatch,
    mock_settings,
    valid_request,
):
    client = MagicMock()
    client.models.generate_content.side_effect = RuntimeError(
        "Simulated API failure"
    )

    monkeypatch.setattr(
        llm_service.genai,
        "Client",
        lambda **kwargs: client,
    )

    with pytest.raises(llm_service.GeminiServiceError):
        llm_service.generate_plan_content(valid_request)


def test_empty_response_raises_invalid_output_error(
    monkeypatch,
    mock_settings,
    valid_request,
):
    client = MagicMock()
    client.models.generate_content.return_value = SimpleNamespace(
        parsed=None,
        text=None,
    )

    monkeypatch.setattr(
        llm_service.genai,
        "Client",
        lambda **kwargs: client,
    )

    with pytest.raises(llm_service.InvalidModelOutputError):
        llm_service.generate_plan_content(valid_request)


def test_malformed_json_raises_invalid_output_error(
    monkeypatch,
    mock_settings,
    valid_request,
):
    client = MagicMock()
    client.models.generate_content.return_value = SimpleNamespace(
        parsed=None,
        text="{invalid json",
    )

    monkeypatch.setattr(
        llm_service.genai,
        "Client",
        lambda **kwargs: client,
    )

    with pytest.raises(llm_service.InvalidModelOutputError):
        llm_service.generate_plan_content(valid_request)


def test_invalid_plan_data_raises_invalid_output_error(
    monkeypatch,
    mock_settings,
    valid_request,
):
    client = MagicMock()
    client.models.generate_content.return_value = SimpleNamespace(
        parsed={"summary": "", "test_cases": []},
        text=None,
    )

    monkeypatch.setattr(
        llm_service.genai,
        "Client",
        lambda **kwargs: client,
    )

    with pytest.raises(llm_service.InvalidModelOutputError):
        llm_service.generate_plan_content(valid_request)


def test_json_fallback_parses_valid_response(
    monkeypatch,
    mock_settings,
    valid_request,
    valid_plan_data,
):
    import json

    client = MagicMock()
    client.models.generate_content.return_value = SimpleNamespace(
        parsed=None,
        text=json.dumps(valid_plan_data),
    )

    monkeypatch.setattr(
        llm_service.genai,
        "Client",
        lambda **kwargs: client,
    )

    result = llm_service.generate_plan_content(valid_request)

    assert result.summary == valid_plan_data["summary"]
    assert len(result.test_cases) == 1


def test_unknown_criterion_reference_raises_error(
    monkeypatch,
    mock_settings,
    valid_request,
    valid_plan_data,
):
    valid_plan_data["test_cases"][0][
        "acceptance_criteria_refs"
    ] = ["AC-999"]

    client = MagicMock()
    client.models.generate_content.return_value = SimpleNamespace(
        parsed=valid_plan_data,
        text=None,
    )

    monkeypatch.setattr(
        llm_service.genai,
        "Client",
        lambda **kwargs: client,
    )

    with pytest.raises(llm_service.InvalidModelOutputError):
        llm_service.generate_plan_content(valid_request)
