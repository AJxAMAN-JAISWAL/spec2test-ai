
from datetime import datetime, timezone
from enum import Enum
from typing import ClassVar
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator


class TestStyle(str, Enum):
    __test__ = False

    MANUAL = "manual"
    GHERKIN = "gherkin"
    PLAYWRIGHT = "playwright"


class ScenarioType(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    BOUNDARY = "boundary"
    REGRESSION = "regression"


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AcceptanceCriterion(BaseModel):
    criterion_id: str = Field(
        min_length=1, max_length=30
    )
    description: str = Field(
        min_length=5, max_length=500
    )


class GenerateTestPlanRequest(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    user_story: str = Field(min_length=20, max_length=5000)
    acceptance_criteria: list[AcceptanceCriterion] = Field(
        min_length=1, max_length=20
    )
    test_style: TestStyle = TestStyle.MANUAL
    include_negative_cases: bool = True
    include_boundary_cases: bool = True

    @model_validator(mode="after")
    def validate_unique_criteria(self):
        ids = [
            criterion.criterion_id
            for criterion in self.acceptance_criteria
        ]
        if len(ids) != len(set(ids)):
            raise ValueError(
                "Acceptance criterion IDs must be unique."
            )
        return self


class TestStep(BaseModel):
    __test__: ClassVar[bool] = False

    action: str = Field(min_length=1)
    expected_result: str = Field(min_length=1)


class TestCase(BaseModel):
    __test__: ClassVar[bool] = False

    case_id: str
    title: str
    scenario_type: ScenarioType
    priority: Priority
    preconditions: list[str]
    steps: list[TestStep] = Field(min_length=1)
    expected_result: str = Field(min_length=1)
    acceptance_criteria_refs: list[str] = Field(default_factory=list)
    unmapped_reason: str | None = None


class CriterionCoverage(BaseModel):
    criterion_id: str
    status: str
    test_case_ids: list[str]


class AutomationDraft(BaseModel):
    language: str = "typescript"
    framework: str = "playwright"
    source: str


class TestPlanResponse(BaseModel):
    __test__: ClassVar[bool] = False

    plan_id: UUID = Field(default_factory=uuid4)
    status: str = "draft"
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    summary: str
    test_cases: list[TestCase]
    assumptions: list[str] = Field(default_factory=list)
    clarification_questions: list[str] = Field(default_factory=list)
    coverage: list[CriterionCoverage]
    automation_draft: AutomationDraft | None = None
