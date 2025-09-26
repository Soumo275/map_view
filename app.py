from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from supabase import create_client, Client
from datetime import datetime
import os
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# ------------------ Database Config ------------------
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", 5432)  # default postgres port
DB_NAME = os.getenv("DB_NAME")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ------------------ Supabase Client ------------------
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# ------------------ Model ------------------
class ReportCard(db.Model):
    __tablename__ = "report_card"
    post_id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String)
    hazard_type = db.Column(db.String, nullable=False)
    severity_level = db.Column(db.String, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    description = db.Column(db.String)
    image_url = db.Column(db.String)
    video_url = db.Column(db.String)
    tags = db.Column(db.String)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)



# ------------------ API ------------------

# Create a report
# Fetch all reports
@app.route("/reports", methods=["GET"])
def get_reports():
    try:
        reports = ReportCard.query.order_by(ReportCard.uploaded_at.desc()).all()
        result = []
        for report in reports:
            result.append({
                "post_id": report.post_id,
                "user_id": report.user_id,
                "hazard_type": report.hazard_type,
                "severity_level": report.severity_level,
                "latitude": report.latitude,
                "longitude": report.longitude,
                "description": report.description,
                "image_url": report.image_url,
                "video_url": report.video_url,
                "tags": report.tags,
                "uploaded_at": report.uploaded_at.isoformat() if report.uploaded_at else None,
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Get a single report by ID
@app.route("/reports/<post_id>", methods=["GET"])
def get_report(post_id):
    try:
        report = ReportCard.query.get(post_id)
        if not report:
            return jsonify({"error": "Report not found"}), 404

        return jsonify({
            "post_id": report.post_id,
            "user_id": report.user_id,
            "hazard_type": report.hazard_type,
            "severity_level": report.severity_level,
            "latitude": report.latitude,
            "longitude": report.longitude,
            "description": report.description,
            "image_url": report.image_url,
            "video_url": report.video_url,
            "tags": report.tags,
            "uploaded_at": report.uploaded_at,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def serve_index():
    return send_file("index.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

