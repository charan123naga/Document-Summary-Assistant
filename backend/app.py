import os
import sys
import logging
import tempfile
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__, static_folder="../frontend/dist", static_url_path="")

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
CORS(app, resources={r"/api/*": {"origins": "*"}})


try:
    from backend import extract, summarize  
except (ModuleNotFoundError, ImportError):
   
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from backend import extract, summarize



logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s %(name)s: %(message)s')
logger = logging.getLogger(__name__)


@app.route('/')
def index():
   
    index_path = os.path.join(app.static_folder or '', 'index.html')
    if app.static_folder and os.path.exists(index_path):
        return send_from_directory(app.static_folder, 'index.html')
    return jsonify({"status": "backend running"})


@app.route('/api/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'no file uploaded', 'code': 'NO_FILE'}), 400
    f = request.files['file']
    if f.filename == '':
        return jsonify({'error': 'empty filename', 'code': 'EMPTY_FILENAME'}), 400

   
    allowed = {'.pdf', '.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp', '.webp'}
    _, ext = os.path.splitext(f.filename.lower())
    if ext not in allowed:
        return jsonify({'error': f'unsupported file type: {ext}', 'code': 'UNSUPPORTED_TYPE'}), 400

  
    suffix = os.path.splitext(f.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        f.save(tmp.name)
        tmp_path = tmp.name

    try:
        logger.info("Processing upload: filename=%s size=%sB tmp=%s", f.filename, request.content_length, tmp_path)
        text = extract.extract_text(tmp_path)
       
        if text:
            preview = (text[:400] + '...') if len(text) > 400 else text
            logger.info("Extracted %d chars. Preview: %s", len(text), preview)
        else:
            logger.info("Extraction produced empty text")
    except Exception as e:
        logger.exception("Extraction failed: %s", e)
        return jsonify({'error': 'extraction failed', 'details': str(e), 'code': 'EXTRACTION_FAILED'}), 500
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    if not text or not text.strip():
        return jsonify({'error': 'no text extracted', 'code': 'EMPTY_TEXT'}), 422

    return jsonify({'text': text})


@app.route('/api/summarize', methods=['POST'])
def summarize_route():
        """Summarization endpoint returning structured data.

        Request JSON:
            { "text": "...", "level": "short|medium|long" }

        Response JSON:
            {
                "summary": str,
                "points": [str, ...],
                "suggestions": [str, ...],
                "level": str,
                "chars": int
            }
        """
        data = request.get_json() or {}
        text = data.get('text', '')
        level = data.get('level', 'short')
        if not text or not str(text).strip():
                return jsonify({'error': 'no text provided', 'code': 'NO_TEXT'}), 400

        result = summarize.summarize(text, level=level)
       
        return jsonify(result)



@app.errorhandler(413)
def too_large(_e):
    return jsonify({'error': 'file too large', 'code': 'FILE_TOO_LARGE', 'maxBytes': app.config['MAX_CONTENT_LENGTH']}), 413


if __name__ == '__main__':
    app.run(debug=True)
