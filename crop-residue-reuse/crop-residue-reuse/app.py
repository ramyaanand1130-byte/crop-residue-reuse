"""Smart Crop Residue Reuse Recommendation System with Tamil Voice Assistant.

Flask backend: serves the web page, validates farmer submissions, generates
rule-based recommendations and stores every submission in SQLite.

Run:  python app.py      then open http://127.0.0.1:5000 in Chrome or Edge.
"""

import json
import os
import sqlite3
from datetime import datetime, timezone

from flask import Flask, g, jsonify, render_template, request

import recommender

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("CROP_DB", os.path.join(BASE_DIR, "data", "records.db"))

app = Flask(__name__)
app.json.ensure_ascii = False  # keep Tamil readable in JSON responses

SCHEMA = """
CREATE TABLE IF NOT EXISTS submissions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at   TEXT NOT NULL,
    crop         TEXT NOT NULL,
    residue      TEXT NOT NULL,
    quantity     REAL NOT NULL,
    unit         TEXT NOT NULL,
    quantity_kg  REAL NOT NULL,
    moisture     TEXT NOT NULL,
    quality      TEXT NOT NULL,
    location     TEXT NOT NULL DEFAULT '',
    input_method TEXT NOT NULL DEFAULT 'manual',
    language     TEXT NOT NULL DEFAULT 'ta',
    result_json  TEXT NOT NULL
);
"""


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA)


def _row_to_item(row, with_result=False):
    result = json.loads(row["result_json"])
    item = {
        "id": row["id"],
        "created_at": row["created_at"],
        "crop": row["crop"],
        "residue": row["residue"],
        "quantity": row["quantity"],
        "unit": row["unit"],
        "moisture": row["moisture"],
        "quality": row["quality"],
        "location": row["location"],
        "input_method": row["input_method"],
        "top": [{"id": r["id"], "icon": r["icon"], "title": r["title"]}
                for r in result["recommendations"][:3]],
    }
    if with_result:
        item["result"] = result
    return item


def _error(message, status=400):
    return jsonify({"error": message}), status


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/options")
def api_options():
    return jsonify(recommender.catalog())


@app.post("/api/recommend")
def api_recommend():
    clean, err = recommender.validate_input(request.get_json(silent=True))
    if err:
        return _error(err)

    result = recommender.recommend(clean)
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    db = get_db()
    cur = db.execute(
        """INSERT INTO submissions
           (created_at, crop, residue, quantity, unit, quantity_kg, moisture, quality,
            location, input_method, language, result_json)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (created_at, clean["crop"], clean["residue"], clean["quantity"], clean["unit"],
         clean["quantity_kg"], clean["moisture"], clean["quality"], clean["location"],
         clean["input_method"], clean["language"], json.dumps(result, ensure_ascii=False)),
    )
    db.commit()
    return jsonify({"id": cur.lastrowid, "created_at": created_at, "result": result}), 201


@app.get("/api/history")
def api_history():
    rows = get_db().execute(
        "SELECT * FROM submissions ORDER BY id DESC LIMIT 100").fetchall()
    return jsonify({"items": [_row_to_item(r) for r in rows]})


@app.get("/api/history/<int:record_id>")
def api_history_item(record_id):
    row = get_db().execute(
        "SELECT * FROM submissions WHERE id = ?", (record_id,)).fetchone()
    if row is None:
        return _error({"en": "Record not found.", "ta": "பதிவு கிடைக்கவில்லை."}, 404)
    return jsonify(_row_to_item(row, with_result=True))


@app.delete("/api/history/<int:record_id>")
def api_history_delete(record_id):
    db = get_db()
    cur = db.execute("DELETE FROM submissions WHERE id = ?", (record_id,))
    db.commit()
    if cur.rowcount == 0:
        return _error({"en": "Record not found.", "ta": "பதிவு கிடைக்கவில்லை."}, 404)
    return jsonify({"deleted": record_id})


@app.delete("/api/history")
def api_history_clear():
    db = get_db()
    cur = db.execute("DELETE FROM submissions")
    db.commit()
    return jsonify({"deleted": cur.rowcount})


init_db()

if __name__ == "__main__":
    # Microphone access works on http://localhost / 127.0.0.1 without HTTPS.
    import sys
    # "python app.py --share" lets phones on the same Wi-Fi open the app.
    share = "--share" in sys.argv
    if share:
        print("\nOn your phone (same Wi-Fi) open  http://<this-computer's-IP>:5000\n"
              "Find the IP with 'ipconfig' (Windows) or 'ifconfig' / 'ip a' (Linux/Mac).\n")
    app.run(host="0.0.0.0" if share else "127.0.0.1",
            port=int(os.environ.get("PORT", 5000)),
            debug=os.environ.get("FLASK_DEBUG") == "1")
