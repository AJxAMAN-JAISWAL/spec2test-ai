
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


VALID_REQUEST = {
    "title": "Login validation",
    "user_story": (
        "As a user, I want to sign in using my email and password."
    ),
    "acceptance_criteria": [
        {
            "criterion_id": "AC-1",
            "description": "A user with valid credentials can sign in.",
        },
        {
            "criterion_id": "AC-2",
            "description": "Invalid credentials display an error.",
        },
    ],
    "test_style": "manual",
    "include_negative_cases": True,
    "include_boundary_cases": True,
}


def test_health_check():
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_generate_mock_test_plan():
    response = client.post(
        "/api/v1/test-plans",
        json=VALID_REQUEST,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "draft"
    assert len(data["test_cases"]) == 2
    assert data["automation_draft"] is None

    # Both criteria must be traceable to their test cases.
    assert data["coverage"] == [
        {
            "criterion_id": "AC-1",
            "status": "covered",
            "test_case_ids": ["TC-001"],
        },
        {
            "criterion_id": "AC-2",
            "status": "covered",
            "test_case_ids": ["TC-002"],
        },
    ]


def test_reject_empty_title():
    invalid_request = {
        **VALID_REQUEST,
        "title": "",
    }

    response = client.post(
        "/api/v1/test-plans",
        json=invalid_request,
    )

    assert response.status_code == 422


def test_reject_duplicate_criterion_ids():
    invalid_request = {
        **VALID_REQUEST,
        "acceptance_criteria": [
            {
                "criterion_id": "AC-1",
                "description": "First criterion is valid.",
            },
            {
                "criterion_id": "AC-1",
                "description": "Second criterion is also valid.",
            },
        ],
    }

    response = client.post(
        "/api/v1/test-plans",
        json=invalid_request,
    )

    assert response.status_code == 422


def test_reject_invalid_test_style():
    invalid_request = {
        **VALID_REQUEST,
        "test_style": "magic",
    }

    response = client.post(
        "/api/v1/test-plans",
        json=invalid_request,
    )

    assert response.status_code == 422
