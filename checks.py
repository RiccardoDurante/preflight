"""checks.py — Metadata validation rules. Each returns {severity, message, fix} or None."""

import re
import requests
from rapidfuzz import fuzz

import models
import musicbrainz_client


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


# How similar two writer names must be (0-100) to flag them as possible
# duplicates, when they are not already an exact match.
# Lower than ARTIST_SIMILARITY_THRESHOLD on purpose: an abbreviation like
# "M. Rossi" shares fewer characters with "Mario Rossi" than two spellings
# of the same full name would, so a strict threshold would miss it.
NAME_SIMILARITY_THRESHOLD = 60


# Writer names that look like variants of each other (e.g. "Mario Rossi"
# and "M. Rossi"), but are not spelled identically.
def check_similar_writer_names(writers):
    names = [w.get("name", "") for w in writers if w.get("name")]

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            name_a = names[i]
            name_b = names[j]

            if name_a.strip().lower() == name_b.strip().lower():
                continue  # exact match, already caught by check_name_consistency

            similarity = fuzz.ratio(name_a, name_b)
            if similarity >= NAME_SIMILARITY_THRESHOLD:
                return {
                    "severity": "amber",
                    "message": f"Writer names look similar, possible duplicate: "
                                f"'{name_a}' and '{name_b}'.",
                    "fix": "Confirm these are two different people, or use one consistent name.",
                }
    return None


# How similar two names must be to count as "the same person". Used both
# for the ISRC artist check and the ISWC composer check.
ARTIST_SIMILARITY_THRESHOLD = 70


# ISRC already registered on MusicBrainz for a different artist.
def check_isrc_conflict(isrc, artist):
    if not isrc or not isrc.strip():
        return None

    cleaned_isrc = isrc.replace("-", "").upper().strip()

    cached_result = models.get_cached_mb_result(cleaned_isrc)

    if cached_result is not None:
        recordings = cached_result
    else:
        try:
            recordings = musicbrainz_client.search_recordings_by_isrc(cleaned_isrc)
            models.save_mb_result(cleaned_isrc, recordings)
        except requests.exceptions.RequestException:
            return {
                "severity": "info",
                "message": "Could not check MusicBrainz for ISRC conflicts right now.",
                "fix": "Check your internet connection and try again later.",
            }

    if len(recordings) == 0:
        return None

    same_artist_found = False
    for recording in recordings:
        similarity = fuzz.token_sort_ratio(artist, recording["artist"])
        if similarity >= ARTIST_SIMILARITY_THRESHOLD:
            same_artist_found = True
            break

    if same_artist_found:
        return None

    other_title = recordings[0]["title"]
    other_artist = recordings[0]["artist"]
    return {
        "severity": "red",
        "message": f"This ISRC is already registered for a different work "
                    f"(found: '{other_title}' by {other_artist}).",
        "fix": "Verify the ISRC is correct, or request a new one for this recording.",
    }


# ISWC already registered on MusicBrainz for a different composer.
# Unlike the ISRC check (one artist), a work can have several writers, so
# we compare against the whole writers list: if at least one of our
# writers matches at least one composer MusicBrainz found, we treat it as
# the same work, not a conflict.
def check_iswc_conflict(iswc, writers):
    if not iswc or not iswc.strip():
        return None

    cleaned_iswc = iswc.replace("-", "").replace(".", "").upper().strip()

    cached_result = models.get_cached_mb_work_result(cleaned_iswc)

    if cached_result is not None:
        works = cached_result
    else:
        try:
            works = musicbrainz_client.search_works_by_iswc(cleaned_iswc)
            models.save_mb_work_result(cleaned_iswc, works)
        except requests.exceptions.RequestException:
            return {
                "severity": "info",
                "message": "Could not check MusicBrainz for ISWC conflicts right now.",
                "fix": "Check your internet connection and try again later.",
            }

    if len(works) == 0:
        return None

    our_writer_names = [w.get("name", "") for w in writers if w.get("name")]

    same_composer_found = False
    for work in works:
        for composer_name in work["composers"]:
            for our_name in our_writer_names:
                similarity = fuzz.token_sort_ratio(our_name, composer_name)
                if similarity >= ARTIST_SIMILARITY_THRESHOLD:
                    same_composer_found = True
                    break
            if same_composer_found:
                break
        if same_composer_found:
            break

    if same_composer_found:
        return None

    other_title = works[0]["title"]
    # Remove duplicate composer names (MusicBrainz can list the same
    # person twice, e.g. once as composer and once as lyricist).
    unique_composers = []
    for name in works[0]["composers"]:
        if name not in unique_composers:
            unique_composers.append(name)
    other_composers = ", ".join(unique_composers) if unique_composers else "unknown composer"

    return {
        "severity": "red",
        "message": f"This ISWC is already registered for a different work "
                    f"(found: '{other_title}' by {other_composers}).",
        "fix": "Verify the ISWC is correct, or request a new one for this composition.",
    }


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
        check_similar_writer_names(writers),
        check_isrc_conflict(track.get("isrc"), track.get("artist", "")),
        check_iswc_conflict(track.get("iswc"), writers),
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


