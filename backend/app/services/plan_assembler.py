
from uuid import uuid4

from app.schemas.generated_plans import GeneratedPlanContent
from app.schemas.test_plan import (
    CriterionCoverage,
    GenerateTestPlanRequest,
    TestCase,
    TestPlanResponse,
)


def build_test_plan_response(
    plan: GeneratedPlanContent,
    request: GenerateTestPlanRequest,
) -> TestPlanResponse:
    test_cases: list[TestCase] = []

    for generated_case in plan.test_cases:
        test_case = TestCase(
            case_id=str(uuid4()),
            **generated_case.model_dump(),
        )
        test_cases.append(test_case)

    coverage_map: dict[str, list[str]] = {
        criterion.criterion_id: []
        for criterion in request.acceptance_criteria
    }

    for test_case in test_cases:
        for criterion_id in test_case.acceptance_criteria_refs:
            coverage_map[criterion_id].append(test_case.case_id)

    coverage = [
        CriterionCoverage(
            criterion_id=criterion.criterion_id,
            status=(
                "covered"
                if coverage_map[criterion.criterion_id]
                else "uncovered"
            ),
            test_case_ids=coverage_map[criterion.criterion_id],
        )
        for criterion in request.acceptance_criteria
    ]

    return TestPlanResponse(
        summary=plan.summary,
        test_cases=test_cases,
        assumptions=plan.assumptions,
        clarification_questions=plan.clarification_questions,
        coverage=coverage,
        automation_draft=plan.automation_draft,
    )
