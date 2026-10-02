"""test_batch.py — Tests for CSV row parsing used by the batch upload."""

from batch import parse_batch_row


def test_minimal_valid_row():
    row = {"title": "Notte a Roma", "artist": "Mario Rossi"}
    track, error = parse_batch_row(row)
    assert error is None
    assert track["title"] == "Notte a Roma"
    assert track["artist"] == "Mario Rossi"
    assert track["writers"] == []


def test_missing_title_is_an_error():
    row = {"title": "", "artist": "Mario Rossi"}
    track, error = parse_batch_row(row)
    assert track is None
    assert error is not None


def test_missing_artist_is_an_error():
    row = {"title": "Notte a Roma", "artist": ""}
    track, error = parse_batch_row(row)
    assert track is None
    assert error is not None


def test_defaults_expected_streams_and_territory():
    row = {"title": "Notte a Roma", "artist": "Mario Rossi"}
    track, error = parse_batch_row(row)
    assert error is None
    assert track["expected_streams"] == "0"
    assert track["territory"] == "other"


def test_parses_one_writer():
    row = {
        "title": "Notte a Roma",
        "artist": "Mario Rossi",
        "writer1_name": "Mario Rossi",
        "writer1_split": "100",
        "writer1_ipi": "00123456789",
    }
    track, error = parse_batch_row(row)
    assert error is None
    assert len(track["writers"]) == 1
    assert track["writers"][0]["name"] == "Mario Rossi"
    assert track["writers"][0]["split"] == 100.0
    assert track["writers"][0]["ipi"] == "00123456789"


def test_parses_multiple_writers():
    row = {
        "title": "Notte a Roma",
        "artist": "Mario Rossi",
        "writer1_name": "Mario Rossi",
        "writer1_split": "60",
        "writer1_ipi": "",
        "writer2_name": "Anna Bianchi",
        "writer2_split": "40",
        "writer2_ipi": "",
    }
    track, error = parse_batch_row(row)
    assert error is None
    assert len(track["writers"]) == 2
    assert track["writers"][1]["name"] == "Anna Bianchi"


def test_skips_empty_writer_slots():
    # writer2_name is blank: that slot should be skipped, not added as an
    # empty writer.
    row = {
        "title": "Notte a Roma",
        "artist": "Mario Rossi",
        "writer1_name": "Mario Rossi",
        "writer1_split": "100",
        "writer1_ipi": "",
        "writer2_name": "",
        "writer2_split": "",
        "writer2_ipi": "",
    }
    track, error = parse_batch_row(row)
    assert error is None
    assert len(track["writers"]) == 1


def test_invalid_split_defaults_to_zero():
    row = {
        "title": "Notte a Roma",
        "artist": "Mario Rossi",
        "writer1_name": "Mario Rossi",
        "writer1_split": "not-a-number",
        "writer1_ipi": "",
    }
    track, error = parse_batch_row(row)
    assert error is None
    assert track["writers"][0]["split"] == 0
