import json

from app.execution.harness import build_harness
from app.execution.signature import parse_signature
from app.execution.testcases import parse_example_outputs, parse_example_testcases
from app.models.problem import Problem
from app.services.piston_service import execute_code


async def run_submission(problem: Problem, submitted_code: str) -> dict:
    python_snippet = next(s for s in problem.code_snippets if s["langSlug"] == "python3")
    method_name, param_count = parse_signature(python_snippet["code"])

    test_cases = parse_example_testcases(problem.example_testcases, param_count)
    expected_outputs = parse_example_outputs(problem.description_html)

    harness_source = build_harness(submitted_code, method_name, test_cases)
    run_result = await execute_code(harness_source)

    actual_lines = run_result["stdout"].strip().split("\n") if run_result["stdout"].strip() else []

    results = []
    for i, test_case in enumerate(test_cases):
        expected = expected_outputs[i] if i < len(expected_outputs) else None

        if run_result["code"] != 0:
            error_detail = run_result["stderr"] or run_result.get("message") or "Execution failed"
            results.append({
                "input": test_case, "expected": expected, "actual": None,
                "passed": False, "error": error_detail,
            })
            continue

        if i >= len(actual_lines):
            results.append({
                "input": test_case, "expected": expected, "actual": None,
                "passed": False, "error": "No output produced for this test case",
            })
            continue

        try:
            actual = json.loads(actual_lines[i])
            error = None
        except json.JSONDecodeError:
            actual = None
            error = "Could not parse program output"

        results.append({
            "input": test_case, "expected": expected, "actual": actual,
            "passed": actual == expected, "error": error,
        })

    return {"passed": all(r["passed"] for r in results), "results": results}
