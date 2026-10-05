import os
from typing import Dict, Any, Tuple
import numpy as np

from app.config import get_settings
from app.ml.feature_engineering import extract_feature_vector

settings = get_settings()

class FingerprintAnomalyDetector:
    """
    ML/Statistical detector for identifying fingerprint anomalies and rare configurations.
    Transparently loads an external scikit-learn model when MODEL_PATH exists, or
    falls back to deterministic statistical z-score/Euclidean centroid distance.
    """
    def __init__(self):
        self.model = None
        self.model_type = "STATISTICAL_BASELINE"
        self.model_loaded = False
        self._load_model_if_available()

        # Baseline centroids calculated from standard population datasets (Chrome/Win, Safari/Mac, etc.)
        self.standard_profiles = np.array([
            # Standard Chrome Win11: 1920x1080, dpr=1, 8 cores, 8GB, -480, ~50 fonts, 2 media, Intel/Nvidia
            [0.5, 0.5, 1.0, 0.75, 0.125, 0.125, -0.57, 0.25, 0.2, 0.6, 0.6, 2.0, 0.0, 0.0],
            # Standard Safari macOS Apple Silicon: 2560x1440, dpr=2, 8 cores, 16GB, -480, Apple M
            [0.66, 0.66, 2.0, 0.75, 0.125, 0.25, -0.57, 0.35, 0.2, 0.65, 0.65, 0.0, 1.0, 1.0],
            # Standard Chrome Linux: 1920x1080, dpr=1, 16 cores, 32GB, Intel
            [0.5, 0.5, 1.0, 0.75, 0.25, 0.5, 0.0, 0.2, 0.2, 0.6, 0.6, 2.0, 2.0, 0.0],
        ])

    def _load_model_if_available(self):
        model_path = settings.MODEL_PATH
        if model_path and os.path.exists(model_path):
            try:
                import joblib
                self.model = joblib.load(model_path)
                self.model_type = "TRAINED_SCIKIT_LEARN"
                self.model_loaded = True
            except Exception:
                self.model = None
                self.model_type = "STATISTICAL_BASELINE"
                self.model_loaded = False
        else:
            self.model = None
            self.model_type = "STATISTICAL_BASELINE"
            self.model_loaded = False

    def score_fingerprint(self, fingerprint_dict: Dict[str, Any]) -> Tuple[float, str]:
        """
        Computes anomaly score (0.0 to 100.0) where 100 is highly anomalous/unique,
        and returns detection metadata noting whether trained ML or statistical model was used.
        """
        features = extract_feature_vector(fingerprint_dict)
        vec = np.array(features)

        if self.model_loaded and self.model is not None:
            try:
                # Expecting scikit-learn decision_function or predict_proba
                if hasattr(self.model, "score_samples"):
                    raw_score = self.model.score_samples([vec])[0]
                    # Convert Isolation Forest negative score to 0-100 anomaly scale
                    anomaly_score = max(0.0, min(100.0, float((-raw_score + 0.5) * 80)))
                    return round(anomaly_score, 2), "TRAINED_SCIKIT_LEARN"
            except Exception:
                pass

        # Deterministic statistical calculation: min Euclidean distance to known population centroids
        distances = [np.linalg.norm(vec - centroid) for centroid in self.standard_profiles]
        min_dist = float(min(distances))

        # Typical standard distance is between 0.1 and 1.8. Anything > 2.5 is extremely rare/unique.
        anomaly_score = max(5.0, min(95.0, (min_dist / 3.0) * 100.0))
        return round(anomaly_score, 2), "STATISTICAL_BASELINE"

_detector_instance = None

def get_anomaly_detector() -> FingerprintAnomalyDetector:
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = FingerprintAnomalyDetector()
    return _detector_instance
