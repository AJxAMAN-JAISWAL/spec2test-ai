
from fastapi import FastAPI

from app.api.routes.test_plans import router as test_plans_router

app = FastAPI(
    title="Spec2Test AI API",
    description="API for generating traceable QA test plans.",
    version="0.1.0",
)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(test_plans_router)
