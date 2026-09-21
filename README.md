# Smart-Fraud-Complaint-Analyzer

This repository contains a full-stack fraud complaint analyzer built to process uploaded complaint documents, extract information, and classify incidents using a trained machine learning pipeline.

## Project structure

- `Backend/` — Flask API, OCR utilities, trained model files, and preprocessing code.
- `Frontend/Smart Fraud Analyzer/` — React + Vite frontend application.

## Backend setup

```bash
cd Backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The backend runs on `http://localhost:5000` by default.

## Frontend setup

```bash
cd "Frontend/Smart Fraud Analyzer"
npm install
npm run dev
```

The frontend usually runs on `http://localhost:5173`.

