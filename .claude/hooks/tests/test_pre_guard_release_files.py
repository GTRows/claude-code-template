"""Tests for pre_guard_release_files hook."""

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


pre_guard = _load_module("pre_guard_release_files")


def test_protected_exact_filename_blocks():
    assert pre_guard.is_protected("package.json") is True
    assert pre_guard.is_protected("PROJECT.yaml") is True
    assert pre_guard.is_protected("CHANGELOG.md") is True


def test_protected_dir_blocks():
    assert pre_guard.is_protected(".github/workflows/release.yml") is True
    assert pre_guard.is_protected("scripts/build.sh") is True


def test_exempt_dir_unblocks_command_files():
    assert pre_guard.is_protected(".claude/commands/release.md") is False
    assert pre_guard.is_protected(".claude/commands/changelog.md") is False
    assert pre_guard.is_protected(".claude/scripts/manifest.py") is False
    assert pre_guard.is_protected(".claude/hooks/pre_guard_security.py") is False


def test_unrelated_files_pass():
    assert pre_guard.is_protected("src/app.py") is False
    assert pre_guard.is_protected("README.md") is False
    assert pre_guard.is_protected("") is False


def test_protected_suffix_blocks():
    assert pre_guard.is_protected("installer.spec") is True
    assert pre_guard.is_protected("setup.iss") is True


def test_case_insensitive_basename():
    assert pre_guard.is_protected("Package.JSON") is True
    assert pre_guard.is_protected("Cargo.LOCK") is True


def test_windows_path_separators():
    assert pre_guard.is_protected(".github\\workflows\\ci.yml") is True
    assert pre_guard.is_protected(".claude\\commands\\release.md") is False
