import ast
import re


def _safe_literal_eval(value: str):
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        normalized = value.replace("true", "True").replace("false", "False").replace("null", "None")
        return ast.literal_eval(normalized)


def parse_example_testcases(raw: str, param_count: int) -> list[list]:
    lines = [line for line in raw.strip().split("\n") if line.strip() != ""]
    values = [_safe_literal_eval(line) for line in lines]

    if param_count == 0:
        return [[] for _ in values]

    return [values[i:i + param_count] for i in range(0, len(values), param_count)]


def parse_example_outputs(content_html: str) -> list:
    matches = re.findall(r"<strong>Output:</strong>\s*([^\n<]+)", content_html)
    return [_safe_literal_eval(m.strip()) for m in matches]
