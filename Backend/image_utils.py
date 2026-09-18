
import easyocr
from PIL import Image
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from transformers import CLIPProcessor, CLIPModel
from sklearn.metrics.pairwise import cosine_similarity
import cv2
import re
import pymupdf

MAX_CLIP_TEXT_LENGTH = 77
FRAUD_KEYWORDS = [
    "bank",
    "otp",
    "upi",
    "payment",
    "verify",
    "login",
    "transaction",
    "account",
    "qr",
    "customer care",
    "wallet",
    "phishing",
    "fraud",
    "unauthorized",
    "credentials",
    "phone",
    "link",
    "sms",
    "mail",
    "scam",
    "malware",
    "ransomware",
    "without consent",
    "sensitive information",
    "personal information",
    "deleted",
    "blocked",
    "suspicious",
    "remote access",
    "email"
]

reader = easyocr.Reader(['en'], gpu=False)

# -----------------------------
# CLIP
# -----------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"

clip_model = CLIPModel.from_pretrained(
    "openai/clip-vit-base-patch32"
).to(device)

clip_processor = CLIPProcessor.from_pretrained(
    "openai/clip-vit-base-patch32"
)

def extract_text(image_path):
    try:
        result = reader.readtext(image_path)
        text = ""
        for r in result:
            text += r[1] + " "

        return text.strip()
    except:
        return ""

def extract_pdf_text(pdf_path):
    try:
        document = pymupdf.open(pdf_path)
        text = ""
        for page in document:
            text += page.get_text() + " "
        document.close()
        return text.strip()

    except Exception as e:
        print("PDF Text Extraction Error:", e)
        return ""


def pdf_to_images(pdf_path):
    try:
        document = pymupdf.open(pdf_path)

        if len(document) == 0:
            document.close()
            return []

        image_paths = []

        for page_number, page in enumerate(document):
            pix = page.get_pixmap(
                matrix=pymupdf.Matrix(2, 2),
                alpha=False
            )

            image_path = pdf_path + f"_page_{page_number}.png"
            pix.save(image_path)
            image_paths.append(image_path)

        document.close()
        return image_paths

    except Exception as e:
        print("PDF Image Conversion Error:", e)
        return []

def calculate_text_similarity(complaint, ocr_text):
    if not complaint or not ocr_text:
        return 0

    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf = vectorizer.fit_transform(
            [complaint.lower(), ocr_text.lower()]
        )

        similarity = cosine_similarity(
            tfidf[0],
            tfidf[1]
        )[0][0]

        return round(similarity * 100, 2)
    
    except:
        return 0
# -----------------------------
# CLIP Relevance
# -----------------------------
def _prepare_text_for_clip(text: str) -> str:
    if not text:
        return ""
    tokens = clip_processor.tokenizer(text, truncation=True)
    if len(tokens['input_ids']) > MAX_CLIP_TEXT_LENGTH:
        return clip_processor.tokenizer.decode(tokens['input_ids'][:MAX_CLIP_TEXT_LENGTH], skip_special_tokens=True)
    return text


def _count_fraud_keywords(text: str) -> int:
    if not text:
        return 0
    lowered = text.lower()
    count = 0
    for keyword in FRAUD_KEYWORDS:
        if keyword in lowered:
            count += 1
    return count


