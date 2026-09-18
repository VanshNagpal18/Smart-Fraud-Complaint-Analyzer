
from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import json
import os
import numpy as np
from werkzeug.utils import secure_filename
from image_utils import (
    extract_text,
    check_relevance,
    analyze_pdf,
    detect_qr,
    detect_urls,
    detect_phone_numbers,
    detect_emails,
    detect_upi
)
import re
from datetime import datetime



app = Flask(__name__)
CORS(app)

BASE_DIR = os.getcwd() 

model = pickle.load(open(os.path.join(BASE_DIR, "model.pkl"), "rb"))
vectorizer = pickle.load(open(os.path.join(BASE_DIR, "vectorizer.pkl"), "rb"))
label_encoder = pickle.load(open(os.path.join(BASE_DIR, "label_encoder.pkl"), "rb"))

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp",
    "pdf"
}

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )

def parse_date(date_text):
    date_text = re.sub(r'\s+', ' ', date_text.strip())

    formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%Y/%m/%d",
        "%Y-%m-%d",
        "%Y.%m.%d",
        "%d %B %Y",
        "%d %b %Y",
        "%B %d, %Y",
        "%B %d %Y",
        "%b %d, %Y",
        "%b %d %Y"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_text, fmt)
        except ValueError:
            continue
    return None


