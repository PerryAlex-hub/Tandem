def build_harness(submitted_code: str, method_name: str, test_cases: list[list]) -> str:
    lines = [submitted_code, "", "import json", "", "_solution = Solution()", ""]

    for args in test_cases:
        args_repr = ", ".join(repr(arg) for arg in args)
        lines.append(f"print(json.dumps(_solution.{method_name}({args_repr})))")

    return "\n".join(lines)
