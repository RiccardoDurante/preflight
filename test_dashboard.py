"""test_dashboard.py — Tests for catalog-wide aggregation used by the dashboard."""

from dashboard import build_catalog_summary


def make_track(risk_score, band, issues, revenue_at_risk):
    return {
        "risk_score": risk_score,
        "band": band,
        "issues": issues,
        "revenue_risk": {"revenue_at_risk": revenue_at_risk},
    }


def test_empty_catalog():
    summary = build_catalog_summary([])
    assert summary["total_tracks"] == 0
    assert summary["average_score"] == 0
    assert summary["band_counts"] == {"green": 0, "amber": 0, "red": 0}
    assert summary["total_revenue_at_risk"] == 0
    assert summary["top_fixes"] == []


def test_total_tracks_and_average_score():
    tracks = [
        make_track(100, "green", [], 0),
        make_track(60, "amber", [], 0),
    ]
    summary = build_catalog_summary(tracks)
    assert summary["total_tracks"] == 2
    assert summary["average_score"] == 80.0


def test_band_counts():
    tracks = [
        make_track(100, "green", [], 0),
        make_track(90, "green", [], 0),
        make_track(60, "amber", [], 0),
        make_track(20, "red", [], 0),
    ]
    summary = build_catalog_summary(tracks)
    assert summary["band_counts"] == {"green": 2, "amber": 1, "red": 1}


def test_total_revenue_at_risk_sums_across_tracks():
    tracks = [
        make_track(80, "green", [], 10.50),
        make_track(60, "amber", [], 25.25),
    ]
    summary = build_catalog_summary(tracks)
    assert summary["total_revenue_at_risk"] == 35.75


def test_top_fixes_counts_and_sorts_by_frequency():
    common_fix = {"severity": "amber", "message": "x", "fix": "Add the IPI number for every writer."}
    rare_fix = {"severity": "red", "message": "y", "fix": "Register the composition and link its ISWC to the ISRC."}

    tracks = [
        make_track(80, "green", [common_fix], 0),
        make_track(70, "amber", [common_fix], 0),
        make_track(60, "amber", [common_fix, rare_fix], 0),
    ]
    summary = build_catalog_summary(tracks)
    assert summary["top_fixes"][0]["fix"] == "Add the IPI number for every writer."
    assert summary["top_fixes"][0]["count"] == 3
    assert summary["top_fixes"][1]["count"] == 1


def test_top_fixes_capped_at_five():
    issues = [
        {"severity": "amber", "message": "x", "fix": f"Fix number {i}"}
        for i in range(8)
    ]
    tracks = [make_track(50, "amber", issues, 0)]
    summary = build_catalog_summary(tracks)
    assert len(summary["top_fixes"]) == 5
