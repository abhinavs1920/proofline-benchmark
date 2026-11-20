# Proofline org run, 2026-11-20

## What this is
The brief's step 2 ("install Proofline on your own GitHub organization and run a
real review") executed literally: ProoflineDev installed on the impact-gate
GitHub organization, scoped to exactly one private repo, with three
representative benchmark case PRs reviewed. This directory is separate from the
scored 8-case clean run (../2026-11-20-clean/); outcomes here are representative
re-reviews, not part of the scored matrix.

## Scope and terms (verified live 2026-11-20 ~17:40 IST)
- GitHub App install: ProoflineDev on org impact-gate, installation 184014625,
  "Only select repositories" = impact-gate/proofline-benchmark (private). No
  other org repo exposed. Permissions shown on screen: read actions,
  attestations api, members, merge queues, metadata; read+write checks, code,
  deployments, issues, pull requests (all scoped to the selected repo).
- Billing (proofline.sh org settings): "Free review month - hosted pull-request
  reviews are covered until December 20, 2026. 0 review credits used." Auto
  top-up OFF (no saved card). No payment method on the org.
- Repo content: app code + case branches from prooflinedev/ai-review-benchmarks
  (Proofline's public assignment starter), per the repo description. No answer
  keys, scores, or methodology in the provider-visible repo or its history.

## Reviews (org: impact-gate, repo: proofline-benchmark)
- PR #1 "Page report history by scheduled time" (case 01, seeded bug):
  1 finding - pagination cursor keeps only scheduled_at, so rows sharing a
  timestamp can be skipped at a page boundary (Logic, reports.py:45).
  Matches the personal-run CORRECT outcome for case 01.
  Review: https://proofline.sh/orgs/github/impact-gate/reviews/pr/proofline-benchmark/1/runs/1
- PR #2 "Increase export batch size" (case 05, clean): no findings.
  Matches the personal-run correct-clean outcome for case 05.
  Review: https://proofline.sh/orgs/github/impact-gate/reviews/pr/proofline-benchmark/2/runs/1
- PR #3 "Use the new delivery queue" (case 06, disputed): 1 finding - README
  still documents the old queue command while scheduled jobs now go to the new
  dispatch queue, and delivery requires an exact queue match (Doc drift,
  reports.py:9). Same finding shape as the personal run.
  Review: https://proofline.sh/orgs/github/impact-gate/reviews/pr/proofline-benchmark/3/runs/1

## Evaluation and disagreement (step 2's "what you changed or disagreed with")
- Cases 01 and 05: agree with Proofline's outcomes; consistent with the scored
  clean run (diff-identical case code, same finding pattern).
- Case 06: the documented disagreement stands, reproduced in
  ../2026-11-20-clean/disputed-case-06.md. Summary of the reproduction: the
  README command Proofline flags does miss new-queue jobs (finding is valid as
  far as it goes), but the more severe effect is already-scheduled rows stranded
  on the old queue (delivery requires exact queue match, so they never run),
  which the doc-drift framing does not capture. Verdict on the finding: valid
  but partial; scored PARTIAL in the clean run.
- Trigger note: the three PRs were opened before the app install, so Proofline
  did not auto-review them; each PR was closed and reopened once to fire the
  pull_request event. Reviews then completed in about 1 minute each and were
  published as GitHub PR comments inside the private repo.

## Provenance and authorship
- Case code: upstream starter (prooflinedev/ai-review-benchmarks), attributed
  in the repo description; PR titles/bodies are the starter's frozen texts.
- Authored by Abhinav: benchmark design, repo setup, PR orchestration, scoring
  rules, raw-output collection, the case-06 reproduction, and this evaluation.
- No synthetic UI was built and no Impact Gate product code was accessed or
  copied for this run.
