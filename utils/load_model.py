# services/load_model.py

# Import library
import joblib
from functools import lru_cache


@lru_cache(maxsize=1)
def load_models():
    """
    Memuat model machine learning dan scaler sekali.
    """

    return {
        "knn_model": joblib.load("models/knn_model.pkl"),
        "rf_model": joblib.load("models/random_forest_model.pkl"),
        "voting_model": joblib.load("models/voting_classifier_model.pkl"),
        "scaler": joblib.load("models/scaler.pkl")
    }


# Inisialisasi model (dipanggil saat modul diimpor)
_models = load_models()

knn_model = _models["knn_model"]
rf_model = _models["rf_model"]
voting_model = _models["voting_model"]
scaler = _models["scaler"]