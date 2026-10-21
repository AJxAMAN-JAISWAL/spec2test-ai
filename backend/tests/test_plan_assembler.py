
from app.schemas.generated_plans import GeneratedPlanContent
from app.schemas.test_plan import (
    AcceptanceCriterion,
    GenerateTestPlanRequest,
)
from app.services.plan_assembler import build_test_plan_response


def test_build_test_plan_response_assigns_ids_and_coverage():
    request = GenerateTestPlanRequest(
        title="Password reset",
        user_story=(
            "As a user, I want to reset my password "
            "so that I can regain access to my account."
        ),
        acceptance_criteria=[
            AcceptanceCriterion(
                criterion_id="AC-1",
                description="Registered email is accepted.",
            ),
            AcceptanceCriterion(
                criterion_id="AC-2",
                description="A confirmation message is displayed.",
            ),
        ],
    )

    plan = GeneratedPlanContent(
        summary="Test the password reset flow.",
        test_cases=[
            {
                "title": "Submit a registered email",
                "scenario_type": "positive",
                "priority": "high",
                "preconditions": [],
                "steps": [
                    {
                        "action": "Enter a registered email.",
                        "expected_result": "The email is accepted.",
                    }
                ],
                "expected_result": "A confirmation message is displayed.",
                "acceptance_criteria_refs": ["AC-1"],
            }
        ],
    )

    response = build_test_plan_response(plan, request)

    assert response.plan_id is not None
    assert response.generated_at is not None
    assert len(response.test_cases) == 1
    assert response.test_cases[0].case_id

    assert len({
        case.case_id for case in response.test_cases
    }) == len(response.test_cases)

    coverage = {
        item.criterion_id: item
        for item in response.coverage
    }

    assert coverage["AC-1"].status == "covered"
    assert coverage["AC-1"].test_case_ids == [
        response.test_cases[0].case_id
    ]

    assert coverage["AC-2"].status == "uncovered"
    assert coverage["AC-2"].test_case_ids == []
