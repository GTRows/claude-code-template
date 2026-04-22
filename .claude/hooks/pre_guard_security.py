#!/usr/bin/env python3
"""
Hook: PreToolUse -- Write | Edit
Purpose: Block dangerous code patterns that introduce security vulnerabilities.
         Covers XSS (innerHTML), code injection (eval), and SQL injection.

Exit 2 = block + send stderr as feedback to Claude.

CUSTOMIZE: Add or remove patterns in DANGEROUS_PATTERNS to match your project needs.
"""

import json
import os
import re
import sys

# ---------- CONFIGURATION ----------
# Pattern -> human-readable risk description
DANGEROUS_PATTERNS = [
    (
        re.compile(r"\.innerHTML\s*=\s*[^\"'`]"),
        "innerHTML with dynamic content detected. Use textContent or DOM API instead.",
    ),
    (
        re.compile(r"\.innerHTML\s*\+="),
        "innerHTML concatenation detected. Use DOM API (createElement/appendChild) instead.",
    ),
    (
        re.compile(r"\beval\s*\("),
        "eval() detected. This is a code injection risk and blocked by most CSPs.",
    ),
    (
        re.compile(r"document\.write\s*\("),
        "document.write() detected. Use DOM API instead.",
    ),
    (
        re.compile(r"new\s+Function\s*\("),
        "new Function() detected. This is equivalent to eval and a security risk.",
    ),
    (
        re.compile(r"""(?:execute|query)\s*\(\s*(?:f['\"]|['\"].*?\{|.*?\+\s*[a-zA-Z])"""),
        "Possible SQL injection: string concatenation/interpolation in query. Use parameterized queries.",
    ),
    (
        re.compile(r"subprocess\.(?:call|run|Popen)\s*\(.*shell\s*=\s*True", re.DOTALL),
        "subprocess with shell=True detected. Use a list of arguments instead to prevent command injection.",
    ),
    (
        re.compile(r"os\.system\s*\("),
        "os.system() detected. Use subprocess with a list of arguments instead.",
    ),
]

# File extensions to scan
CODE_EXTENSIONS = {".js", ".mjs", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".py", ".pyw", ".html"}
# -----------------------------------


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path or os.path.splitext(file_path)[1].lower() not in CODE_EXTENSIONS:
        sys.exit(0)

    content = tool_input.get("content") or tool_input.get("new_string") or ""

    warnings = []
    for pattern, description in DANGEROUS_PATTERNS:
        if pattern.search(content):
            warnings.append(f"  - {description}")

    if warnings:
        print(
            f"Security risk in '{os.path.basename(file_path)}':\n"
            + "\n".join(warnings)
            + "\nFix the security issue before proceeding.",
            file=sys.stderr,
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
