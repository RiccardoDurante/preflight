"""test_checks.py — Automated tests for the validation engine. Run with: pytest -v"""

from checks import (
    check_splits_sum,
    validate_isrc,
    validate_iswc,
    check_isrc_iswc_linkage,
    check_missing_publisher,
    check_missing_ipi,
    run_all_checks,
    calculate_risk_score,
    score_band,
)


# --- Rule 1: splits sum ---

def test_splits_sum_100_passes():
    writers = [{"split": 60}, {"split": 40}]
    assert check_splits_sum(writers) is None


def test_splits_over_100_is_red():
    writers = [{"split": 60}, {"split": 60}]
    issue = check_splits_sum(writers)
    assert issue is not None
    assert issue["severity"] == "red"


def test_splits_under_100_is_red():
    writers = [{"split": 60}, {"split": 30}]
    issue = check_splits_sum(writers)
    assert issue is not None
    assert issue["severity"] == "red"


def test_splits_with_rounding_passes():
    # 33.33 + 33.33 + 33.34 = 100.00
    writers = [{"split": 33.33}, {"split": 33.33}, {"split": 33.34}]
    assert check_splits_sum(writers) is None


# --- Rule 2: ISRC ---

def test_valid_isrc_passes():
    assert validate_isrc("ITB251234567") is None


def test_isrc_with_hyphens_passes():
    assert validate_isrc("IT-B25-12-34567") is None


def test_malformed_isrc_is_red():
    issue = validate_isrc("ITB25")
    assert issue is not None
    assert issue["severity"] == "red"


def test_missing_isrc_is_amber():
    issue = validate_isrc("")
    assert issue is not None
    assert issue["severity"] == "amber"


# --- Rule 3: ISWC ---

def test_valid_iswc_passes():
    assert validate_iswc("T-123456789-0") is None


def test_malformed_iswc_is_amber():
    issue = validate_iswc("X999")
    assert issue is not None
    assert issue["severity"] == "amber"


# --- Rule 4: linkage (the important one) ---

def test_isrc_present_iswc_missing_is_red():
    issue = check_isrc_iswc_linkage("ITB251234567", "")
    assert issue is not None
    assert issue["severity"] == "red"


def test_both_codes_present_passes():
    assert check_isrc_iswc_linkage("ITB251234567", "T-123456789-0") is None


# --- Rules 5 & 6: publisher and IPI ---

def test_missing_publisher_is_amber():
    issue = check_missing_publisher("")
    assert issue is not None
    assert issue["severity"] == "amber"


def test_missing_ipi_is_amber():
    writers = [{"name": "Mario Rossi", "ipi": ""}]
    issue = check_missing_ipi(writers)
    assert issue is not None
    assert issue["severity"] == "amber"


# --- Score ---

def test_perfect_track_scores_100():
    track = {
        "title": "Perfect",
        "artist": "Mario Rossi",
        "isrc": "ITB251234567",
        "iswc": "T-123456789-0",
        "publisher": "Rossi Publishing",
        "writers": [{"name": "Mario Rossi", "split": 100, "ipi": "00123456789"}],
    }
    issues = run_all_checks(track)
    assert issues == []
    assert calculate_risk_score(issues) == 100


def test_two_reds_subtract_40():
    issues = [
        {"severity": "red", "message": "x", "fix": "y"},
        {"severity": "red", "message": "x", "fix": "y"},
    ]
    assert calculate_risk_score(issues) == 60


def test_score_never_below_zero():
    issues = [{"severity": "red", "message": "x", "fix": "y"}] * 10
    assert calculate_risk_score(issues) == 0


def test_score_bands():
    assert score_band(100) == "green"
    assert score_band(65) == "amber"
    assert score_band(30) == "red"