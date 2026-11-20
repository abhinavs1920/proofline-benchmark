#!/usr/bin/env python3
"""Deterministic scorer for the 2026-11-20 clean AI-reviewer benchmark run.

Reads stored raw provider outputs (runs/2026-11-20-clean/*.json) plus
runner/expected.json (per-case expected outcome kinds, attributed to the
public starter's case evidence) and emits the per-case outcome labels.

Idempotent: it recomputes only from stored raw outputs; it never re-collects
from providers. Re-running it on unchanged inputs reproduces the same table.
--verify compares computed labels against the committed scored matrix
(runs/2026-11-20-clean/scores.json) and exits non-zero on any mismatch.

Usage:  python3 runner/score.py [--verify]
Run from the repository root.
"""
import json, re, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load(p):
    with open(os.path.join(ROOT, p)) as f:
        return json.load(f)

def greptile_finding(comment):
    # A scored finding exists when the review body has a Findings section with
    # at least one collapsed finding marker; summary-only "safe to merge"
    # reviews count as quiet.
    if not comment:
        return False
    return ("Findings\n" in comment) and ("▶" in comment)

def proofline_finding(entry):
    state = (entry.get("console_state") or "").lower()
    gh = entry.get("github_comment")
    if "no findings" in state:
        return False
    if gh and isinstance(gh, dict) and re.search(r"\b[1-9]\d* finding", gh.get("txt", "")):
        return True
    text = entry.get("console_page_text") or ""
    return bool(re.search(r"[1-9]\d* (warning|finding)s? to address", text))

def coderabbit_quota(entry):
    return any("Review limit reached" in (it.get("x") or "") for it in entry.get("items", []))

def label(kind, finding):
    if kind == "real_defect":
        return "CORRECT" if finding else "MISSED"
    if kind == "clean":
        return "FALSE_POSITIVE" if finding else "quiet (correct)"
    if kind == "allowed_quiet":
        return "finding (context)" if finding else "quiet (allowed)"
    if kind == "real_defect_partial":
        # doc/drift-framed finding on the queue case: valid but partial scope
        return "PARTIAL (doc framing)" if finding else "MISSED"
    raise ValueError(kind)

def main():
    expected = load("runner/expected.json")["cases"]
    state = load("runner/state.json")
    raw = {p: load(path) for p, path in state["raw"].items()}
    out = {}
    for case, meta in expected.items():
        kind = meta["kind"]
        row = {}
        for provider, status in state["pairs"].items():
            s = status[case]
            if s == "quota_stop":
                row[provider] = "quota_stop"
                continue
            if s == "not_applicable":
                row[provider] = "not_applicable"
                continue
            if provider == "greptile":
                e = next(x for x in raw["greptile"] if x["case"] == case)
                f = greptile_finding(e.get("comment") or "")
            elif provider == "proofline":
                e = next(x for x in raw["proofline"] if x["case"] == case)
                f = proofline_finding(e)
            else:
                continue
            row[provider] = label(kind, f)
        out[case] = row

    with open(os.path.join(ROOT, "runner/out/scores.computed.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    for case in sorted(out):
        print(case, out[case])

    if "--verify" in sys.argv:
        committed = load("runs/2026-11-20-clean/scores.json")["cases"]
        base = lambda s: s.split(" (")[0].strip()
        ok = True
        for case, row in out.items():
            for provider, computed in row.items():
                ref = committed[case].get(provider, "")
                if computed in ("quota_stop", "not_applicable"):
                    continue  # statuses, not scores; asserted in state.json
                if base(ref) != base(computed):
                    print(f"MISMATCH {case}/{provider}: computed={computed!r} committed={ref!r}")
                    ok = False
        print("VERIFY", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
