"""checks.py — Metadata validation rules. Each returns {severity, message, fix} or None."""

import re


# Splits must sum to 100.
def check_splits_sum(writers):
    total = sum(w.get("split", 0) for w in writers)
    if abs(total - 100) < 0.01:
        return None
    return {
        "severity": "red",
        "message": f"Writer splits sum to {total}%, not 100%.",
        "fix": "Adjust the percentages so they total exactly 100%.",
    }


# ISRC format: CCOOOYYSSSSS (12 chars).
ISRC_PATTERN = re.compile(r"^[A-Z]{2}[A-Z0-9]{3}\d{2}\d{5}$")


def validate_isrc(isrc):
    if not isrc or not isrc.strip():
        return {"severity": "amber", "message": "ISRC missing.", "fix": "Add the track's ISRC."}
    cleaned = isrc.replace("-", "").upper().strip()
    if not ISRC_PATTERN.match(cleaned):
        return {
            "severity": "red",
            "message": f"ISRC '{isrc}' has an invalid format.",
            "fix": "Required format: 12 chars CCOOOYYSSSSS (e.g. ITB251234567).",
        }
    return None


# ISWC format: T + 10 digits.
ISWC_PATTERN = re.compile(r"^T\d{10}$")


def validate_iswc(iswc):
    if not iswc or not iswc.strip():
        return {"severity": "amber", "message": "ISWC missing.", "fix": "Add the composition's ISWC."}
    cleaned = iswc.replace("-", "").replace(".", "").upper().strip()
    if not ISWC_PATTERN.match(cleaned):
        return {
            "severity": "amber",
            "message": f"ISWC '{iswc}' has an invalid format.",
            "fix": "Required format: T-DDDDDDDDD-C (e.g. T-123456789-0).",
        }
    return None


# ISRC present but ISWC missing.
def check_isrc_iswc_linkage(isrc, iswc):
    has_isrc = bool(isrc and isrc.strip())
    has_iswc = bool(iswc and iswc.strip())
    if has_isrc and not has_iswc:
        return {
            "severity": "red",
            "message": "ISRC present but ISWC missing.",
            "fix": "Register the composition and link its ISWC to the ISRC.",
        }
    return None


# Publisher missing.
def check_missing_publisher(publisher):
    if not publisher or not publisher.strip():
        return {
            "severity": "amber",
            "message": "Publisher not specified.",
            "fix": "Specify the publisher (or 'self-published').",
        }
    return None


# IPI missing for one or more writers.
def check_missing_ipi(writers):
    missing = [
        w.get("name", "(unnamed)")
        for w in writers
        if not w.get("ipi") or not str(w.get("ipi")).strip()
    ]
    if missing:
        return {
            "severity": "amber",
            "message": f"IPI code missing for: {', '.join(missing)}.",
            "fix": "Add the IPI number for every writer.",
        }
    return None


# Writer names spelled inconsistently.
def check_name_consistency(artist, writers):
    def normalize(name):
        return re.sub(r"\s+", " ", name.strip().lower())

    originals = [w.get("name", "") for w in writers if w.get("name")]
    normalized = [normalize(n) for n in originals]
    seen = {}
    for original, norm in zip(originals, normalized):
        if norm in seen and seen[norm] != original:
            return {
                "severity": "amber",
                "message": f"Writer names spelled differently: '{seen[norm]}' and '{original}'.",
                "fix": "Use a consistent spelling for each writer's name.",
            }
        seen[norm] = original
    return None


# Run all rules, drop the Nones.
def run_all_checks(track):
    writers = track.get("writers", [])
    results = [
        check_splits_sum(writers),
        validate_isrc(track.get("isrc")),
        validate_iswc(track.get("iswc")),
        check_isrc_iswc_linkage(track.get("isrc"), track.get("iswc")),
        check_missing_publisher(track.get("publisher")),
        check_missing_ipi(writers),
        check_name_consistency(track.get("artist", ""), writers),
    ]
    return [r for r in results if r is not None]


# Score: start at 100, subtract per issue.
def calculate_risk_score(issues):
    score = 100
    for issue in issues:
        if issue["severity"] == "red":
            score -= 20
        elif issue["severity"] == "amber":
            score -= 8
    return max(score, 0)


# Score -> color band.
def score_band(score):
    if score >= 80:
        return "green"
    elif score >= 50:
        return "amber"
    else:
        return "red"


# Smoke test: `python checks.py`
if __name__ == "__main__":
    sample = {
        "title": "Notte a Roma",
        "artist": "Mario Rossi",
        "isrc": "ITB251234567",
        "iswc": "",
        "publisher": "",
        "writers": [
            {"name": "Mario Rossi", "split": 60, "ipi": "00123456789"},
            {"name": "Anna Bianchi", "split": 30, "ipi": ""},
        ],
    }

    issues = run_all_checks(sample)
    score = calculate_risk_score(issues)

    print(f"Risk score: {score}/100  (band: {score_band(score)})")
    print(f"Issues found: {len(issues)}\n")
    for i in issues:
        print(f"[{i['severity'].upper()}] {i['message']}")
        print(f"    -> {i['fix']}\n")