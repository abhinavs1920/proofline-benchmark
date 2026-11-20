# Scoring rules

Frozen before any provider output is read. The commit SHA of this file pins the rules.

## Unit of observation

One attempt = (provider, case, base commit, head commit, context condition, run id). Record per attempt: trigger, plan or model when visible, settings, timestamps, terminal outcome, and the original review link. A repeated delivery of the same webhook is one attempt. An intentional re-review is marked as a repeat.

## Definitions

- **Correct finding:** identifies a real defect in the change, at the right file and line (or clearly the right location), and is reproducible or directly verifiable from the code.
- **False positive:** flags behavior that is correct in the code or already handled elsewhere in the change.
- **Missed defect:** a defect present in the change that the provider did not identify. Scored against the frozen expected-findings list plus defects agreed during grading.
- **Partial credit:** right problem, wrong line or imprecise location. Counted separately from full correct findings.
- **Unanticipated valid finding:** a real defect not on the expected list. Kept, graded on merit, marked unanticipated.
- **Style / nit comments:** recorded in a separate bucket, excluded from correctness scoring.

## Severity

No severity weights in v1. All correctness findings count equally, to keep grading unambiguous.

## Terminal outcomes that are not scores

`quota_stop`, `error`, `unattempted`, and `not_applicable` are statuses in the coverage table. They never count as a miss or a zero score. A quiet review on a correct change is a good outcome, not a failure.

## First response rule

The provider's first complete review of a pull request is the scored output. Follow-up comments, later summaries, and re-reviews triggered by new pushes are ignored unless marked as a deliberate repeat attempt.

## Context conditions

Cases 04, 05 and 06 ship optional deployment snapshots. If a snapshot is supplied to one provider, the same snapshot is supplied to every comparison partner for that case, and the choice is recorded per attempt. Every fact cited in grading is labelled by source: live deployment, case snapshot (synthetic), or case patch.

## Impact Gate applicability (predeclared)

Documented capability: Impact Gate reviews pull requests for HTTP API contract changes it can detect from OpenAPI specifications and supported-language codebases (TypeScript/JavaScript and Java extractors). A case is IG-applicable only if its patch introduces or modifies an HTTP API contract change expressible in OpenAPI within a supported language.

Declared from the frozen case patches, before any run:

- Cases 01-08 patch only a single Python application (`reports.py`) or its SQLite migrations. None introduces or modifies an HTTP API contract or an OpenAPI specification.
- Therefore all 8 cases are **not_applicable** for Impact Gate.

IG's coverage row reports all 8 as `not_applicable`. This is a scope statement, not eight misses. The shared-case ranking excludes IG because there are no shared applicable cases. A separate held-out experiment with an original contract-changing pull request (outside these eight cases) may be reported on its own and is never merged into this ranking.

## Blinding

Where practical, findings are graded with provider names hidden. Ambiguous calls get a second reading with recorded reasoning; single-grader grading is listed as a limitation.

## Runs

One run per (provider, case) unless an error forces a retry; retries are recorded. Single-run evidence is listed as a limitation.

## Pinning

Per attempt: repository, base SHA, head SHA, provider settings and plan, snapshot condition, timestamp. Raw outputs (comment URLs and JSON payloads) are stored under `runs/` and every score must trace back to a raw file.

## Isolation

Answer keys, expected findings, calibration notes and other providers' comments never enter any run repository. Run repositories contain only the application branches. No reviewer is ever installed on this working repository.
