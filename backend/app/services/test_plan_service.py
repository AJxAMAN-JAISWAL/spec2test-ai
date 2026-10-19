
from app.schemas.test_plan import (
    CriterionCoverage,
    GenerateTestPlanRequest,
    Priority,
    ScenarioType,
    TestCase,
    TestPlanResponse,
    TestStep,
)


def generate_mock_test_plan(
    request: GenerateTestPlanRequest,
) -> TestPlanResponse:
    """Return deterministic demo data without calling an LLM."""

    test_cases: list[TestCase] = []

    for index, criterion in enumerate(
        request.acceptance_criteria, start=1
    ):
        case_id = f"TC-{index:03d}"

        test_cases.append(
            TestCase(
                case_id=case_id,
                title=f"Verify {criterion.criterion_id}: "
                f"{criterion.description}",
                scenario_type=ScenarioType.POSITIVE,
                priority=Priority.HIGH,
                preconditions=[
                    "The application is available in the test environment."
                ],
                steps=[
                    TestStep(
                        action=(
                            "Set up the scenario described by the "
                            "acceptance criterion."
                        ),
                        expected_result=(
                            "The scenario is ready for verification."
                        ),
                    ),
                    TestStep(
                        action="Perform the relevant user action.",
                        expected_result=criterion.description,
                    ),
                ],
                expected_result=criterion.description,
                acceptance_criteria_refs=[criterion.criterion_id],
            )
        )

    # Coverage is computed by our code, not supplied by an AI model.
    coverage = []

    for criterion in request.acceptance_criteria:
        matching_cases = [
            case.case_id
            for case in test_cases
            if criterion.criterion_id
            in case.acceptance_criteria_refs
        ]

        coverage.append(
            CriterionCoverage(
                criterion_id=criterion.criterion_id,
                status="covered" if matching_cases else "uncovered",
                test_case_ids=matching_cases,
            )
        )

    return TestPlanResponse(
        summary=(
            f"Mock plan for '{request.title}' with "
            f"{len(test_cases)} draft test cases. "
            "These are illustrative placeholders, not executable tests."
        ),
        test_cases=test_cases,
        assumptions=[
            "The target application and test environment are available."
        ],
        clarification_questions=[],
        coverage=coverage,
        automation_draft=None,
    )
