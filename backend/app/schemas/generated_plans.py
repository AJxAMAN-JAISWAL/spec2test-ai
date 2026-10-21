
from pydantic import BaseModel, Field

from app.schemas.test_plan import (
    AutomationDraft,
    Priority,
    ScenarioType,
    TestStep,
)


class GeneratedTestCase(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    scenario_type: ScenarioType
    priority: Priority
    preconditions: list[str] = Field(default_factory=list)
    steps: list[TestStep] = Field(min_length=1, max_length=20)
    expected_result: str = Field(min_length=1, max_length=1000)
    acceptance_criteria_refs: list[str] = Field(default_factory=list)
    unmapped_reason: str | None = None


class GeneratedPlanContent(BaseModel):
    summary: str = Field(min_length=1, max_length=1000)
    test_cases: list[GeneratedTestCase] = Field(min_length=1, max_length=100)
    assumptions: list[str] = Field(default_factory=list)
    clarification_questions: list[str] = Field(default_factory=list)
    automation_draft: AutomationDraft | None = None
