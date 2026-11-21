# Benchmark runner tooling

Executable tooling for the 2026-11-20 clean AI-reviewer benchmark run. The
collection was performed against the providers' consoles/web UIs (see
RERUN.md); this package makes the scoring step deterministic, re-runnable and
evidence-grounded from the stored raw outputs.

## Layout
- `state.json` - one record per (provider, case): completed / quota_stop /
  not_applicable, plus the raw output file for each provider. quota_stop and
  not_applicable are statuses, not scores, per SCORING rules (a provider that
  never reviewed is not punished with a 0).
- `expected.json` - per-case expected outcome kinds plus mechanism_terms,
  derived from the public starter's case evidence
  (prooflinedev/ai-review-benchmarks cases/0N, attributed). Answer-bearing
  data is recorded here for auditability. The added-case private answer-key file was not pushed. This working repository had pre-existing CodeRabbit all-repositories access, so universal provider isolation is not claimed; see REPORT.md.
- `score.py` - deterministic classifier. It parses each provider's raw output
  (Greptile review-body Findings section; Proofline console state, GitHub
  comment stub and console warning body; CodeRabbit quota warning text),
  checks the finding text against the case's mechanism terms, and maps the
  result against the expected kind to the scored labels.
- `test_score.py` - mutation tests proving the labels move with the raw
  evidence (see below).
- `out/scores.computed.json` - the emitted table.

## Run
From the repository root:
    python3 runner/score.py            # recompute runner/out/scores.computed.json
    python3 runner/score.py --verify   # also assert equality with runs/2026-11-20-clean/scores.json
    python3 runner/test_score.py       # 9 mutation tests

## What is automated vs manual adjudication
Automated, parsed from raw provider text:
- whether a review produced a finding at all;
- whether the finding text matches the case's seeded mechanism
  (mechanism_terms in expected.json);
- whether a case-06 finding is doc-framed (doc/README/drift/example wording),
  which the frozen rubric scores as partial;
- whether a quota_stop status is backed by the provider's quota warning text.

Manual, recorded as data and labeled as such:
- the per-case expected kinds (the answer key, attributed to the starter's
  public case evidence and the human clean-run analysis);
- the rubric rule that a doc-framed finding on case 06 is partial;
- the original human confirmation during collection that each finding matched
  the seeded defect. A real finding whose text matches no mechanism term is
  labeled FINDING (unmatched) and surfaced for human review instead of being
  silently credited CORRECT.

## Verification evidence (2026-11-20)
- `score.py --verify` PASS on all 8 cases x 4 providers (32 pairs): computed
  labels reproduce the committed runs/2026-11-20-clean/scores.json from raw
  outputs alone. Two consecutive runs produce a byte-identical out file
  (sha256 8a7a80ff...).
- `test_score.py`: 9 of 9 pass, including - removing a raw finding flips
  CORRECT to MISSED; injecting one on a clean case flips quiet to
  FALSE_POSITIVE; an off-mechanism finding is surfaced as FINDING
  (unmatched), not credited; case 06 scores CORRECT on a mechanism-framed
  finding and PARTIAL on a doc-framed one (partial is grounded in the
  finding's framing, not hardcoded to the case); quota_stop, not_applicable
  and quiet are distinct labels; a quota_stop without the provider's quota
  warning in raw is flagged QUOTA_UNVERIFIED.
- Case 06's real-data PARTIAL is grounded in both providers' actual finding
  text (Greptile: "Worker example misses new jobs"; Proofline: "Warning -
  Doc drift ... README.md still invokes the worker with --queue reports");
  the reproduction is runs/2026-11-20-clean/disputed-case-06.md.

## Attribution
App code, case diffs, PR titles/bodies and case evidence come from
prooflinedev/ai-review-benchmarks (Proofline's public assignment starter).
This runner, the state/expected data, the scoring rules, the tests and the
evaluation docs are authored for the benchmark exercise.

## Scope clarification (final report)

The executable scorer replays supported stored Greptile and Proofline artifacts for the eight supplied cases and preserves CodeRabbit quota statuses. Copilot and added/regression cases are manually adjudicated, not automatically graded by this package. The final report explains the review differences, the queue-case judgment, and the Azure VM handler run, which does not fulfill the AWS deployment requirement.
