import re


def _split_params(params: str) -> list[str]:
    parts = []
    depth = 0
    current = ""
    for ch in params:
        if ch in "[({":
            depth += 1
        elif ch in "])}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(current.strip())
            current = ""
        else:
            current += ch
    if current.strip():
        parts.append(current.strip())
    return parts


def parse_signature(starter_code: str) -> tuple[str, int]:
    match = re.search(r"def\s+(\w+)\s*\(self\s*(?:,\s*(.*?))?\)\s*(?:->.*)?:", starter_code)
    if match is None:
        raise ValueError("Could not parse method signature from starter code")

    method_name = match.group(1)
    params_str = match.group(2) or ""
    params = _split_params(params_str) if params_str else []
    return method_name, len(params)
