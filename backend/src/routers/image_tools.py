"""Image analysis service — OCR + description via EasyOCR + optional LLM."""
from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Optional

import easyocr
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# EasyOCR reader (lazy init — models load on first call)
# ---------------------------------------------------------------------------
_reader: Optional[easyocr.Reader] = None


def _get_reader() -> easyocr.Reader:
    global _reader
    if _reader is None:
        logger.info("Initializing EasyOCR reader (tha+eng)…")
        _reader = easyocr.Reader(["th", "en"], gpu=True, verbose=False)
    return _reader


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
router = APIRouter(prefix="/v1/image", tags=["image"])


@router.post("/ocr")
async def ocr_image(file: UploadFile = File(...)):
    """Extract text from an uploaded image (Thai + English)."""
    try:
        content = await file.read()
        if len(content) > 20 * 1024 * 1024:
            raise HTTPException(413, "File too large (max 20MB)")
        
        reader = _get_reader()
        results = reader.readtext(content, detail=0, paragraph=True)
        text = "\n".join(results)
        
        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "text": text,
            "lines": results
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("OCR failed")
        raise HTTPException(500, f"OCR failed: {e}")


@router.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """Upload image → return OCR text + basic metadata."""
    try:
        content = await file.read()
        if len(content) > 20 * 1024 * 1024:
            raise HTTPException(413, "File too large (max 20MB)")
        
        # OCR
        reader = _get_reader()
        results = reader.readtext(content, detail=0, paragraph=True)
        text = "\n".join(results)
        
        # Basic metadata
        from PIL import Image
        img = Image.open(io.BytesIO(content))
        
        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "format": img.format,
            "size": img.size,
            "mode": img.mode,
            "text": text,
            "lines": results
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Analyze failed")
        raise HTTPException(500, f"Analyze failed: {e}")
