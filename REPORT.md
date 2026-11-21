# Benchmark report: comparing AI pull-request reviewers on the same changes

Abhinav Sharma, 21 November 2026. This report, the coverage table, the rerun guide and the traced result below are the submission companion to the demo video and evaluation PDF shared through the application route.

## What the benchmark does

One pull request per case; every provider under test reviews the same head commit of the same PR; the provider's first complete review is captured and scored against expectations recorded before the result was read. The runner tooling in this branch collects reviews, normalizes outcomes and scores them deterministically. Scoring rules are frozen in [SCORING.md](SCORING.md), expected findings in [EXPECTED.md](EXPECTED.md), both committed before the first run.

## Method, briefly

Fifteen cases in three groups: the eight supplied cases (01-08), five added API-contract cases (S1-S3, P1-P2), and two seeded regressions on my own Flask service (C1, C3) proven locally with baseline-pass / changed-fail tests. Supplied-case expectations come from the assignment's seeded reference patches; added and seeded-regression expectations were written in a private answer-key file before those PRs were opened. The answer key lives outside every provider-visible repository. The diffs behind the supplied-case PRs are SHA-256 identical across the pilot and both rerun repositories (16/16 pairs, [runs/2026-11-20-clean/diff-hashes.txt](runs/2026-11-20-clean/diff-hashes.txt)), so every provider reviewed byte-identical changes.

Outcomes: CORRECT (defect and mechanism identified), PARTIAL (right area, imprecise), MISS (completed review, no relevant finding), NO-RUN (never executed; never a score). Quiet on a clean change counts as correct; case 04 is context-only, so quiet is allowed there. A warning alone is not CORRECT: the finding must identify the actual failure.

## Coverage

Results as of 00:40 IST, 21 Nov, with every scheduled review completed.

| Provider | Supplied cases 01-08 | Added S1-S3, P1-P2 | Seeded regressions C1, C3 |
| --- | --- | --- | --- |
| Greptile | 8/8 complete | 5/5 complete | 2/2 complete |
| GitHub Copilot (Lite) | 8/8 complete | 5/5 complete | 2/2 complete |
| Proofline (same-PR run) | 8/8 complete | 5/5 complete | 2/2 complete |
| Proofline (historical, pre-rerun repos) | 8/8 complete; kept separate, never merged into same-PR cells | n/a | n/a |
| CodeRabbit | 8/8 attempted, stopped by plan limit (uniform "Review limit reached", no review content) | stopped by plan limit | not attempted |

Denominators: 3 providers with completed same-head reviews, 15 distinct cases, 45 completed same-head provider-case pairs, plus 8 repeated pairs from the historical Proofline run reported separately. The contaminated pilot (one provider edited PR bodies) was closed and fully rerun before scoring.

## Results on the eight supplied cases (same PR, same head)

| Case | Seeded situation | Greptile | Copilot Lite | Proofline (same-PR) |
| --- | --- | --- | --- | --- |
| 01 Page history: cursor drops the id tiebreak | defect | CORRECT | CORRECT | CORRECT |
| 02 Stream export: CSV escaping dropped | defect | CORRECT | CORRECT | CORRECT |
| 03 Batch deliveries: loop drops the remainder | defect | CORRECT | CORRECT | CORRECT |
| 04 Retire legacy column | context-only | quiet (allowed) | quiet (allowed) | quiet (allowed) |
| 05 Increase batch size | clean | quiet (correct) | quiet (correct) | quiet (correct) |
| 06 New delivery queue: pending rows stranded | defect | PARTIAL (doc-fix) | PARTIAL (operator-invocation) | PARTIAL (doc-drift) |
| 07 Index pending | clean | quiet (correct) | quiet (correct) | quiet (correct) |
| 08 Activity total | clean | quiet (correct) | quiet (correct) | quiet (correct) |

Counts, unaggregated by design: on the four defect cases, each of Greptile, Copilot Lite and Proofline scored 3 CORRECT + 1 PARTIAL. All three stayed quiet on the three clean controls and the context-only case; no false positives from any provider. Every cell links to its PR and review in the evaluation PDF; raw outputs and per-case scores are in [runs/2026-11-20-clean/](runs/2026-11-20-clean) (`greptile.json`, `proofline.json`, `coderabbit.json`, `pr-timelines.json`, `scores.json`).

On the five added cases, all three providers detected every seeded defect with the correct breakage mechanism and caller-level evidence (hermes #20-22, proofline-demo-backend #1-2). On the two seeded regressions, Copilot Lite and Proofline each identified the exact seeded failure; Greptile's findings landed on both PRs. Differences were depth and packaging: severity levels, confidence scores, stale-documentation warnings, suggested changesets.

## Rerun instructions

[runs/2026-11-20-clean/RERUN.md](runs/2026-11-20-clean/RERUN.md) is the full guide. The load-bearing rules I actually operated by: reviewers are only ever installed on app-only run repositories, never on this working repo; PRs are opened from frozen titles and bodies; every timeline item is recorded with author and timestamp, and the first complete review is the scored output; diff identity is hash-verified before scoring; quota stops and errors are coverage statuses, never zero scores.

## One traced result: case 06

All three providers flagged case 06 without identifying the seeded data-level defect: Greptile as a documentation fix, Proofline as documentation drift, Copilot Lite as an operator-invocation concern. The seeded defect is that `DELIVERY_QUEUE` changes from `reports` to `report-dispatch` with no migration, so rows already pending in `reports` are never picked up by a worker draining only `report-dispatch`. I reproduced it in both directions on the starter's own CLI: a row scheduled before the change stays pending after a `report-dispatch` work run, and the old queue command later delivers the stale row while missing every newly scheduled job. Verdict: real bug; every provider reached the operator-facing half, none identified that the change itself strands pending data. PARTIAL stands for all three. Full walkthrough: [runs/2026-11-20-clean/disputed-case-06.md](runs/2026-11-20-clean/disputed-case-06.md).

## Systems trace (commit -> CI -> AWS -> verified invocation)

- Commit and PR: the `benchmark-runner` branch, PR #1 in this repository.
- CI: the starter's PR checks ran green on PR open and on the latest synchronize; evidence at the PR checks page: <https://github.com/abhinavs1920/proofline-benchmark/pull/1/checks>.
- Local deployment smoke: PASS (commit 79d0377).
- AWS deployment and verified invocation: **not completed as of 08:15 IST, 21 Nov** (console sign-in waiting on my MFA step). No claim is made on that leg. The intended path is the starter's OIDC workflow (.github/workflows/aws.yml, no stored keys): deploy a known revision, verify the delivered report, save the workflow link and receipt, delete the stack. This section gets updated with the run link and receipt when it completes.

## One limitation that could change the conclusion

Exposure history. The eight supplied cases predate the first historical reviews on the per-tool run repositories, so a provider that learns across repositories could have seen these changes before the same-head rerun. I controlled what was controllable (fresh repos, frozen inputs, hash-verified diffs, first-response scoring), and the same-head rerun improves comparability, but it does not erase that earlier exposure. Combined with the small sample (15 cases, single runs), this is a fair-protocol snapshot, not a leaderboard.
