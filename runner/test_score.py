#!/usr/bin/env python3
"""Mutation tests for runner/score.py.

Proves the scorer's labels move with the raw evidence rather than restating
stored answers: each test mutates a copy of the raw artifacts and asserts
the label changes the way the rubric says it should. Run from the repo root:
    python3 runner/test_score.py
"""
import copy, json, os, sys, unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fresh():
    return score.load_artifacts(ROOT)


def case_entry(raw, provider, case):
    return next(x for x in raw[provider] if x.get("case") == case)


class BaselineTest(unittest.TestCase):
    def test_baseline_matches_committed_matrix(self):
        raw, expected, state = fresh()
        out = score.compute_scores(raw, expected, state)
        committed = score.load("runs/2026-11-20-clean/scores.json", ROOT)["cases"]
        base = lambda s: s.split(" (")[0].strip()
        for case, row in out.items():
            for provider, computed in row.items():
                if computed in ("quota_stop", "not_applicable"):
                    continue
                self.assertEqual(base(computed), base(committed[case][provider]),
                                 f"{case}/{provider}")


class FindingRemovedTest(unittest.TestCase):
    def test_removing_finding_flips_correct_to_missed(self):
        raw, expected, state = fresh()
        case_entry(raw, "greptile", "01")["comment"] = "Confidence Score: 5/5\n\nThe code appears safe to merge."
        out = score.compute_scores(raw, expected, state)
        self.assertEqual(out["01"]["greptile"], "MISSED")
        self.assertEqual(out["01"]["proofline"], "CORRECT")  # other provider untouched

    def test_weakening_finding_off_mechanism_is_surfaced_not_credited(self):
        raw, expected, state = fresh()
        e = case_entry(raw, "greptile", "02")
        e["comment"] = e["comment"].replace("Report names break CSV output", "Consider adding more tests")
        out = score.compute_scores(raw, expected, state)
        self.assertEqual(out["02"]["greptile"], "FINDING (unmatched)")


class FalsePositiveTest(unittest.TestCase):
    def test_injected_finding_on_clean_case_is_false_positive(self):
        raw, expected, state = fresh()
        e = case_entry(raw, "greptile", "05")
        e["comment"] = "Confidence Score: 3/5\n\nFindings\n Batch size may overflow ▶\nSummary\nIncreased the export batch size."
        out = score.compute_scores(raw, expected, state)
        self.assertEqual(out["05"]["greptile"], "FALSE_POSITIVE")
        self.assertEqual(out["05"]["proofline"], "quiet (correct)")


class PartialGroundingTest(unittest.TestCase):
    """Case 06: partial must come from the finding's doc framing, not from the
    case number. A mechanism-framed finding scores CORRECT; a doc-framed one
    scores PARTIAL; none scores MISSED."""

    def _with_comment(self, text):
        raw, expected, state = fresh()
        case_entry(raw, "greptile", "06")["comment"] = "Confidence Score: 4/5\n\nFindings\n " + text + " ▶\nSummary\nUses the new delivery queue."
        return score.compute_scores(raw, expected, state)["06"]["greptile"]

    def test_mechanism_framed_finding_scores_correct(self):
        self.assertEqual(self._with_comment("Pending deliveries stranded in the old queue"), "CORRECT")

    def test_doc_framed_finding_scores_partial(self):
        self.assertEqual(self._with_comment("Worker example misses new jobs"), "PARTIAL (doc framing)")

    def test_no_finding_scores_missed(self):
        raw, expected, state = fresh()
        case_entry(raw, "greptile", "06")["comment"] = "The code appears safe to merge."
        self.assertEqual(score.compute_scores(raw, expected, state)["06"]["greptile"], "MISSED")


class StatusDistinctnessTest(unittest.TestCase):
    def test_quota_notapplicable_quiet_are_distinct(self):
        raw, expected, state = fresh()
        row = score.compute_scores(raw, expected, state)["05"]
        self.assertEqual(row["greptile"], "quiet (correct)")
        self.assertEqual(row["coderabbit"], "quota_stop")
        self.assertEqual(row["impact_gate"], "not_applicable")
        self.assertEqual(len({row["greptile"], row["coderabbit"], row["impact_gate"]}), 3)

    def test_quota_stop_requires_quota_text_in_raw(self):
        raw, expected, state = fresh()
        for e in raw["coderabbit"]:
            for it in e["items"]:
                it["x"] = it["x"].replace("Review limit reached", "All good")
        out = score.compute_scores(raw, expected, state)
        self.assertEqual(out["05"]["coderabbit"], "QUOTA_UNVERIFIED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
