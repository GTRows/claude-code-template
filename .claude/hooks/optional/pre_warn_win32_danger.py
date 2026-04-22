#!/usr/bin/env python3
"""
Hook: PreToolUse - Write | Edit
Purpose: Warn before writing Python code that contains high-risk Windows API patterns.
         For projects that use ctypes / winreg directly; some calls can corrupt
         system state if used incorrectly (HKLM writes, SystemParametersInfo,
         UAC elevation via 'runas').

OPTIONAL HOOK. Not registered by default.
To enable: register this script in .claude/settings.json under PreToolUse matcher "Write|Edit":
    "command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/optional/pre_warn_win32_danger.py\""

Exit 2 = block + send stderr as feedback to Claude.
"""

import json
import os
import re
import sys

RISKY_PATTERNS: list[tuple[re.Pattern, str]] = [
    (
        re.compile(r"winreg\.OpenKey\s*\(.*HKEY_LOCAL_MACHINE", re.IGNORECASE),
        "Writing to HKEY_LOCAL_MACHINE affects all users. Use HKEY_CURRENT_USER unless strictly necessary.",
    ),
    (
        re.compile(r"winreg\.SetValue|winreg\.SetValueEx", re.IGNORECASE),
        "Registry write detected. Ensure a backup/restore path exists before modifying the registry.",
    ),
    (
        re.compile(r"SystemParametersInfo", re.IGNORECASE),
        "SystemParametersInfo changes system-wide display or UI settings. Verify the flags and confirm with the user.",
    ),
    (
        re.compile(r"\"runas\"", re.IGNORECASE),
        "UAC elevation via 'runas' detected. Confirm the user intends to run this with admin privileges.",
    ),
    (
        re.compile(r"ctypes\.windll\.advapi32", re.IGNORECASE),
        "advapi32 call detected. These APIs can modify security descriptors, services, or the registry.",
    ),
]

CODE_EXTENSIONS = {".py", ".pyw"}


def is_code_file(path: str) -> bool:
    return os.path.splitext(path)[1].lower() in CODE_EXTENSIONS


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not is_code_file(file_path):
        sys.exit(0)

    content = tool_input.get("content") or tool_input.get("new_string") or ""

    warnings: list[str] = []
    for pattern, description in RISKY_PATTERNS:
        if pattern.search(content):
            warnings.append(f"  - {description}")

    if warnings:
        print(
            f"High-risk Windows API pattern detected in '{os.path.basename(file_path)}':\n"
            + "\n".join(warnings)
            + "\nConfirm with the user before writing this code.",
            file=sys.stderr,
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
