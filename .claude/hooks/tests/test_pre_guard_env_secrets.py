"""Tests for pre_guard_env_secrets hook.

Fixture strings are assembled at runtime so the test file itself does not
contain literal secret-looking values (otherwise the very hook under test
would block this file from being committed).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parents[1]


def _load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, HOOKS_DIR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


secrets = _load_module("pre_guard_env_secrets")


def _matches(content: str) -> list[str]:
    hits: list[str] = []
    for pattern, description in secrets.SECRET_PATTERNS:
        if pattern.search(content):
            hits.append(description)
    return hits


# Built at import time, kept short so the source itself contains no full
# pattern that the hook regex would match.
def _openai_key() -> str:
    return "s" + "k-" + "a" * 32


def _aws_key() -> str:
    return "AK" + "IA" + "B" * 16


def _github_pat() -> str:
    return "g" + "hp_" + "c" * 40


def _private_key_header() -> str:
    return "-----BE" + "GIN " + "RSA PRI" + "VATE KEY-----"


def test_openai_key_detected():
    hits = _matches('OPENAI_KEY = "%s"' % _openai_key())
    assert any("OpenAI" in h for h in hits)


def test_aws_access_key_detected():
    hits = _matches('AWS_KEY = "%s"' % _aws_key())
    assert any("AWS" in h for h in hits)


def test_github_pat_detected():
    hits = _matches('TOKEN = "%s"' % _github_pat())
    assert any("GitHub" in h for h in hits)


def test_private_key_detected():
    hits = _matches(_private_key_header())
    assert any("Private key" in h for h in hits)


def test_generic_api_key_pattern_detected():
    payload = "x" * 24
    hits = _matches('api_key = "%s"' % payload)
    assert any("API key" in h or "secret token" in h for h in hits)


def test_hardcoded_password_detected():
    hits = _matches('password = "%s"' % ("z" * 12))
    assert any("password" in h.lower() for h in hits)


def test_clean_code_passes():
    assert _matches("import os\nKEY = os.environ['API_KEY']") == []
    assert _matches("# api_key from env") == []


def test_protected_file_set_membership():
    assert ".env" in secrets.PROTECTED_FILES
    assert ".env.production" in secrets.PROTECTED_FILES
    assert "credentials.json" in secrets.PROTECTED_FILES


def test_code_extensions_include_common_languages():
    for ext in (".py", ".js", ".ts", ".go", ".rs", ".yml"):
        assert ext in secrets.CODE_EXTENSIONS