# Royalty rate per stream, in euros (rough industry averages).
ROYALTY_RATE_PER_STREAM = {
    "italy": 0.0035,
    "usa": 0.0040,
    "other": 0.0025,
}

# Each red issue puts this fraction of revenue at risk (e.g. wrong splits
# or missing ISWC linkage can block or misdirect royalty payments).
# Each amber issue puts a smaller fraction at risk. Capped so the total
# never exceeds 80% (there's always some chance revenue still comes through).
RISK_FRACTION_RED = 0.15
RISK_FRACTION_AMBER = 0.05
RISK_FRACTION_CAP = 0.80


# Rough euro estimate of revenue at risk, based on expected streams,
# territory, and the issues found. This is an illustrative estimate,
# not a financial calculation -- it's meant to make the risk tangible,
# not to be precise.
def estimate_revenue_at_risk(track, issues):
    try:
        streams = float(track.get("expected_streams", 0))
    except (ValueError, TypeError):
        streams = 0

    territory = track.get("territory", "other")
    rate = ROYALTY_RATE_PER_STREAM.get(territory, ROYALTY_RATE_PER_STREAM["other"])

    risk_fraction = 0
    for issue in issues:
        if issue["severity"] == "red":
            risk_fraction += RISK_FRACTION_RED
        elif issue["severity"] == "amber":
            risk_fraction += RISK_FRACTION_AMBER
    risk_fraction = min(risk_fraction, RISK_FRACTION_CAP)

    total_revenue = streams * rate
    revenue_at_risk = total_revenue * risk_fraction

    return {
        "total_revenue": round(total_revenue, 2),
        "risk_fraction": round(risk_fraction * 100, 1),  # as a percentage
        "revenue_at_risk": round(revenue_at_risk, 2),
    }


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
    models.init_db()

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

    print("--- Direct test of check_isrc_conflict ---")
    conflict = check_isrc_conflict("GBDUW0000053", "Mario Rossi")
    if conflict is None:
        print("No conflict detected (unexpected for this test).")
    else:
        print(f"[{conflict['severity'].upper()}] {conflict['message']}")
        print(f"    -> {conflict['fix']}")

    print("\n--- Direct test of check_similar_writer_names ---")
    similar_writers = [
        {"name": "Mario Rossi", "split": 60, "ipi": ""},
        {"name": "M. Rossi", "split": 40, "ipi": ""},
    ]
    similar = check_similar_writer_names(similar_writers)
    if similar is None:
        print("No similar names detected (unexpected for this test).")
    else:
        print(f"[{similar['severity'].upper()}] {similar['message']}")
        print(f"    -> {similar['fix']}")

    print("\n--- Direct test of check_iswc_conflict ---")
    fake_writers = [{"name": "Mario Rossi", "split": 100, "ipi": ""}]
    iswc_conflict = check_iswc_conflict("T-101.690.320-9", fake_writers)
    if iswc_conflict is None:
        print("No conflict detected (unexpected for this test).")
    else:
        print(f"[{iswc_conflict['severity'].upper()}] {iswc_conflict['message']}")
        print(f"    -> {iswc_conflict['fix']}")

