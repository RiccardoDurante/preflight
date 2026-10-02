"""batch.py — Parses CSV rows into track dicts for batch analysis."""


def parse_batch_row(row):
    """Converts one CSV row (a dict from csv.DictReader) into a track dict,
    the same shape used by the single-track form. Returns (track, error):
    error is None on success, or a short string describing what is wrong
    with this row so the caller can skip it and keep processing the rest.
    """
    title = (row.get("title") or "").strip()
    artist = (row.get("artist") or "").strip()

    if title == "" or artist == "":
        return None, "Missing title or artist."

    track = {
        "title": title,
        "artist": artist,
        "isrc": (row.get("isrc") or "").strip(),
        "iswc": (row.get("iswc") or "").strip(),
        "publisher": (row.get("publisher") or "").strip(),
        "expected_streams": (row.get("expected_streams") or "0").strip(),
        "territory": (row.get("territory") or "other").strip(),
    }

    # Writers come as numbered columns: writer1_name, writer1_split,
    # writer1_ipi, writer2_name, writer2_split, writer2_ipi, and so on --
    # as many as the CSV header has. A row can have a different writer
    # count than another row in the same file.
    writers = []
    i = 1
    while f"writer{i}_name" in row:
        name = (row.get(f"writer{i}_name") or "").strip()
        if name != "":
            try:
                split_value = float(row.get(f"writer{i}_split") or 0)
            except ValueError:
                split_value = 0
            writers.append({
                "name": name,
                "split": split_value,
                "ipi": (row.get(f"writer{i}_ipi") or "").strip(),
            })
        i += 1

    track["writers"] = writers
    return track, None
