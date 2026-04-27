"""Tests for pre_guard_security hook.

Fixture strings are assembled at runtime so the test file itself does not
contain literal dangerous patterns (otherwise the very hook under test would
block this file from being committed).
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


sec = _load_module("pre_guard_security")


def _matches(content: str) -> list[str]:
    hits: list[str] = []
    for pattern, description in sec.DANGEROUS_PATTERNS:
        if pattern.search(content):
            hits.append(description)
    return hits


# Fragment builders — keep individual literals harmless. The hook scans
# .py/.js/.ts/etc. files for the patterns; by splitting the strings here
# the source-level literals never form a complete dangerous pattern.
_DOT = "."
_OPEN = "("
_INNER_HTML = "inner" + "HTML"
_EVAL = "ev" + "al"
_DOCUMENT_WRITE = "document" + _DOT + "wri" + "te"
_NEW_FUNCTION = "new" + " " + "Func" + "tion"
_OS_SYSTEM = "os" + _DOT + "sys" + "tem"
_SUBPROCESS_RUN = "subprocess" + _DOT + "run"


def test_inner_html_assignment_detected():
    src = "el" + _DOT + _INNER_HTML + " = userInput"
    hits = _matches(src)
    assert any(_INNER_HTML in h for h in hits)


def test_inner_html_concat_detected():
    src = "el" + _DOT + _INNER_HTML + " += userInput"
    hits = _matches(src)
    assert any(_INNER_HTML in h for h in hits)


def test_eval_detected():
    src = _EVAL + _OPEN + "payload)"
    hits = _matches(src)
    assert any(_EVAL in h for h in hits)


def test_document_write_detected():
    src = _DOCUMENT_WRITE + _OPEN + "userInput)"
    hits = _matches(src)
    assert any("document" in h for h in hits)


def test_new_function_detected():
    src = "const fn = " + _NEW_FUNCTION + _OPEN + "'return 1')"
    hits = _matches(src)
    assert any("Function" in h for h in hits)


def test_shell_true_detected():
    src = _SUBPROCESS_RUN + _OPEN + "cmd, shell" + "=" + "True)"
    hits = _matches(src)
    assert any("shell" in h.lower() for h in hits)


def test_os_system_detected():
    src = _OS_SYSTEM + _OPEN + "cmd)"
    hits = _matches(src)
    assert any("system" in h.lower() for h in hits)


def test_safe_python_passes():
    assert _matches(_SUBPROCESS_RUN + _OPEN + "['ls', '-la'])") == []
    assert _matches("import os\nprint(os.environ['HOME'])") == []


def test_safe_js_passes():
    assert _matches("el" + _DOT + "textContent = userInput") == []
    # Quote-immediate form passes — assignment of a string literal with no
    # whitespace between `=` and the quote is treated as safe.
    safe = "el" + _DOT + _INNER_HTML + "='static'"
    assert _matches(safe) == []


def test_code_extensions_include_common_languages():
    for ext in (".js", ".ts", ".py", ".html"):
        assert ext in sec.CODE_EXTENSIONS
