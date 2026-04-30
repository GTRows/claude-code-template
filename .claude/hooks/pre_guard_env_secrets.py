#!/usr/bin/env python3
"""
Hook: PreToolUse -- Write | Edit
Purpose: Prevent hardcoded secrets, API keys, and credentials from being written
         into source files. Scans content for common secret patterns.

Exit 2 = block + send stderr as feedback to Claude.
"""

import json
import os
import re
import sys

# ---------- CONFIGURATION ----------
# Protected filenames that should never be created/edited by Claude
PROTECTED_FILES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.staging",
    ".env.development",
    "credentials.json",
    "service-account.json",
    "secrets.yml",
    "secrets.yaml",
}

# Patterns that indicate hardcoded secrets in code
SECRET_PATTERNS = [
    (
        re.compile(r"""(?:api[_-]?key|apikey|secret[_-]?key|auth[_-]?token|access[_-]?token|private[_-]?key)\s*[:=]\s*['\"][A-Za-z0-9+/=_\-]{16,}['\"]""", re.IGNORECASE),
        "Hardcoded API key or secret token detected. Use environment variables instead.",
    ),
    (
        re.compile(r"""['\"]sk-[A-Za-z0-9]{20,}['\"]"""),
        "OpenAI API key pattern (sk-...) detected. Use environment variables.",
    ),
    (
        re.compile(r"""['\"]AKIA[A-Z0-9]{12,}['\"]"""),
        "AWS Access Key ID pattern (AKIA...) detected. Use environment variables.",
    ),
    (
        re.compile(r"""['\"]ghp_[A-Za-z0-9]{36,}['\"]"""),
        "GitHub Personal Access Token (ghp_...) detected. Use environment variables.",
    ),
    (
        re.compile(r"""['\"]glpat-[A-Za-z0-9\-]{20,}['\"]"""),
        "GitLab Personal Access Token detected. Use environment variables.",
    ),
    (
        re.compile(r"""(?:password|passwd|pwd)\s*[:=]\s*['\"][^'\"]{8,}['\"]""", re.IGNORECASE),
        "Hardcoded password detected. Use environment variables or a secrets manager.",
    ),
    (
        re.compile(r"""-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----"""),
        "Private key detected in source file. Store keys in secure key management.",
    ),
]

# File extensions to scan for secrets
CODE_EXTENSIONS = {
    ".js", ".mjs", ".jsx", ".ts", ".tsx", ".py", ".pyw",
    ".go", ".rs", ".java", ".kt", ".cs", ".rb",
    ".vue", ".svelte", ".html", ".yml", ".yaml", ".toml", ".json",
    ".sh", ".bash", ".zsh", ".ps1", ".bat", ".cmd",
}
# -----------------------------------



# --- audit ---
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
try:
    from _audit import record_block as _record_block
except Exception:
    def _record_block(*_args, **_kwargs):
        pass
# --- end audit ---

def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path:
        sys.exit(0)

    name = os.path.basename(file_path).lower()

    # Block writing to secret files entirely
    if name in PROTECTED_FILES:
        print(
            f"Blocked: '{name}' is a secrets/environment file.\n"
            "Do not create or edit secrets files. "
            "Advise the user to manage secrets manually.",
            file=sys.stderr,
        )
        _record_block("pre_guard_env_secrets", file_path=file_path, reason=f"secrets/env file: {name}")
        sys.exit(2)

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in CODE_EXTENSIONS:
        sys.exit(0)

    content = tool_input.get("content") or tool_input.get("new_string") or ""

    warnings = []
    for pattern, description in SECRET_PATTERNS:
        if pattern.search(content):
            warnings.append(f"  - {description}")

    if warnings:
        print(
            f"Potential secret in '{os.path.basename(file_path)}':\n"
            + "\n".join(warnings)
            + "\nRemove hardcoded secrets and use environment variables.",
            file=sys.stderr,
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
