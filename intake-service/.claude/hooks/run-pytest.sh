#!/bin/bash
# Runs after every Edit or Write the agent makes (see .claude/settings.json).
# If the edited file is Python and the tests fail, the failures are sent back
# to the agent so it sees them straight away.

# The hook receives a JSON description of the edit on stdin.
file=$(jq -r '.tool_input.file_path // empty')

# Only Python files can change the test results.
case "$file" in
  *.py) ;;
  *) exit 0 ;;
esac

cd "$CLAUDE_PROJECT_DIR" || exit 0

# --tb=no keeps the output to the list of failing tests and the totals.
if output=$(uv run pytest -q --tb=no 2>&1); then
  exit 0
fi

# Exit code 2 tells Claude Code to show stderr to the agent.
echo "pytest is failing after the edit to $file:" >&2
echo "$output" | tail -n 60 >&2
exit 2
