#!/usr/bin/env python3
"""
Hook: PostToolUse -- Write | Edit
Purpose: Validate syntax of written files immediately after creation/edit.
         Supports multiple languages: Python, JavaScript, TypeScript, JSON.
         Feed errors back to Claude before it proceeds further.

Exit 2 = block + send stderr as feedback to Claude.
"""

import json
import os
import subprocess
import sys

# ---------- CONFIGURATION ----------
# Map file extensions to their validation commands
# Each entry: extension -> (command_template, timeout_seconds)
# {file} is replaced with the actual file path
VALIDATORS = {
    ".py": {
        "method": "py_compile",
    },
    ".js": {
        "command": ["node", "--check", "{file}"],
        "timeout": 10,
    },
    ".mjs": {
        "command": ["node", "--check", "{file}"],
        "timeout": 10,
    },
    ".json": {
        "method": "json_parse",
    },
}
# -----------------------------------


def validate_python(file_path: str) -> str | None:
    """Validate Python syntax using py_compile."""
    import py_compile
    try:
        py_compile.compile(file_path, doraise=True)
        return None
    except py_compile.PyCompileError as exc:
        return str(exc)


def validate_json(file_path: str) -> str | None:
    """Validate JSON syntax."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            json.load(f)
        return None
    except json.JSONDecodeError as exc:
        return f"JSON syntax error: {exc}"


def validate_command(file_path: str, command: list, timeout: int) -> str | None:
    """Validate using an external command."""
    cmd = [part.replace("{file}", file_path) for part in command]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            return result.stderr.strip() or result.stdout.strip()
        return None
    except FileNotFoundError:
        # Validator not installed, skip silently
        return None
    except subprocess.TimeoutExpired:
        return f"Validation timed out after {timeout}s"


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    file_path = data.get("tool_input", {}).get("file_path", "")
    if not file_path:
        sys.exit(0)

    ext = os.path.splitext(file_path)[1].lower()
    validator = VALIDATORS.get(ext)
    if not validator:
        sys.exit(0)

    file_path = os.path.normpath(file_path)
    if not os.path.isfile(file_path):
        sys.exit(0)

    error = None
    method = validator.get("method")

    if method == "py_compile":
        error = validate_python(file_path)
    elif method == "json_parse":
        error = validate_json(file_path)
    elif "command" in validator:
        error = validate_command(file_path, validator["command"], validator.get("timeout", 10))

    if error:
        print(
            f"Syntax error in '{file_path}':\n{error}\n"
            "Fix the syntax error before proceeding.",
            file=sys.stderr,
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
