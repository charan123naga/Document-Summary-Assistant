import os
from pdfminer.high_level import extract_text as pdf_extract_text
from PIL import Image, ImageFilter
import pytesseract
from typing import Tuple


def _preprocess_for_ocr(img: Image.Image) -> Image.Image:
    """Basic preprocessing: grayscale, denoise, and binarize for OCR."""
    gray = img.convert('L') 
   
    gray = gray.filter(ImageFilter.MedianFilter(size=3))
    gray = gray.filter(ImageFilter.SHARPEN)
   
    bw = gray.point(lambda x: 255 if x > 150 else 0, mode='1')
    return bw


def _is_image_extension(ext: str) -> bool:
    return ext in {'.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp', '.webp'}


def extract_text(path: str) -> str:
    """Extract text from a PDF or image file.

    Uses pdfminer for PDFs and pytesseract for images with basic preprocessing.
    """
    _, ext = os.path.splitext(path.lower())
    if ext == '.pdf':
      
        return pdf_extract_text(path)
    elif _is_image_extension(ext):
      
        with Image.open(path) as img:
            pre = _preprocess_for_ocr(img)
          
            config = '--oem 3 --psm 6'
            text = pytesseract.image_to_string(pre, config=config)
            return text
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
