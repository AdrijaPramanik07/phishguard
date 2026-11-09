import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure src path is accessible
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from src.explain import PhishExplainer

app = FastAPI(title="PhishGuard AI Engine")

# Enable CORS so your React frontend on port 3000 can communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load SHAP and model engine once on startup
explainer = PhishExplainer(model_path="models/model.joblib")

class URLRequest(BaseModel):
    url: str

@app.get("/api/health")
def health_check():
    return {"status": "online", "model": "XGBoost + SHAP Calibrated"}

@app.post("/api/scan")
def scan_url(payload: URLRequest):
    url = payload.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty")

    try:
        analysis = explainer.analyze_url(url)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)