# Benchmark report: comparing AI pull-request reviewers on the same changes

Abhinav Sharma, 21 November 2026. This report, the coverage table, the rerun guide and the traced result below are the submission companion to the demo video and evaluation PDF shared through the application route.

## Final walkthrough and report

- [Narrated walkthrough (1:45)](https://drive.google.com/file/d/1q7RE-FhpJVcGwQTY6DZ47aFRZwq5a8eT/view?usp=drivesdk&authuser=abxh1920%40gmail.com)
- [Matching evaluation PDF](https://drive.google.com/file/d/1-ivt9KNATtFBT9ymNXI07WRX65l8_NOf/view?usp=drivesdk&authuser=abxh1920%40gmail.com)

Anyone with either file link can view that file. The added-case private answer key and unrelated product repositories are not part of this publication.

## What the benchmark does

One pull request per case; every provider under test reviews the same head commit of the same PR; the provider's first complete review is captured and scored against expectations recorded before the result was read. The benchmark workflow captures reviews and normalizes outcomes; runner/score.py deterministically replays the supported stored artifacts. Other provider-case outcomes are manually adjudicated. Scoring rules are frozen in [SCORING.md](SCORING.md), expected findings in [EXPECTED.md](EXPECTED.md), both committed before the first run.

## Method, briefly

Fifteen cases in three groups: the eight supplied cases (01-08), five added API-contract cases (S1-S3, P1-P2), and two seeded regressions on my own Flask service (C1, C3) proven locally with baseline-pass / changed-fail tests. Supplied-case expectations come from the assignment's seeded reference patches; added and seeded-regression expectations were written in a private answer-key file before those PRs were opened. Added-case answer keys were kept in a separate private file. The working-repository access exception is disclosed under Isolation and scorer scope below. The diffs behind the supplied-case PRs are SHA-256 identical across the pilot and both rerun repositories (16/16 pairs, [runs/2026-11-20-clean/diff-hashes.txt](runs/2026-11-20-clean/diff-hashes.txt)), so every provider reviewed byte-identical changes.

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

Counts, unaggregated by design: on the four defect cases, each of Greptile, Copilot Lite and Proofline scored 3 CORRECT + 1 PARTIAL. All three stayed quiet on the three clean controls and the context-only case; no false positives from any provider. The evaluation PDF lists case PRs and the external-check review; raw outputs and per-case scores are in [runs/2026-11-20-clean/](runs/2026-11-20-clean) (`greptile.json`, `proofline.json`, `coderabbit.json`, `pr-timelines.json`, `scores.json`).

On the five added cases, all three providers detected every seeded defect with the correct breakage mechanism and caller-level evidence (hermes #20-22, proofline-demo-backend #1-2). On the two seeded regressions, Copilot Lite and Proofline each identified the exact seeded failure; Greptile's findings landed on both PRs. Differences were depth and packaging: severity levels, confidence scores, stale-documentation warnings, suggested changesets.

## Rerun instructions

[runs/2026-11-20-clean/RERUN.md](runs/2026-11-20-clean/RERUN.md) is the full guide. The load-bearing rules I actually operated by: review runs use isolated app-only repositories; the pre-existing CodeRabbit working-repo access exception is disclosed below; PRs are opened from frozen titles and bodies; every timeline item is recorded with author and timestamp, and the first complete review is the scored output; diff identity is hash-verified before scoring; quota stops and errors are coverage statuses, never zero scores.

## One traced result: case 06

All three providers flagged case 06 primarily as an operator/documentation issue: Greptile as a documentation fix, Proofline as documentation drift, Copilot Lite as an operator-invocation concern. The seeded defect is that `DELIVERY_QUEUE` changes from `reports` to `report-dispatch` with no migration, so rows already pending in `reports` are never picked up by a worker draining only `report-dispatch`. I reproduced it in both directions on the starter's own CLI: a row scheduled before the change stays pending after a `report-dispatch` work run, and the old queue command later delivers the stale row while missing every newly scheduled job. All three mention retaining the old worker for legacy jobs. Verdict: real bug; the findings offer useful operator advice, but do not explicitly require migration/backfill or a deliberate cutover as a property of the change. The frozen rubric therefore retains PARTIAL for all three. Full walkthrough: [runs/2026-11-20-clean/disputed-case-06.md](runs/2026-11-20-clean/disputed-case-06.md).

## Systems trace

The starter report-service handler ran on an existing Azure Linux VM on 21 November, 18:18-18:19 IST, using starter commit `79d03777827b88aa23ee9309ebefab5f9766cd09`. A small stand-in replaced the Azure Functions binding. Result: HANDLER OK, delivered 1, pending 0, receipt_at 101. Source hashes were checked and the temporary folder was removed. This was a handler run on a VM, not an AWS Lambda or Azure Functions deployment. The AWS-specific deployment requirement is not fulfilled by this run.

## What differs when detection agrees

On pagination (case 01), Greptile gives a concrete three-row/limit-two example, recommends retaining scheduled_at and id in the cursor, and adds a supporting-index suggestion. Proofline explains the ORDER BY/cursor mismatch, gives a two-row/limit-one counterexample, and recommends a matching lexicographic continuation predicate. Copilot Lite identifies the missing secondary id key in a more concise changes-recommended summary. These are differences in explanation and suggested action, not a difference in detecting the seeded defect; all remain CORRECT. The extra index suggestion was not a separately seeded detection credit.

On the queue rename (case 06), Greptile calls the code safe to merge with a non-blocking documentation update. Proofline explains that following the README delivers zero new jobs. Copilot Lite includes equivalent deployment configuration in its proposed operator fix. All three mention keeping/draining the old queue for legacy rows. The rubric distinguishes that useful operational workaround from an explicit diagnosis that the change requires a migration/backfill or deliberate cutover for already-pending data. PARTIAL reflects that narrower framing, not an absence of all legacy-job advice. A deliberate two-queue cutover and a regression test for already-pending work are the benchmark author's recommendations, not changes claimed to have been implemented.

Sources: https://github.com/abhinavs1920/run-greptile/pull/9 and https://github.com/abhinavs1920/run-greptile/pull/14 .

## Isolation and scorer scope

The separate private added-case answer-key file was not pushed to review repositories. However, the working repository was not invisible to every provider: CodeRabbit had a pre-existing account-level all-repositories installation and later edited PR #1 with a generated summary. As recorded in that PR, the scored clean and organization runs were frozen before the first evidenced CodeRabbit content access; CodeRabbit produced quota warnings, not scored review content. Structural access existed from repository creation. Retention and cross-repository learning cannot be verified, so strict universal isolation is not claimed.

The deterministic scorer in runner/score.py covers the supported stored Greptile and Proofline outputs for the eight supplied cases, with CodeRabbit quota statuses separate. It is not an automatic grader for every cell of the full fifteen-case, three-provider comparison. Copilot and the added/regression outcomes are manually adjudicated from the captured evidence. Mechanism-term checks supplement, rather than replace, semantic judgment.

## One limitation that could change the conclusion

Exposure history. The eight supplied cases predate the first historical reviews on the per-tool run repositories, so a provider that learns across repositories could have seen these changes before the same-head rerun. I controlled what was controllable (fresh repos, frozen inputs, hash-verified diffs, first-response scoring), and the same-head rerun improves comparability, but it does not erase that earlier exposure. Combined with the small sample (15 cases, single runs), this is a fair-protocol snapshot, not a leaderboard.

## External real-repo check (reported separately)

One external validation case outside the 15-case corpus: a real upstream bug, not a seeded fixture. In the abhinavs1920/strapi fork I reverted only the controller hunk of strapi/strapi#28719 ("string populate on stage reads returns a 500 error", merged 19 Nov 2026) and opened it as a neutrally framed PR: <https://github.com/abhinavs1920/strapi/pull/1>. Ground truth comes from the upstream project itself: its controller tests pass 16/16 on develop and fail 10/16 on the case branch, the failures being exactly the populate tests the fix added. With the expectation recorded before the PR was opened, one approved Copilot Lite review identified the exact defect and mechanism in its first complete review (107 seconds after the request): the raw query-string populate reaches the database query builder untransformed and throws on `?populate=*` instead of returning stages. CORRECT. Review: <https://github.com/abhinavs1920/strapi/pull/1#pullrequestreview-6002461674>. Single-provider, single-case check; not counted in the coverage table or denominators above.
