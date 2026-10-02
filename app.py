"""app.py — Flask routes for the PreFlight app."""

from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, abort, Response

from xhtml2pdf import pisa

from checks import run_all_checks, calculate_risk_score, score_band, estimate_revenue_at_risk
from models import init_db, save_track, get_track, get_all_tracks

app = Flask(__name__)

# Create the database tables at startup.
init_db()


# Home page: shows the form.
@app.route("/")
def index():
    return render_template("index.html")


# About page: explains the problem and the idea.
@app.route("/about")
def about():
    return render_template("about.html")


# Reads the form, runs the checks, saves the result, and goes to the report.
@app.route("/analyze", methods=["POST"])
def analyze():
    # Read the simple fields from the form.
    track = {
        "title": request.form.get("title", "").strip(),
        "artist": request.form.get("artist", "").strip(),
        "isrc": request.form.get("isrc", "").strip(),
        "iswc": request.form.get("iswc", "").strip(),
        "publisher": request.form.get("publisher", "").strip(),
        "expected_streams": request.form.get("expected_streams", "0").strip(),
        "territory": request.form.get("territory", "other").strip(),
    }

    # Read the writer fields (they come as parallel lists).
    names = request.form.getlist("writer_name")
    splits = request.form.getlist("writer_split")
    ipis = request.form.getlist("writer_ipi")

    # Build the list of writers.
    writers = []
    for i in range(len(names)):
        name = names[i].strip()
        if name == "":
            continue  # skip empty rows
        try:
            split_value = float(splits[i])
        except (ValueError, IndexError):
            split_value = 0
        ipi_value = ""
        if i < len(ipis):
            ipi_value = ipis[i].strip()
        writers.append({
            "name": name,
            "split": split_value,
            "ipi": ipi_value,
        })

    track["writers"] = writers

    # Basic check: title and artist are required.
    if track["title"] == "" or track["artist"] == "":
        return redirect(url_for("index"))

    # Run the validation and save.
    issues = run_all_checks(track)
    score = calculate_risk_score(issues)
    track_id = save_track(track, score, issues)

    return redirect(url_for("report", track_id=track_id))


# Report page: shows the score and the list of issues.
@app.route("/report/<int:track_id>")
def report(track_id):
    track = get_track(track_id)
    if track is None:
        abort(404)

    # Sort issues so that red comes before amber.
    red_issues = []
    amber_issues = []
    for issue in track["issues"]:
        if issue["severity"] == "red":
            red_issues.append(issue)
        else:
            amber_issues.append(issue)
    track["issues"] = red_issues + amber_issues

    band = score_band(track["risk_score"])
    revenue_risk = estimate_revenue_at_risk(track, track["issues"])
    return render_template("report.html", track=track, band=band, revenue_risk=revenue_risk)


# PDF download of the report.
@app.route("/report/<int:track_id>/pdf")
def report_pdf(track_id):
    track = get_track(track_id)
    if track is None:
        abort(404)

    # Same sort as the report page.
    red_issues = []
    amber_issues = []
    for issue in track["issues"]:
        if issue["severity"] == "red":
            red_issues.append(issue)
        else:
            amber_issues.append(issue)
    track["issues"] = red_issues + amber_issues

    band = score_band(track["risk_score"])

    # Render the PDF template and convert it to PDF.
    revenue_risk = estimate_revenue_at_risk(track, track["issues"])
    html = render_template("report_pdf.html", track=track, band=band, revenue_risk=revenue_risk)
    pdf_buffer = BytesIO()
    pisa.CreatePDF(src=html, dest=pdf_buffer)
    pdf_buffer.seek(0)

    # Build a safe file name from the track title.
    safe_title = ""
    for ch in track["title"]:
        if ch.isalnum() or ch in " -_":
            safe_title += ch
    safe_title = safe_title.strip()
    if safe_title == "":
        safe_title = "track"

    filename = "preflight_report_" + safe_title + ".pdf"

    return Response(
        pdf_buffer.read(),
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment; filename=" + filename},
    )


# History page: list of all analyzed tracks.
@app.route("/history")
def history():
    tracks = get_all_tracks()
    for t in tracks:
        t["band"] = score_band(t["risk_score"])
        t["revenue_risk"] = estimate_revenue_at_risk(t, t["issues"])
    return render_template("history.html", tracks=tracks)


if __name__ == "__main__":
    app.run(debug=True)







