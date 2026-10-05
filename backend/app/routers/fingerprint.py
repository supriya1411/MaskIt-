from fastapi import APIRouter, Depends
from app.schemas.fingerprint import FingerprintAnalyzeRequest, FingerprintAnalyzeResponse
from app.services.risk_engine import RiskEngine
from app.dependencies import enforce_rate_limit

router = APIRouter(prefix="/fingerprint", tags=["Fingerprint Analysis"], dependencies=[Depends(enforce_rate_limit)])

@router.post("/analyze", response_model=FingerprintAnalyzeResponse)
def analyze_fingerprint(payload: FingerprintAnalyzeRequest):
    """
    Evaluates privacy-safe signals, computes deterministic risk score (0-100),
    detects browser/OS inconsistencies, and returns granular recommendations.
    Never stores complete raw fingerprints.
    """
    signals_dict = payload.model_dump()
    result = RiskEngine.analyze(signals_dict)
    return FingerprintAnalyzeResponse(**result)
