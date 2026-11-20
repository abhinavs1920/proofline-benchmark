# Expected findings (answer key)

Written before the first provider run, from the frozen case patches and the application guide. Graders may add unanticipated valid findings during scoring; removals need a recorded reason.

Source facts used below come from the case patches and `docs/report-service.md` unless marked [snapshot] (synthetic two-site records supplied with cases 04-06).

## Case 01 - Page report history by scheduled time

- **Real defect:** the cursor predicate changed to `WHERE scheduled_at < ?` while ordering is `scheduled_at DESC, id DESC`. The application guide states schedulers can enqueue multiple reports for the same second, so rows sharing the cursor's `scheduled_at` are silently skipped across pages. The cursor must include the id tiebreak (e.g. `scheduled_at < ? OR (scheduled_at = ? AND id < ?)`).

## Case 02 - Stream the report export

- **Real defect:** the change drops `csv.writer` for a manual `",".join`, removing CSV escaping. A report name containing a comma, quote or newline corrupts the export columns; the guide promises a CSV header plus one record per delivery.

## Case 03 - Batch queued deliveries

- **Real defect:** `range(0, len(jobs) - batch_size + 1, batch_size)` never processes the remainder. With 25 due jobs only 20 are delivered; with fewer than 20 due jobs none are delivered, and `processed` undercounts versus the previous `len(jobs)`.

## Case 04 - Retire the legacy delivery column

- **Expected context finding [snapshot]:** the migration drops `deliveries.legacy_format` with no accompanying code change in the patch. The supplied two-site snapshot should be used to ask whether every deployed site runs code that no longer reads the column before it is dropped. A code-only review can reasonably be quiet here; that is recorded, not punished.

## Case 05 - Increase export batch size

- **Expected clean.** Doubling `EXPORT_BATCH_SIZE` is coherent on its own. The supplied [snapshot] should be checked for downstream batch-size limits; if none, a quiet review is a good outcome.

## Case 06 - Use the new delivery queue

- **Real defect [patch + snapshot]:** `DELIVERY_QUEUE` changes from `reports` to `report-dispatch` with no migration or backfill. Existing pending rows keep `queue = 'reports'`, so the worker draining `report-dispatch` never picks them up; the snapshot's pending deliveries in the old queue demonstrate the stranding.

## Case 07 - Index pending deliveries

- **Expected clean.** The partial index `(queue, scheduled_at, id) WHERE delivered_at IS NULL` matches the `deliver_due` predicate and ordering.

## Case 08 - Include a total in the activity summary

- **Expected clean.** `total = sent + waiting` equals `count(*)` given how `sent` and `waiting` are computed.
