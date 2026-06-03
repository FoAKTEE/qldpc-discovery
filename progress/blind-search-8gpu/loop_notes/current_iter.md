# current_iter — 8-GPU blind search, iter 5 (overwrite-mode)

## Anchor
Directive: do NOT work around the crash — debug + FIX the Julia package at root cause; and make
"encounter a bug -> debug the package" a BINDING rule injected into the infra.

## Done this iter
- INJECTED `package_debug_policy` into .claude/ralph-loop.local.md (BINDING): any bug/crash/error ->
  root-cause + fix IN the package (julia/src|ext) + regression test, BEFORE proceeding; no workarounds
  (no thread-count reduction, no silent try/catch swallowing, no skipping without a fix).
- DIAGNOSED the crash (tool-verified, ruling out the easy explanations):
  - NOT a thread ceiling: -t 64 / 128 / 192 ALL complete (exit 0, DONE). 200-thread Julia runtime
    itself is fine (a no-package 200-thread busy loop completes).
  - IT IS CANDIDATE EXPOSURE: a rare degenerate code (~1 in several thousand) aborts the process
    ABRUPTLY at ~4000+ candidates. exit 1, NO Julia exception (driver top-level try/catch does NOT
    fire), --check-bounds=yes does NOT help => NOT an @inbounds OOB; a genuine SEGFAULT in a package
    routine (or a thread-safety/heavy-alloc fault) on that degenerate code.
- Launched debug Workflow wvkhs33ub: instrument -> capture the exact failing (l,m,A,B) + the package
  function -> root-cause -> fix in package + regression test in julia/test -> verify at -t 200 over
  many candidates + package tests green.

## Status
Full run GATED on the package fix (per the new policy). No frontier recorded yet (the bisection
frontiers are BP-OSD upper bounds from incomplete runs, NOT a deliverable).

## Verifier
T=64/128/192 -> DONE exit 0; -t 200 / long -> abrupt exit 1 (no exception, check-bounds no help);
minimal 200-thread busy loop -> OK. code_quality_policy_pass: R1 (diagnosis + infra policy) -> PROVEN.
Package fix + verification -> pending workflow wvkhs33ub.
