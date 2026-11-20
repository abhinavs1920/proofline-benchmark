#!/usr/bin/env python3
"""Deterministic scorer for the 2026-11-20 clean AI-reviewer benchmark run.

Reads stored raw provider outputs (runs/2026-11-20-clean/*.json) plus
runner/expected.json and emits per-case outcome labels.

What is automated here (parsed from raw provider text):
  - whether a provider produced a review finding at all (Greptile Findings
    section; Proofline console state / GitHub comment stub);
  - whether the finding text is grounded in the case's seeded mechanism
    (per-case mechanism_terms, from the starter's public case evidence);
  - whether a case-06 finding is doc-framed (explicit doc/README/drift/
    example wording), which the frozen rubric scores as partial;
  - whether a quota_stop status is backed by the provider's quota warning
    text in the raw artifact.

What is NOT automated (manual semantic adjudication, recorded as data):
  - the per-case expected kinds in expected.json (the answer key, attributed
    to the starter's case evidence and the human clean-run analysis);
  - the rubric rule that a doc-framed finding on case 06 is partial;
  - the original human confirmation, during collection, that each finding
    matched the seeded defect. A finding whose text matches no mechanism
    term is labeled FINDING (unmatched) and surfaced for human review rather
    than silently scored CORRECT.

Idempotent: recomputes only from stored raw outputs; never re-contacts
providers, so a rerun cannot disturb completed pairs. --verify compares
against the committed matrix (runs/2026-11-20-clean/scores.json) and exits
non-zero on any mismatch. runner/test_score.py mutates raw copies to prove
the labels move with the evidence.

Usage: python3 runner/score.py [--verify]   (from the repository root)
"""
import json, re, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DOC_SIGNAL = re.compile(r"(?i)\b(doc[- ]?drift|readme(?:\.md)?|documentation|docs?|example|instructions?)\b")


def load(p, root=ROOT):
    with open(os.path.join(root, p)) as f:
        return json.load(f)


def _norm(s):
    return (s or "").replace("\xa0", " ")


# --- raw parsing: finding existence and finding text -------------------------

def greptile_finding_text(entry):
    """The Findings section of a Greptile review body, or '' when the review
    is summary-only ('appears safe to merge')."""
    comment = _norm(entry.get("comment"))
    if not comment or "Findings\n" not in comment:
        return ""
    section = comment.split("Findings\n", 1)[1]
    section = section.split("\nSummary", 1)[0]
    return section if "▶" in section else ""


def proofline_finding_text(entry):
    """The warning body from the Proofline console page, or '' when the
    review completed with no findings. Proofline posts a GitHub comment only
    when a review has findings; zero-finding reviews are console-only."""
    state = (entry.get("console_state") or "").lower()
    if "no findings" in state:
        return ""
    gh = entry.get("github_comment")
    has_gh = bool(gh and isinstance(gh, dict) and re.search(r"\b[1-9]\d* finding", gh.get("txt", "")))
    text = _norm(entry.get("console_page_text"))
    m = re.search(r"Warning[^\n]*\n(.+?)(?:\nImpact|\nConfirm records|$)", text, re.S)
    body = m.group(1).strip() if m else ""
    if has_gh or re.search(r"[1-9]\d* (warning|finding)s? to address", text):
        return body or (gh.get("txt", "") if has_gh else "")
    return ""


def coderabbit_quota(entry):
    return any("Review limit reached" in (it.get("x") or "") for it in entry.get("items", []))


FINDING_TEXT = {"greptile": greptile_finding_text, "proofline": proofline_finding_text}


# --- labeling ---------------------------------------------------------------

def label(kind, finding_text, mechanism_terms):
    """Map (expected kind, parsed finding text) to an outcome label."""
    found = bool(finding_text)
    if kind == "real_defect":
        if not found:
            return "MISSED"
        if any(t.lower() in finding_text.lower() for t in mechanism_terms):
            return "CORRECT"
        return "FINDING (unmatched)"  # surfaced for human adjudication
    if kind == "clean":
        return "FALSE_POSITIVE" if found else "quiet (correct)"
    if kind == "allowed_quiet":
        return "finding (context)" if found else "quiet (allowed)"
    if kind == "real_defect_partial":
        if not found:
            return "MISSED"
        if DOC_SIGNAL.search(finding_text):
            return "PARTIAL (doc framing)"  # rubric: doc-framed finding = partial
        if any(t.lower() in finding_text.lower() for t in mechanism_terms):
            return "CORRECT"
        return "FINDING (unmatched)"
    raise ValueError(kind)


def compute_scores(raw, expected, state):
    """Pure scoring over loaded artifacts. Returns {case: {provider: label}}."""
    out = {}
    for case, meta in expected.items():
        kind = meta["kind"]
        terms = meta.get("mechanism_terms", [])
        row = {}
        for provider, statuses in state["pairs"].items():
            s = statuses[case]
            if s == "not_applicable":
                row[provider] = "not_applicable"  # declared scope fact, not a score
                continue
            if s == "quota_stop":
                # status must be backed by the provider's quota warning in raw;
                # coderabbit records are per PR, PR 9..16 map to cases 01..08
                entries = [x for x in raw[provider] if x.get("pr") == 8 + int(case)]
                row[provider] = "quota_stop" if entries and all(coderabbit_quota(e) for e in entries) else "QUOTA_UNVERIFIED"
                continue
            entry = next(x for x in raw[provider] if x["case"] == case)
            row[provider] = label(kind, FINDING_TEXT[provider](entry), terms)
        out[case] = row
    return out


def load_artifacts(root=ROOT):
    state = load("runner/state.json", root)
    expected = load("runner/expected.json", root)["cases"]
    raw = {p: load(path, root) for p, path in state["raw"].items()}
    return raw, expected, state


def main():
    raw, expected, state = load_artifacts()
    out = compute_scores(raw, expected, state)

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
                if computed in ("quota_stop", "not_applicable"):
                    continue  # statuses, not scores; grounded in state.json + raw quota text
                ref = committed[case].get(provider, "")
                if base(ref) != base(computed):
                    print(f"MISMATCH {case}/{provider}: computed={computed!r} committed={ref!r}")
                    ok = False
        print("VERIFY", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
