"""dashboard.py — Aggregates stats across all analyzed tracks for the dashboard page."""


def build_catalog_summary(tracks):
    """Takes the list of tracks returned by models.get_all_tracks() (each
    already carrying its "issues", "band", and "revenue_risk") and returns
    a dict of catalog-wide numbers for the dashboard page.
    """
    total_tracks = len(tracks)

    if total_tracks == 0:
        return {
            "total_tracks": 0,
            "average_score": 0,
            "band_counts": {"green": 0, "amber": 0, "red": 0},
            "total_revenue_at_risk": 0,
            "top_fixes": [],
        }

    average_score = sum(t["risk_score"] for t in tracks) / total_tracks

    band_counts = {"green": 0, "amber": 0, "red": 0}
    for t in tracks:
        band_counts[t["band"]] += 1

    total_revenue_at_risk = sum(t["revenue_risk"]["revenue_at_risk"] for t in tracks)

    # Count how many times each fix recommendation appears across every
    # track''s issues. The fix text is stable (it never embeds per-track
    # data like names or numbers, unlike some issue messages), so this is
    # a reliable way to see which action is needed most often across the
    # whole catalog.
    fix_counts = {}
    for t in tracks:
        for issue in t["issues"]:
            fix = issue["fix"]
            fix_counts[fix] = fix_counts.get(fix, 0) + 1

    top_fixes = sorted(fix_counts.items(), key=lambda pair: pair[1], reverse=True)
    top_fixes = [{"fix": fix, "count": count} for fix, count in top_fixes[:5]]

    return {
        "total_tracks": total_tracks,
        "average_score": round(average_score, 1),
        "band_counts": band_counts,
        "total_revenue_at_risk": round(total_revenue_at_risk, 2),
        "top_fixes": top_fixes,
    }
