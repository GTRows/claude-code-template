#!/usr/bin/env python3
"""
Hook: UserPromptSubmit
Purpose: When the project has not been initialised via /setup, inject a
         reminder into the prompt's context so Claude nudges the user.
         Does NOT block — blocking creates a bootstrap deadlock when the
         `/setup` slash command hasn't loaded yet.

Stdout from UserPromptSubmit is appended to the user's prompt as context.
Exit 0 always.
"""

import os
import sys

PROJECT_DIR = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
MARKER = os.path.join(PROJECT_DIR, ".claude", ".setup-complete")


def main() -> None:
    if os.path.exists(MARKER):
        sys.exit(0)

    sys.stdout.write(
        "[template] This project has not been initialised by the template "
        "setup wizard (no .claude/.setup-complete marker). "
        "If the user is about to start coding work, recommend `/setup` first. "
        "Read-only questions and template maintenance are fine without it.\n"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
