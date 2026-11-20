# Disputed finding walkthrough: case 06 (Use the new delivery queue)

## What the reviewers said
Greptile and Proofline both flagged case 06 only as a documentation problem:
README still tells operators to run `work --queue reports` while new jobs go to
`report-dispatch`. Greptile added that operators should also drain `reports`
for existing jobs. Both scored PARTIAL under the frozen rubric (right problem,
imprecise location: README, not the change itself).

## The seeded defect (EXPECTED.md)
`DELIVERY_QUEUE` changes `reports` -> `report-dispatch` with no migration or
backfill. Existing pending rows keep `queue = 'reports'`, so a worker draining
only `report-dispatch` never picks them up.

## Reproduction (starter repo, commit 79d0377 + cases/06/change.patch)
1. `python3 console.py --db c06.db schedule "Weekly orders" 1700000100`
   -> summary: {"delivered": 0, "pending": 1}  (row pending in queue `reports`)
2. apply cases/06/change.patch (DELIVERY_QUEUE = "report-dispatch")
3. `python3 console.py --db c06.db work --queue report-dispatch --now 1700000101`
   -> 0 delivered; summary still {"delivered": 0, "pending": 1}
   CONFIRMED: the pre-existing pending row is stranded for the new queue.
4. `python3 console.py --db c06.db schedule "Daily stock" 1700000100`
   `python3 console.py --db c06.db work --queue reports --now 1700000102`
   -> delivered 1 (the old row), pending 1 (the NEW job)
   CONFIRMED in reverse: the README command now misses every newly scheduled job.

## Snapshot context [synthetic]
cases/06/evidence.md: site elm subscribes only to `reports`; site cedar to both.
At elm, all 8 jobs due in the cutover window would never run. Label: case
snapshot (synthetic), not a live deployment.

## Verdict
Real bug, reproducible in both directions. The providers' doc-drift finding
describes the operator-facing half and Greptile's advice (also drain the old
queue) covers the stranded rows as a workaround, but neither identifies that
the change itself strands pending data and needs a migration or backfill.
PARTIAL stands for both providers. This is also the run's honest limitation:
on the one case needing data-thinking beyond the diff, both tools reached for
the nearest file (README) instead.
