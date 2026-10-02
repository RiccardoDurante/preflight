"""test_checks.py — Automated tests for the validation engine. Run with: pytest -v"""

import requests

import models
import musicbrainz_client
from checks import (
    check_splits_sum,
    validate_isrc,
    validate_iswc,
    check_isrc_iswc_linkage,
    check_missing_publisher,
    check_missing_ipi,
    check_similar_writer_names,
    check_isrc_conflict,
    check_iswc_conflict,
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


# --- Rule 7: similar writer names (fuzzy matching) ---

def test_similar_writer_names_detects_variant():
    writers = [
        {"name": "Mario Rossi"},
        {"name": "M. Rossi"},
    ]
    issue = check_similar_writer_names(writers)
    assert issue is not None
    assert issue["severity"] == "amber"


def test_different_writer_names_passes():
    writers = [
        {"name": "Mario Rossi"},
        {"name": "Anna Bianchi"},
    ]
    assert check_similar_writer_names(writers) is None


def test_exact_duplicate_is_not_flagged_here():
    # Same name, different case: this is check_name_consistency's job,
    # not check_similar_writer_names's job. It should be skipped here.
    writers = [
        {"name": "Mario Rossi"},
        {"name": "mario rossi"},
    ]
    assert check_similar_writer_names(writers) is None


# --- Rule 8: ISRC conflict via MusicBrainz (mocked, no real network calls) ---

def test_isrc_conflict_different_artist_is_red(monkeypatch):
    def fake_cache_lookup(isrc):
        return None  # cache miss

    def fake_save(isrc, recordings):
        pass  # do nothing, we don't need to really save during a test

    def fake_search(isrc):
        return [{"title": "One More Time", "artist": "Daft Punk", "mbid": "abc123"}]

    monkeypatch.setattr(models, "get_cached_mb_result", fake_cache_lookup)
    monkeypatch.setattr(models, "save_mb_result", fake_save)
    monkeypatch.setattr(musicbrainz_client, "search_recordings_by_isrc", fake_search)

    issue = check_isrc_conflict("GBDUW0000053", "Mario Rossi")
    assert issue is not None
    assert issue["severity"] == "red"


def test_isrc_conflict_same_artist_passes(monkeypatch):
    def fake_cache_lookup(isrc):
        return None

    def fake_save(isrc, recordings):
        pass

    def fake_search(isrc):
        return [{"title": "Notte a Roma", "artist": "Mario Rossi", "mbid": "abc123"}]

    monkeypatch.setattr(models, "get_cached_mb_result", fake_cache_lookup)
    monkeypatch.setattr(models, "save_mb_result", fake_save)
    monkeypatch.setattr(musicbrainz_client, "search_recordings_by_isrc", fake_search)

    assert check_isrc_conflict("ITB251234567", "Mario Rossi") is None


def test_isrc_conflict_no_recordings_found_passes(monkeypatch):
    def fake_cache_lookup(isrc):
        return None

    def fake_save(isrc, recordings):
        pass

    def fake_search(isrc):
        return []

    monkeypatch.setattr(models, "get_cached_mb_result", fake_cache_lookup)
    monkeypatch.setattr(models, "save_mb_result", fake_save)
    monkeypatch.setattr(musicbrainz_client, "search_recordings_by_isrc", fake_search)

    assert check_isrc_conflict("ITB251234567", "Mario Rossi") is None


def test_isrc_conflict_uses_cache_and_skips_network(monkeypatch):
    def fake_cache_lookup(isrc):
        # Cache hit: a different artist was already found and saved before.
        return [{"title": "One More Time", "artist": "Daft Punk", "mbid": "abc123"}]

    def fake_search(isrc):
        # This must never be called when the cache already has an answer.
        raise AssertionError("Network call made even though cache had a result.")

    monkeypatch.setattr(models, "get_cached_mb_result", fake_cache_lookup)
    monkeypatch.setattr(musicbrainz_client, "search_recordings_by_isrc", fake_search)

    issue = check_isrc_conflict("GBDUW0000053", "Mario Rossi")
    assert issue is not None
    assert issue["severity"] == "red"


def test_isrc_conflict_network_error_is_info(monkeypatch):
    def fake_cache_lookup(isrc):
        return None

    def fake_search(isrc):
        raise requests.exceptions.ConnectionError("No internet for this test.")

    monkeypatch.setattr(models, "get_cached_mb_result", fake_cache_lookup)
    monkeypatch.setattr(musicbrainz_client, "search_recordings_by_isrc", fake_search)

    issue = check_isrc_conflict("ITB251234567", "Mario Rossi")
    assert issue is not None
    assert issue["severity"] == "info"


def test_isrc_conflict_empty_isrc_passes():
    # No ISRC at all: nothing to check, and no network call should happen.
    assert check_isrc_conflict("", "Mario Rossi") is None


# --- Rule 9: ISWC conflict via MusicBrainz (mocked, no real network calls) ---

def test_iswc_conflict_different_composer_is_red(monkeypatch):
    def fake_cache_lookup(iswc):
        return None

    def fake_save(iswc, works):
        pass

    def fake_search(iswc):
        return [{"title": "HELLO!", "composers": ["Tsunku"], "mbid": "abc123"}]

    monkeypatch.setattr(models, "get_cached_mb_work_result", fake_cache_lookup)
    monkeypatch.setattr(models, "save_mb_work_result", fake_save)
    monkeypatch.setattr(musicbrainz_client, "search_works_by_iswc", fake_search)

    writers = [{"name": "Mario Rossi", "split": 100, "ipi": ""}]
    issue = check_iswc_conflict("T1016903209", writers)
    assert issue is not None
    assert issue["severity"] == "red"


def test_iswc_conflict_same_composer_passes(monkeypatch):
    def fake_cache_lookup(iswc):
        return None

    def fake_save(iswc, works):
        pass

    def fake_search(iswc):
        return [{"title": "Notte a Roma", "composers": ["Mario Rossi"], "mbid": "abc123"}]

    monkeypatch.setattr(models, "get_cached_mb_work_result", fake_cache_lookup)
    monkeypatch.setattr(models, "save_mb_work_result", fake_save)
    monkeypatch.setattr(musicbrainz_client, "search_works_by_iswc", fake_search)

    writers = [{"name": "Mario Rossi", "split": 100, "ipi": ""}]
    assert check_iswc_conflict("T1234567890", writers) is None


def test_iswc_conflict_matches_any_writer_in_list(monkeypatch):
    # The track has two writers. MusicBrainz's composer matches the second
    # one, not the first. This should still count as "the same work".
    def fake_cache_lookup(iswc):
        return None

    def fake_save(iswc, works):
        pass

    def fake_search(iswc):
        return [{"title": "Notte a Roma", "composers": ["Anna Bianchi"], "mbid": "abc123"}]

    monkeypatch.setattr(models, "get_cached_mb_work_result", fake_cache_lookup)
    monkeypatch.setattr(models, "save_mb_work_result", fake_save)
    monkeypatch.setattr(musicbrainz_client, "search_works_by_iswc", fake_search)

    writers = [
        {"name": "Mario Rossi", "split": 60, "ipi": ""},
        {"name": "Anna Bianchi", "split": 40, "ipi": ""},
    ]
    assert check_iswc_conflict("T1234567890", writers) is None


def test_iswc_conflict_no_works_found_passes(monkeypatch):
    def fake_cache_lookup(iswc):
        return None

    def fake_save(iswc, works):
        pass

    def fake_search(iswc):
        return []

    monkeypatch.setattr(models, "get_cached_mb_work_result", fake_cache_lookup)
    monkeypatch.setattr(models, "save_mb_work_result", fake_save)
    monkeypatch.setattr(musicbrainz_client, "search_works_by_iswc", fake_search)

    writers = [{"name": "Mario Rossi", "split": 100, "ipi": ""}]
    assert check_iswc_conflict("T1234567890", writers) is None


def test_iswc_conflict_uses_cache_and_skips_network(monkeypatch):
    def fake_cache_lookup(iswc):
        return [{"title": "HELLO!", "composers": ["Tsunku"], "mbid": "abc123"}]

    def fake_search(iswc):
        raise AssertionError("Network call made even though cache had a result.")

    monkeypatch.setattr(models, "get_cached_mb_work_result", fake_cache_lookup)
    monkeypatch.setattr(musicbrainz_client, "search_works_by_iswc", fake_search)

    writers = [{"name": "Mario Rossi", "split": 100, "ipi": ""}]
    issue = check_iswc_conflict("T1016903209", writers)
    assert issue is not None
    assert issue["severity"] == "red"


def test_iswc_conflict_network_error_is_info(monkeypatch):
    def fake_cache_lookup(iswc):
        return None

    def fake_search(iswc):
        raise requests.exceptions.ConnectionError("No internet for this test.")

    monkeypatch.setattr(models, "get_cached_mb_work_result", fake_cache_lookup)
    monkeypatch.setattr(musicbrainz_client, "search_works_by_iswc", fake_search)

    writers = [{"name": "Mario Rossi", "split": 100, "ipi": ""}]
    issue = check_iswc_conflict("T1234567890", writers)
    assert issue is not None
    assert issue["severity"] == "info"


def test_iswc_conflict_empty_iswc_passes():
    writers = [{"name": "Mario Rossi", "split": 100, "ipi": ""}]
    assert check_iswc_conflict("", writers) is None


# --- Score ---

def test_perfect_track_scores_100(monkeypatch):
    def fake_cache_lookup(isrc):
        return []  # pretend MusicBrainz has no conflicting recording

    def fake_work_cache_lookup(iswc):
        return []  # pretend MusicBrainz has no conflicting work

    monkeypatch.setattr(models, "get_cached_mb_result", fake_cache_lookup)
    monkeypatch.setattr(models, "get_cached_mb_work_result", fake_work_cache_lookup)

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