def parse_time(time_text):
    time_text = re.sub(r'\s+', ' ', time_text.strip())

    time_text = re.sub(
        r'(\d{1,2})\.(\d{2})',
        r'\1:\2',
        time_text
    )

    formats = [
        "%I:%M %p",
        "%I:%M:%S %p",
        "%H:%M",
        "%H:%M:%S"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(time_text, fmt)
        except ValueError:
            continue

    return None


def extract_timeline_events(text, source):
    events = []

    if not text:
        return events

    date_pattern = (
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b'
        r'|'
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'
        r'|'
        r'\b\d{1,2}\s+'
        r'(?:January|February|March|April|May|June|July|August|'
        r'September|October|November|December)'
        r'\s+\d{4}\b'
        r'|'
        r'\b(?:January|February|March|April|May|June|July|August|'
        r'September|October|November|December)'
        r'\s+\d{1,2},?\s+\d{4}\b'
    )

    time_pattern = (
        r'\b(?:0?[1-9]|1[0-2])'
        r'[:.]\d{2}'
        r'\s*(?:AM|PM|am|pm)\b'
    )

    date_matches = list(
        re.finditer(
            date_pattern,
            text,
            re.IGNORECASE
        )
    )

    time_matches = list(
        re.finditer(
            time_pattern,
            text,
            re.IGNORECASE
        )
    )

    for time_match in time_matches:

        time_text = time_match.group().strip()

        parsed_time = parse_time(time_text)

        if not parsed_time:
            continue

        time_position = time_match.start()

        previous_dates = [
            d for d in date_matches
            if d.start() < time_position
        ]

        next_dates = [
            d for d in date_matches
            if d.start() > time_position
        ]

        selected_date = None

        if previous_dates:

            previous_date = previous_dates[-1]

            if next_dates:

                next_date = next_dates[0]

                distance_to_next = (
                    next_date.start() -
                    time_match.end()
                )

                distance_to_previous = (
                    time_match.start() -
                    previous_date.end()
                )

                if (
                    distance_to_next >= 0
                    and distance_to_next <= 20
                    and distance_to_next < distance_to_previous
                ):
                    selected_date = next_date
                else:
                    selected_date = previous_date

            else:
                selected_date = previous_date

        elif next_dates:
            selected_date = next_dates[0]

        if not selected_date:
            continue

        parsed_date = parse_date(
            selected_date.group()
        )

        if not parsed_date:
            continue


        start_positions = [
            text.rfind(".", 0, time_match.start()),
            text.rfind("!", 0, time_match.start()),
            text.rfind("?", 0, time_match.start()),
            text.rfind("\n", 0, time_match.start())
        ]

        start = max(start_positions) + 1

        end_positions = [
            text.find(".", time_match.end()),
            text.find("!", time_match.end()),
            text.find("?", time_match.end()),
            text.find("\n", time_match.end())
        ]

        valid_end_positions = [
            position
            for position in end_positions
            if position != -1
        ]

        if valid_end_positions:
            end = min(valid_end_positions) + 1
        else:
            end = len(text)

        event_text = text[start:end].strip()

        # Clean OCR spaces
        event_text = re.sub(
            r'\s+',
            ' ',
            event_text
        ).strip()

        if not event_text:
            event_text = time_text

        events.append({
            "date": parsed_date.strftime("%Y-%m-%d"),
            "time": parsed_time.strftime("%I:%M %p"),
            "event": event_text,
            "source": source
        })

    dates_with_times = {
        event["date"]
        for event in events
    }

    for date_match in date_matches:

        parsed_date = parse_date(
            date_match.group()
        )

        if not parsed_date:
            continue

        date_string = parsed_date.strftime(
            "%Y-%m-%d"
        )

        if date_string in dates_with_times:
            continue

        start_positions = [
            text.rfind(".", 0, date_match.start()),
            text.rfind("!", 0, date_match.start()),
            text.rfind("?", 0, date_match.start()),
            text.rfind("\n", 0, date_match.start())
        ]

        start = max(start_positions) + 1

        end_positions = [
            text.find(".", date_match.end()),
            text.find("!", date_match.end()),
            text.find("?", date_match.end()),
            text.find("\n", date_match.end())
        ]

        valid_end_positions = [
            position
            for position in end_positions
            if position != -1
        ]

        if valid_end_positions:
            end = min(valid_end_positions) + 1
        else:
            end = len(text)

        event_text = text[start:end].strip()

        event_text = re.sub(
            r'\s+',
            ' ',
            event_text
        ).strip()

        if not event_text:
            event_text = date_match.group()

        events.append({
            "date": date_string,
            "time": "",
            "event": event_text,
            "source": source
        })

    return events


def create_timeline(complaint, proof_text, analysis_time=None):
    timeline = []

    # Complaint events
    timeline.extend(
        extract_timeline_events(
            complaint,
            "Complaint"
        )
    )

    timeline.extend(
        extract_timeline_events(
            proof_text,
            "Proof"
        )
    )

    if analysis_time:
     try:
        analysis_datetime = datetime.fromisoformat(
            analysis_time.replace("Z", "+00:00")
        )

        timeline.append({
            "date": analysis_datetime.strftime("%Y-%m-%d"),
            "time": analysis_datetime.strftime("%I:%M %p"),
            "event": "Complaint entered by user",
            "source": "Analysis"
        })

     except ValueError:
        pass

    # Sort by date and time
    def timeline_sort_key(item):

        date_part = item["date"]

        if item["time"]:
            try:
                time_part = datetime.strptime(
                    item["time"],
                    "%I:%M %p"
                ).strftime("%H:%M")
            except ValueError:
                time_part = "00:00"
        else:
            time_part = "00:00"

        return (
            date_part,
            time_part
        )

    timeline.sort(
        key=timeline_sort_key
    )

    return timeline

with open(os.path.join(BASE_DIR, "mapping.json"), "r", encoding="utf-8") as f:
    section_mapping = json.load(f)

@app.route("/")
def home():
    return jsonify({"message": "Smart Fraud Complaint Analyzer API is Running"})

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True)
    if not data:
        data = request.form.to_dict()

    analysis_time = data.get("analysis_time")
    complaint = (data.get("complaint") or "").strip()
    selected_category = (data.get("selected_category") or "").strip()
    image = request.files.get("image")
    print("Backend received image:", bool(image), image.filename if image else None)

    image_name = ""
    image_uploaded = False
    ocr_text = ""
    relevance = "Not Applicable"
    score = 0.0
    qr_detected = False
    qr_data = ""
    urls = []
    phones = []
    emails = []
    upi_ids = []

    if image:

        image_uploaded = True

    image_name = secure_filename(
        image.filename
    )

    if not allowed_file(image_name):

        return jsonify({
            "error":
            "Only JPG, JPEG, PNG, WEBP and PDF files are allowed."
        }), 400

    image_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        image_name
    )

    image.save(image_path)

    extension = image_name.rsplit(
        ".",
        1
    )[1].lower()

    if extension == "pdf":

        (
            ocr_text,
            relevance,
            score,
            qr_detected,
            qr_text
        ) = analyze_pdf(
            image_path,
            complaint
        )

    else:

        ocr_text = extract_text(
            image_path
        )

        relevance, score = check_relevance(
            image_path,
            complaint,
            ocr_text
        )

        qr_detected, qr_text = detect_qr(
            image_path
        )

        qr_data = [qr_text] if qr_text else []

    urls = detect_urls(
        ocr_text
    )

    phones = detect_phone_numbers(
        ocr_text
    )

    emails = detect_emails(
        ocr_text
    )

    upi_ids = detect_upi(
        ocr_text
    )

    if complaint == "":
                     return jsonify({"error": "Complaint cannot be empty."}), 400

    complaint_vector = vectorizer.transform([complaint])
    prediction = model.predict(complaint_vector)
    predicted_category = label_encoder.inverse_transform(prediction)[0]
    predicted_section = section_mapping.get(predicted_category, "Not Available")

    is_match = selected_category.lower() == predicted_category.lower()

    result = {
        "complaint": complaint,
        "selected_category": selected_category,
        "predicted_category": predicted_category,
        "suggested_section": predicted_section,
        "match": is_match,
        "ocr_text": ocr_text,
        "image_uploaded": image_uploaded,
        "image_relevance": relevance,
        "relevance_score": score,
        "qr_detected": qr_detected,
        "qr_data": qr_data,
        "urls": urls,
        "phone_numbers": phones,
        "emails": emails,
        "upi_ids": upi_ids,
        "timeline": create_timeline(
            complaint,
            ocr_text,
            analysis_time
        )
    }

    return jsonify(result)

if __name__ == "__main__":
    flask_debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(
        debug=flask_debug,
        use_reloader=flask_debug,
        host="0.0.0.0",
        port=5000
    )