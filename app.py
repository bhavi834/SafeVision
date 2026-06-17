"""
app.py
------
Flask dashboard — the "core pipeline" slice of Module 8.

Live right now:
  /            home page with the image upload dropzone
  /upload      runs PPEDetector + ComplianceEngine on the uploaded image,
               saves an annotated copy, renders the per-person result page
  /api/detect  JSON equivalent of /upload, for future video/webcam/mobile use

Stubbed (placeholder pages, wired into nav so the dashboard shape is
already there for the next phase):
  /live        Module 5 — webcam/CCTV streaming
  /violations  Module 7/8 — violation history from MongoDB
  /reports     Module 10 — daily/weekly/monthly reports
  /analytics   Module 10 — compliance charts & trends
"""

import os
import uuid

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename

import config
from detection.detector import PPEDetector
from detection.compliance import ComplianceEngine
from alerts.email_alert import send_email_alert, build_violation_message as build_email_message
from alerts.telegram_alert import send_telegram_alert, build_violation_message as build_telegram_message
from database.db import insert_violation

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH

os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(config.OUTPUT_FOLDER, exist_ok=True)

# Loaded lazily on first request that actually needs the model (see
# PPEDetector.model), so the dashboard still boots even before you've
# trained a model — you just can't run detection until you have.
detector = PPEDetector()
engine = ComplianceEngine()


def _allowed_image(filename: str) -> bool:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in config.ALLOWED_IMAGE_EXTENSIONS


def _notify_violations(results, image_path):
    """Fire DB write + alert channels for every non-compliant person.

    Each of these is a no-op (returns False/None) unless explicitly
    enabled in .env, so this is safe to call unconditionally.
    """
    records = engine.to_violation_records(results, source_path=image_path)
    for record in records:
        insert_violation(record)

        timestamp = record["timestamp"]
        missing = record["missing_ppe"]

        subject, body = build_email_message(missing, record["location"], timestamp)
        send_email_alert(subject, body)

        send_telegram_alert(build_telegram_message(missing, record["location"], timestamp))


@app.route("/")
def home():
    return render_template(
        "index.html",
        active_page="home",
        classes=config.CLASS_NAMES,
        required_ppe=config.REQUIRED_PPE,
    )


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("image")
    if not file or file.filename == "":
        flash("No image selected.", "error")
        return redirect(url_for("home"))

    if not _allowed_image(file.filename):
        flash(f"Unsupported file type. Allowed: {', '.join(config.ALLOWED_IMAGE_EXTENSIONS)}", "error")
        return redirect(url_for("home"))

    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    upload_path = os.path.join(config.UPLOAD_FOLDER, filename)
    file.save(upload_path)

    try:
        image, detections = detector.predict_path(upload_path)
    except FileNotFoundError as exc:
        flash(str(exc), "error")
        return redirect(url_for("home"))

    results = engine.evaluate(detections)
    status_map = {i: p.is_compliant for i, p in enumerate(results)}
    annotated = detector.draw_detections(image, detections, status_map)

    import cv2
    output_filename = f"annotated_{filename}"
    output_path = os.path.join(config.OUTPUT_FOLDER, output_filename)
    cv2.imwrite(output_path, annotated)

    violation_count = sum(1 for p in results if not p.is_compliant)
    if violation_count:
        _notify_violations(results, upload_path)

    return render_template(
        "result.html",
        active_page="home",
        results=results,
        violation_count=violation_count,
        annotated_image=f"outputs/{output_filename}",
    )


@app.route("/api/detect", methods=["POST"])
def api_detect():
    """JSON API: same pipeline as /upload, for programmatic / future
    video-frame and webcam callers."""
    file = request.files.get("image")
    if not file or file.filename == "":
        return jsonify({"error": "No image file provided under field name 'image'."}), 400

    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    upload_path = os.path.join(config.UPLOAD_FOLDER, filename)
    file.save(upload_path)

    try:
        _, detections = detector.predict_path(upload_path)
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 503

    results = engine.evaluate(detections)
    violation_count = sum(1 for p in results if not p.is_compliant)
    if violation_count:
        _notify_violations(results, upload_path)

    return jsonify(
        {
            "person_count": len(results),
            "violation_count": violation_count,
            "results": [p.to_dict() for p in results],
        }
    )


# --------------------------------------------------------------------------
# Stub pages for upcoming modules — keep the dashboard nav fully clickable
# now, swap each render_template call for the real implementation later.
# --------------------------------------------------------------------------
@app.route("/live")
def live():
    return render_template(
        "coming_soon.html",
        active_page="live",
        page_title="Live Monitoring",
        module_label="Module 5",
        description="Real-time webcam/CCTV detection with live worker counts is next on the roadmap.",
    )


@app.route("/violations")
def violations():
    return render_template(
        "coming_soon.html",
        active_page="violations",
        page_title="Violation History",
        module_label="Module 7/8",
        description="Once MongoDB is connected, every violation logged here gets a searchable history view.",
    )


@app.route("/reports")
def reports():
    return render_template(
        "coming_soon.html",
        active_page="reports",
        page_title="Reports",
        module_label="Module 10",
        description="Daily / weekly / monthly compliance reports will be generated here.",
    )


@app.route("/analytics")
def analytics():
    return render_template(
        "coming_soon.html",
        active_page="analytics",
        page_title="Analytics",
        module_label="Module 10",
        description="Compliance trends, PPE usage charts, and violation frequency breakdowns land here.",
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
