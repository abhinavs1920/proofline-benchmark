# Clean rerun, 2026-11-20

## What this directory is
Raw outputs and scores for the scored rerun of the 8 starter cases, after the
pilot was found contaminated by CodeRabbit Free (summaries + PR-body edits on 24
pilot PRs across run-greptile, run-proofline, run-coderabbit). Pilot PRs 1-8 on
each repo are closed and preserved. Scored PRs are 9-16 on run-greptile and
run-proofline (cases 01-08 in order, base branch pilot/base).

## Files
- greptile.json - full greptile-apps review text per clean PR (url, posted_at, comment).
- proofline.json - per clean PR: GitHub comment stub (findings count), console
  review URL and page text where findings exist; zero-finding reviews are
  console-only (no GitHub comment) with console_state from the All reviews list.
- coderabbit.json - every coderabbitai item on the 16 clean PRs: one uniform
  "Review limit reached" warning per PR, no review content.
- pr-timelines.json - author census of all 16 clean PR timelines.
- diff-hashes.txt - SHA-256 of each pilot and clean .diff, 16/16 identical pairs.
- scores.json - per-case outcomes vs EXPECTED.md under SCORING.md.
- pilot-evidence-condensed.json - condensed pilot timeline scrape.

## Reproduce collection
1. Create run repos from prooflinedev/ai-review-benchmarks app-only branches
   (pilot/base + pilot/01..08); never install reviewers on a repo holding case
   catalog or answer keys.
2. If CodeRabbit is installed account-wide, commit .coderabbit.yaml with
   reviews.auto_review.enabled=false to the base branch before opening PRs.
3. Open PRs pilot/0N -> pilot/base with the frozen titles/bodies from
   cases/0N/title.txt and cases/0N/body.md.
4. Record every timeline item with author and timestamp (first complete review
   is the scored output per SCORING.md). For Proofline, also read console run
   states: zero-finding reviews post nothing to GitHub.
5. Verify diff identity against reference .diff files before scoring.
6. Score per EXPECTED.md and SCORING.md only; quota stops and not_applicable
   are coverage statuses, never zero scores.
