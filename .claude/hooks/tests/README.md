# Hook tests

Run from repo root:

```bash
python -m pytest .claude/hooks/tests -q
```

Tests cover the regex predicates of every hook plus the template manifest
script. They do not exercise the stdin/stdout protocol — that is integration
territory and would require running the hook as a subprocess. The unit tests
here keep the patterns honest and catch silent regressions when someone
edits a regex.

If you add a new hook, add a matching `test_<hook_name>.py` here. Tests
should not contain literal dangerous values — assemble fixtures at runtime
so the hook under test does not block its own test file from being written.
