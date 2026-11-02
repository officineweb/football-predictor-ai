from fastapi import FastAPI
from pydantic import BaseModel, Field
from predictor import analyze

app = FastAPI(title="Football Predictor AI API", version="0.1.0")

class MatchInput(BaseModel):
    home: str = "Home"
    away: str = "Away"
    lambda_home: float = Field(1.5, ge=0, le=8)
    lambda_away: float = Field(1.1, ge=0, le=8)

@app.get("/health")
def health():
    return {"status":"ok","version":"0.1.0"}

@app.post("/analyze")
def match_analyze(m: MatchInput):
    return {"home":m.home,"away":m.away,"inputs":{"lambda_home":m.lambda_home,"lambda_away":m.lambda_away},
            "probabilities":analyze(m.lambda_home,m.lambda_away)}
