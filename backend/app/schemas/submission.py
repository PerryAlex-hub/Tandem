from typing import Any

from pydantic import BaseModel


class SubmitRequest(BaseModel):
    code: str


class TestCaseResult(BaseModel):
    input: list
    expected: Any | None
    actual: Any | None
    passed: bool
    error: str | None = None


class SubmissionResult(BaseModel):
    passed: bool
    results: list[TestCaseResult]
