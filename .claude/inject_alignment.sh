#!/usr/bin/env bash
# inject_alignment.sh — UserPromptSubmit hook for alignment-protocol injection.
#
# **MULTI-WINDOW TOLERANCE (iter 304):** If `ralph-loop.local.md` indicates
# an active multi-window task with `closing: false` (intermediate window),
# this hook emits NOTHING. The FINAL window (`closing: true`) gets full
# alignment-protocol injection.

set -u

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || printf '%s' "$(cd "$(dirname "$0")/.." && pwd)")"
STATE="$REPO_ROOT/.claude/ralph-loop.local.md"

# Auto-detect alignment.md location (standalone methodology repo vs nested in consumer).
if [ -f "$REPO_ROOT/alignment.md" ]; then
    ALIGN="$REPO_ROOT/alignment.md"
else
    ALIGN="$REPO_ROOT/phys-agentic-loop/alignment.md"
fi

mw_active=""
mw_closing=""
if [ -f "$STATE" ]; then
    mw_active=$(awk '/^multi_window_task:/{in_mw=1; next} in_mw && /^[^ ]/{in_mw=0} in_mw && /active:/{gsub("\r",""); print $2; exit}' "$STATE")
    mw_closing=$(awk '/^multi_window_task:/{in_mw=1; next} in_mw && /^[^ ]/{in_mw=0} in_mw && /closing:/{gsub("\r",""); print $2; exit}' "$STATE")
fi

if [ "$mw_active" = "true" ] && [ "$mw_closing" != "true" ]; then
    exit 0
fi

printf '<alignment-protocol enforcement="MANDATORY" scope="this-turn-and-subagents">\n'
printf 'The following protocol is BINDING operational rules, not reference material. Apply every rule at the moment its trigger condition fires. Do not merely acknowledge.\n\n'
printf 'Non-negotiable rules:\n'
printf '1. No completion claim without pasted verification output (TRF-R).\n'
printf '2. No untyped scientific claim: every result needs context, claim type, evidence modality, and verifier/kernel status.\n'
printf '3. No failure attribution without tool-verified evidence (fact-driven).\n'
printf '4. No surrender before the five-step universal methodology (五步纪律) is complete.\n'
printf '5. No parameter-tweak loops: three cycles of the same idea auto-escalates L0 → L4.\n'
printf '6. When spawning any sub-agent, inject the full protocol file into its prompt.\n'
printf '7. Stall ≥30 min → L3+ 揪头条 (7 项检查清单) with 30-min cap.\n'
printf '8. Source-artifact discipline: tex into ref-paper/, code into ref-code/.\n'
printf '9. Infra-injection contract: inject_infra.sh on SessionStart, inject_alignment.sh on UserPromptSubmit, ralph_stop_guard.sh on Stop.\n'
printf '10. Multi-window tolerance: when `multi_window_task.active=true` and `closing=false`, intermediate windows skip self-prompting and enforce-reading; only the FINAL (`closing=true`) window gets full discipline.\n\n'
printf 'On violation: stop, name the rule, correct course, proceed.\n\n'

if [ -f "$ALIGN" ]; then
    cat "$ALIGN"
fi

printf '\n</alignment-protocol>\n'
