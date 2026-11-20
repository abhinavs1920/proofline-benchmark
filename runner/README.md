# Benchmark runner tooling

Executable tooling for the 2026-11-20 clean AI-reviewer benchmark run. This is
the authored deliverable for the review-ready PR: the collection was performed
against the providers' consoles/web UIs (see RERUN.md), and this package makes
the scoring step deterministic, re-runnable and verifiable from the stored raw
outputs.

## Layout
- `state.json` - one record per (provider, case): completed / quota_stop /
  not_applicable, plus the raw output file for each provider. quota_stop and
  not_applicable are statuses, not scores, per SCORING rules (a provider that
  never reviewed is not punished with a 0).
- `expected.json` - per-case expected outcome kinds, derived from the public
  starter's case evidence (prooflinedev/ai-review-benchmarks cases/0N,
  attributed). Answer-bearing data lives only in this private repo, never in
  any provider-visible repo.
- `score.py` - deterministic classifier: parses each provider's raw output
  (Greptile review body Findings section; Proofline console state / GitHub
  comment stub; CodeRabbit quota warning text) and maps it against the expected
  kind to the labels used in the scored matrix.
- `out/scores.computed.json` - the emitted table.

## Run
From the repository root:
    python3 runner/score.py            # recompute runner/out/scores.computed.json
    python3 runner/score.py --verify   # also assert equality with runs/2026-11-20-clean/scores.json

## Idempotency and verification evidence
- Recomputes only from stored raw outputs; never re-contacts providers, so a
  rerun cannot disturb completed (provider, case) pairs. quota_stop and
  not_applicable pairs are carried through untouched.
- Executed 2026-11-20 on the committed artifacts: `--verify` PASS on all
  8 cases x 4 providers (32 pairs), and two consecutive runs produced a
  byte-identical out file (sha256 stable).
- Case 06 is labeled PARTIAL by rule, not by hand: the kind
  real_defect_partial encodes that doc/drift-framed findings on that case have
  valid-but-partial scope; the reproduction is
  runs/2026-11-20-clean/disputed-case-06.md.

## Attribution
App code, case diffs, PR titles/bodies and case evidence come from
prooflinedev/ai-review-benchmarks (Proofline's public assignment starter).
This runner, the state/expected data files, the scoring rules and the
evaluation docs are authored for the benchmark exercise.
