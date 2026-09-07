"""
Astral — Complete Astrology Web App
Running FastAPI with frontend static files served
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=7860)
