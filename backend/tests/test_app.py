import io
import json
import os
import tempfile
import pytest
from PIL import Image, ImageDraw, ImageFont

from backend.app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_index(client):
    rv = client.get('/')
    assert rv.status_code in (200, 304)


def test_summarize_empty(client):
    rv = client.post('/api/summarize', data=json.dumps({}), content_type='application/json')
    assert rv.status_code == 400


def test_summarize_structure(client):
    payload = { 'text': 'This is a test. It has multiple sentences. The goal is to summarize effectively.', 'level': 'short' }
    rv = client.post('/api/summarize', data=json.dumps(payload), content_type='application/json')
    assert rv.status_code == 200
    data = rv.get_json()
    # ensure new structured fields exist
    assert 'summary' in data and isinstance(data['summary'], str)
    assert 'points' in data and isinstance(data['points'], list)
    assert 'suggestions' in data and isinstance(data['suggestions'], list)
    assert data.get('level') == 'short'


def _make_pdf_bytes(text: str = "Hello PDF") -> bytes:
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt=text, ln=True, align='L')
    out = pdf.output(dest='S')
    # fpdf2 may return bytearray
    if isinstance(out, bytearray):
        out = bytes(out)
    return out


def test_upload_pdf_extracts_text(client):
    pdf_bytes = _make_pdf_bytes("Hello from PDF")
    data = {
        'file': (io.BytesIO(pdf_bytes), 'sample.pdf')
    }
    rv = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert rv.status_code == 200, rv.data
    payload = rv.get_json()
    assert 'text' in payload
    assert isinstance(payload['text'], str)
    # pdfminer might not perfectly include the word, but should have non-empty text
    assert payload['text'].strip() != ''


def test_upload_invalid_extension(client):
    data = {
        'file': (io.BytesIO(b'hello'), 'note.txt')
    }
    rv = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert rv.status_code == 400
    payload = rv.get_json()
    assert payload.get('code') == 'UNSUPPORTED_TYPE'


def test_upload_image_ocr_when_available(client):
    # Skip if Tesseract binary isn't available
    import pytesseract
    try:
        _ = pytesseract.get_tesseract_version()
    except Exception:
        pytest.skip("tesseract binary not installed")

    # Create a simple high-contrast image with text
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    # Use default bitmap font for portability
    draw.text((20, 80), "Hello OCR", fill='black')

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    data = {
        'file': (buf, 'image.png')
    }
    rv = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert rv.status_code in (200, 422), rv.data  # allow empty text depending on env quality
    if rv.status_code == 200:
        payload = rv.get_json()
        assert payload['text'].strip() != ''