def check_relevance(image_path, complaint, ocr_text):

    clip_score = 0
    clip_error = False
    try:
        image = Image.open(image_path).convert("RGB")

        image_inputs = clip_processor(
            images=image,
            return_tensors="pt"
        ).to(device)

        safe_complaint = _prepare_text_for_clip(complaint)
        safe_ocr_text = _prepare_text_for_clip(ocr_text)

        text_inputs = clip_processor(
            text=[safe_complaint],
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=MAX_CLIP_TEXT_LENGTH
        ).to(device)

        ocr_text_inputs = None
        if safe_ocr_text:
            ocr_text_inputs = clip_processor(
                text=[safe_ocr_text],
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=MAX_CLIP_TEXT_LENGTH
            ).to(device)

        text_score = calculate_text_similarity(
            complaint,
            ocr_text
        )

        def _extract_tensor(output):
            if hasattr(output, "pooler_output") and output.pooler_output is not None:
                return output.pooler_output
            if hasattr(output, "image_embeds") and output.image_embeds is not None:
                return output.image_embeds
            if hasattr(output, "text_embeds") and output.text_embeds is not None:
                return output.text_embeds
            return output

        with torch.no_grad():
            image_output = clip_model.get_image_features(
                **image_inputs
            )
            text_output = clip_model.get_text_features(
                **text_inputs
            )

            image_features = _extract_tensor(image_output)
            text_features = _extract_tensor(text_output)

            clip_present_score = 0
            if isinstance(image_features, torch.Tensor) and isinstance(text_features, torch.Tensor) and image_features.ndim == 2 and text_features.ndim == 2:
                image_norm = image_features / image_features.norm(dim=-1, keepdim=True)
                text_norm = text_features / text_features.norm(dim=-1, keepdim=True)
                clip_present_score = max(0, torch.matmul(image_norm, text_norm.T).item() * 100)

            clip_score = clip_present_score
            if ocr_text_inputs is not None:
                ocr_text_output = clip_model.get_text_features(
                    **ocr_text_inputs
                )
                ocr_text_features = _extract_tensor(ocr_text_output)
                if isinstance(ocr_text_features, torch.Tensor) and ocr_text_features.ndim == 2 and isinstance(image_features, torch.Tensor) and image_features.ndim == 2:
                    ocr_text_norm = ocr_text_features / ocr_text_features.norm(dim=-1, keepdim=True)
                    ocr_clip_score = max(0, torch.matmul(image_norm, ocr_text_norm.T).item() * 100)
                    clip_score = max(clip_score, ocr_clip_score)

    except Exception as e:
        print("CLIP Error:", e)
        clip_error = True
        clip_score = 0

    keyword_count = _count_fraud_keywords(ocr_text)
    # keyword_count = _count_fraud_keywords(complaint + " " + ocr_text)
    keyword_score = min(keyword_count * 8, 28)
    if text_score < 1:
        keyword_score = min(keyword_count , 5)

    if text_score > 10:
        keyword_score = min(keyword_count * 8, 60)
        text_score *= 2
        if text_score > 32:
            keyword_score = 60

    qr_bonus = 0
    qr_found, _ = detect_qr(image_path)
    if qr_found:
        qr_bonus = 10

    final_score = (
        text_score * 0.4 +
        clip_score * 0.3 +
        keyword_score +
        qr_bonus
    )

    if (text_score == 0 and keyword_score == 0):
        final_score = 0

    if (final_score < 55 and text_score >= 10) and (keyword_score >= 20 or text_score >= 30 or clip_score >= 50):
        final_score = max(final_score, 55)

    final_score = round(min(final_score, 100), 2)

    if final_score >= 75:
        status = "Highly Relevant"
    elif final_score >= 50:
        status = "Relevant"
    elif final_score >= 30:
        status = "Partially Relevant"
    else:
        status = "Not Relevant"

    print(f"Relevance debug: text={text_score}, clip={clip_score}, keywords={keyword_score}, qr={qr_bonus}, final={final_score}")
    return status, final_score

 

def detect_qr(image_path):   
    try:
        image = cv2.imread(image_path)
        if image is None:
            return False, ""

        detector = cv2.QRCodeDetector()

        data, points, _ = detector.detectAndDecode(image)
        if points is not None:
            return True, data

        return False, ""

    except Exception as e:
        print("QR Detection Error:", e)
        return False, ""


def detect_urls(text):
    pattern = r'https?://[^\s]+|www\.[^\s]+'
    return re.findall(pattern, text)


def detect_phone_numbers(text):
    pattern = r'(?:\+91[- ]?)?[6-9]\d{9}'
    return re.findall(pattern, text)


def detect_emails(text):
    pattern = r"\b(?:[A-Za-z0-9._%+-]+@(?:gmail\.com|yahoo\.com|outlook\.com|hotmail\.com|businessmail\.com|[A-Za-z0-9-]+\.(?:com|in))|(?:noreply|info|support|contact|admin|help|hello|accounts)@[A-Za-z0-9-]+)\b"
    return re.findall(pattern, text)

def detect_upi(text):
    pattern = r"\b(?!noreply|info|support|contact|admin|help|hello|accounts)[a-zA-Z0-9.\-_]{2,}@(?!gmail\.com|yahoo\.com|outlook\.com|hotmail\.com|[A-Za-z0-9-]+\.(?:com|in))[a-zA-Z]{2,}\b"
    return re.findall(pattern, text)


def analyze_pdf(pdf_path, complaint):
    pdf_text = extract_pdf_text(pdf_path)
    image_paths = pdf_to_images(pdf_path)

    if image_paths:
        image_text = " ".join(
            extract_text(image_path)
            for image_path in image_paths
        ).strip()
        ocr_text = " ".join(
            text for text in (pdf_text, image_text) if text
        ).strip()

        relevance, score = check_relevance(
            image_paths[0],
            complaint,
            ocr_text
        )

        qr_detected, qr_text = detect_qr(
            image_paths[0]
        )

        for image_path in image_paths:
            try:
                import os
                os.remove(image_path)
            except:
                pass

    else:
        relevance = "Not Relevant"
        score = 0

        qr_detected = False
        qr_text = ""

    return (
        ocr_text,
        relevance,
        score,
        qr_detected,
        qr_text
    )