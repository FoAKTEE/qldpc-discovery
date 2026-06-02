#!/usr/bin/env bash
# ralph_stop_guard.sh — reference implementation of the Stop-hook guard.
#
# Reads .claude/ralph-loop.local.md frontmatter. If a Ralph loop is active
# and iteration < max_iterations, emit the client stop-hook "block" decision so
# the agent is forced to continue. Otherwise exit silently and let the normal
# stop happen.

set -u

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || printf '%s' "$(cd "$(dirname "$0")/.." && pwd)")"
STATE="$REPO_ROOT/.claude/ralph-loop.local.md"

[ -f "$STATE" ] || exit 0

# The local state file has two yaml blocks: the first carries role/scope/discipline
# metadata, the second (n==3 after three `---` markers) carries the live runtime
# keys (active, iteration, max_iterations). Scan both block-1 and block-3 so we
# remain forward-compatible with single-block variants.
active=$(awk '/^---$/{n++; next} (n==1 || n==3) && /^active:/ {print $2}' "$STATE" | head -1)
iter=$(awk '/^---$/{n++; next} (n==1 || n==3) && /^iteration:/ {print $2}' "$STATE" | head -1)
max=$(awk '/^---$/{n++; next} (n==1 || n==3) && /^max_iterations:/ {print $2}' "$STATE" | head -1)

[ "$active" = "true" ] || exit 0
[ -n "$iter" ] && [ -n "$max" ] || exit 0

case "$iter$max" in
    *[!0-9]*) exit 0 ;;
esac

if [ "$iter" -lt "$max" ]; then
    reason="Ralph loop active — iteration ${iter}/${max}. Advance the counter in .claude/ralph-loop.local.md, ship the next verified step, then continue. Do NOT stop until iteration >= max_iterations or active=false. If stalled >30 min, escalate per alignment.md L3+ 揪头条 (7 项检查清单) with a 30-min cap."
    printf '{"decision":"block","reason":%s}\n' \
        "$(printf '%s' "$reason" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')"
fi

exit 0
