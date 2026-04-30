"""Tests for the plugin pin tracker."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


plugins = _load("plugins_mod", SCRIPTS / "plugins.py")


def test_render_string():
    assert plugins._render("foo@bar") == "foo@bar"
    assert plugins._render("plain-name") is None


def test_render_dict():
    assert plugins._render({"name": "x", "marketplace": "y"}) == "x@y"
    assert plugins._render({"id": "x", "source": "y"}) == "x@y"
    assert plugins._render({"name": "x"}) is None


def test_save_and_load_pin(tmp_path: Path):
    pinned = ["a@b", "c@d"]
    plugins.save_pin(tmp_path, pinned)
    loaded = plugins.load_pin(tmp_path)
    assert loaded == {"plugins": pinned}


def test_diff_finds_missing_and_extra():
    missing, extra = plugins.diff(installed=["a@m", "c@m"], pinned=["a@m", "b@m"])
    assert missing == ["b@m"]
    assert extra == ["c@m"]


def test_diff_empty_when_aligned():
    missing, extra = plugins.diff(installed=["a@m"], pinned=["a@m"])
    assert missing == [] and extra == []


def test_load_pin_empty_when_absent(tmp_path: Path):
    assert plugins.load_pin(tmp_path) == {}
