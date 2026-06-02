#!/usr/bin/env bash
# inject_infra.sh — methodology-repo reference implementation.
#
# Reads the phys-agentic-loop methodology core (alignment + _common + state
# templates) from disk and emits a <session-start-briefing> envelope.
#
# Auto-detects layout:
#   * Inside this repo:   $REPO_ROOT/alignment.md exists -> $PAL_ROOT=$REPO_ROOT.
#   * Consumer repo:      $REPO_ROOT/phys-agentic-loop/alignment.md exists ->
#                         $PAL_ROOT=$REPO_ROOT/phys-agentic-loop.
#
# Wired into .claude/settings.json as the SessionStart hook, and also usable as
# a manual bootstrap for clients that do not support hooks. Consumer repos may
# fork this and append project-specific state injection (e.g. local ralph-loop
# state, project progress notes).

set -u

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || printf '%s' "$(cd "$(dirname "$0")/.." && pwd)")"
if [ -f "$REPO_ROOT/alignment.md" ]; then
    PAL_ROOT="$REPO_ROOT"
else
    PAL_ROOT="$REPO_ROOT/phys-agentic-loop"
fi
STATE="$REPO_ROOT/.claude/ralph-loop.local.md"

# MULTI-WINDOW TOLERANCE (iter 304 user directive): if mid-task intermediate
# window, emit lightweight marker only and skip full re-injection.
mw_active=""
mw_closing=""
mw_count=""
mw_max=""
if [ -f "$STATE" ]; then
    mw_active=$(awk '/^multi_window_task:/{in_mw=1; next} in_mw && /^[^ ]/{in_mw=0} in_mw && /active:/{gsub("\r",""); print $2; exit}' "$STATE")
    mw_closing=$(awk '/^multi_window_task:/{in_mw=1; next} in_mw && /^[^ ]/{in_mw=0} in_mw && /closing:/{gsub("\r",""); print $2; exit}' "$STATE")
    mw_count=$(awk '/^multi_window_task:/{in_mw=1; next} in_mw && /^[^ ]/{in_mw=0} in_mw && /window_count:/{gsub("\r",""); print $2; exit}' "$STATE")
    mw_max=$(awk '/^multi_window_task:/{in_mw=1; next} in_mw && /^[^ ]/{in_mw=0} in_mw && /max_windows:/{gsub("\r",""); print $2; exit}' "$STATE")
fi

if [ "$mw_active" = "true" ] && [ "$mw_closing" != "true" ]; then
    printf '<session-start-briefing scope="multi-window-intermediate">\n'
    printf 'MULTI-WINDOW TASK INTERMEDIATE (window %s/%s).\n' "$mw_count" "$mw_max"
    printf 'Methodology re-injection SKIPPED per multi_window_tolerance_policy.\n'
    printf 'Continue from prior window state. Build green required before next window.\n'
    printf '</session-start-briefing>\n'
    exit 0
fi

emit_file() {
    local label="$1" path="$2"
    printf '\n----- BEGIN %s (%s) -----\n' "$label" "$path"
    if [ -f "$path" ]; then
        cat "$path"
    else
        printf '(missing: %s)\n' "$path"
    fi
    printf '\n----- END %s -----\n' "$label"
}

printf '<session-start-briefing enforcement="MANDATORY">\n'
printf '\n=== PHYS-AGENTIC-LOOP INFRA (source of truth: %s) ===\n' "$PAL_ROOT"

emit_file "INDEX.md"                             "$PAL_ROOT/INDEX.md"
emit_file "alignment.md"                         "$PAL_ROOT/alignment.md"
emit_file "_common/markers.md"                   "$PAL_ROOT/_common/markers.md"
emit_file "_common/note_discipline.md"           "$PAL_ROOT/_common/note_discipline.md"
emit_file "_common/progress_principles.md"       "$PAL_ROOT/_common/progress_principles.md"
emit_file "_common/agentic_lean_contract.md"     "$PAL_ROOT/_common/agentic_lean_contract.md"
emit_file "notes/agentic_lean_state_template.md" "$PAL_ROOT/notes/agentic_lean_state_template.md"
emit_file "notes/ralph_loop_local_template.md"   "$PAL_ROOT/notes/ralph_loop_local_template.md"

# Local ralph-loop state (if present in this repo).
if [ -f "$REPO_ROOT/.claude/ralph-loop.local.md" ]; then
    printf '\n----- BEGIN local ralph-loop state -----\n'
    emit_file "ralph-loop.local.md"              "$REPO_ROOT/.claude/ralph-loop.local.md"
    printf '\n----- END local ralph-loop state -----\n'
fi

printf '\n=== END PHYS-AGENTIC-LOOP INFRA ===\n'
printf '</session-start-briefing>\n'
