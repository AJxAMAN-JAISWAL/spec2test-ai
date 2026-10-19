
from fastapi import APIRouter

from app.schemas.test_plan import (
    GenerateTestPlanRequest,
    TestPlanResponse,
)
from app.services.test_plan_service import generate_mock_test_plan

router = APIRouter(prefix="/api/v1/test-plans", tags=["Test Plans"])


@router.post("", response_model=TestPlanResponse, status_code=200)
def generate_test_plan(
    request: GenerateTestPlanRequest,
) -> TestPlanResponse:
    return generate_mock_test_plan(request)
