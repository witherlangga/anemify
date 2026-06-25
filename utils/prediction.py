# services/prediction.py

# Import library
import pandas as pd
import numpy as np

# Import model
from utils.load_model import (
    knn_model,
    rf_model,
    voting_model
)

# Import preprocessing
from utils.preprocessing import preprocess_input


# Prediksi menggunakan KNN
def predict_knn(gender, hemoglobin, mch, mchc, mcv):
    input_scaled = preprocess_input(gender, hemoglobin, mch, mchc, mcv)
    return int(knn_model.predict(input_scaled)[0])


# Prediksi menggunakan Random Forest
def predict_rf(gender, hemoglobin, mch, mchc, mcv):
    input_data = pd.DataFrame({
        "Gender": [gender],
        "Hemoglobin": [hemoglobin],
        "MCH": [mch],
        "MCHC": [mchc],
        "MCV": [mcv]
    })

    return int(rf_model.predict(input_data)[0])


# Prediksi menggunakan Voting Classifier
def predict_voting(gender, hemoglobin, mch, mchc, mcv):
    input_scaled = preprocess_input(gender, hemoglobin, mch, mchc, mcv)
    return int(voting_model.predict(input_scaled)[0])


# Mengubah hasil prediksi menjadi label
def get_prediction_label(prediction):
    return "Berisiko Anemia" if int(prediction) == 1 else "Tidak Berisiko Anemia"


# Melakukan prediksi berdasarkan model yang dipilih
def predict(model_name, gender, hemoglobin, mch, mchc, mcv):
    if model_name == "KNN":
        return predict_knn(gender, hemoglobin, mch, mchc, mcv)
    if model_name == "Random Forest":
        return predict_rf(gender, hemoglobin, mch, mchc, mcv)
    return predict_voting(gender, hemoglobin, mch, mchc, mcv)


# Prediksi probabilitas untuk KNN
def predict_proba_knn(gender, hemoglobin, mch, mchc, mcv):
    input_scaled = preprocess_input(gender, hemoglobin, mch, mchc, mcv)
    return knn_model.predict_proba(input_scaled)[0]


# Prediksi probabilitas untuk Random Forest
def predict_proba_rf(gender, hemoglobin, mch, mchc, mcv):
    input_data = pd.DataFrame({
        "Gender": [gender],
        "Hemoglobin": [hemoglobin],
        "MCH": [mch],
        "MCHC": [mchc],
        "MCV": [mcv]
    })
    return rf_model.predict_proba(input_data)[0]


# Prediksi probabilitas untuk Voting Classifier (robust fallback)
def predict_proba_voting(gender, hemoglobin, mch, mchc, mcv):
    # Avoid accessing voting_model.predict_proba directly because scikit-learn's
    # descriptor may raise AttributeError. Instead compute probabilities from
    # internal estimators when possible.
    input_scaled = preprocess_input(gender, hemoglobin, mch, mchc, mcv)

    # Try to get internal estimators safely
    estimators = None
    try:
        named = getattr(voting_model, "named_estimators_", None)
        if named:
            estimators = list(named.values())
        else:
            estimators = getattr(voting_model, "estimators_", None)
    except Exception:
        estimators = None

    probs = []
    if estimators:
        for est in estimators:
            if est is None:
                continue

            # Try estimator.predict_proba without triggering sklearn descriptors
            est_proba = None
            try:
                est_proba = getattr(est, "predict_proba", None)
            except Exception:
                est_proba = None

            if callable(est_proba):
                # Try scaled input first
                try:
                    p = est_proba(input_scaled)
                    probs.append(p[0])
                    continue
                except Exception:
                    pass

                # Try raw dataframe input
                try:
                    input_df = pd.DataFrame({
                        "Gender": [gender],
                        "Hemoglobin": [hemoglobin],
                        "MCH": [mch],
                        "MCHC": [mchc],
                        "MCV": [mcv]
                    })
                    p = est_proba(input_df)
                    probs.append(p[0])
                    continue
                except Exception:
                    pass

            # If no predict_proba, fallback to predict -> one-hot
            try:
                pred = est.predict(input_scaled)[0]
                probs.append([0.0, 1.0] if int(pred) == 1 else [1.0, 0.0])
            except Exception:
                try:
                    input_df = pd.DataFrame({
                        "Gender": [gender],
                        "Hemoglobin": [hemoglobin],
                        "MCH": [mch],
                        "MCHC": [mchc],
                        "MCV": [mcv]
                    })
                    pred = est.predict(input_df)[0]
                    probs.append([0.0, 1.0] if int(pred) == 1 else [1.0, 0.0])
                except Exception:
                    continue

    if probs:
        return np.mean(probs, axis=0)

    # If no internal estimators or none usable, fallback to voting_model.predict
    try:
        pred = voting_model.predict(input_scaled)[0]
        return [0.0, 1.0] if int(pred) == 1 else [1.0, 0.0]
    except Exception:
        return [0.5, 0.5]


# Prediksi semua model sekaligus, mengembalikan prediksi dan probabilitas
def predict_all(gender, hemoglobin, mch, mchc, mcv):
    results = {}

    knn_pred = predict_knn(gender, hemoglobin, mch, mchc, mcv)
    knn_proba = predict_proba_knn(gender, hemoglobin, mch, mchc, mcv)
    results["KNN"] = {"prediction": knn_pred, "proba": list(knn_proba)}

    rf_pred = predict_rf(gender, hemoglobin, mch, mchc, mcv)
    rf_proba = predict_proba_rf(gender, hemoglobin, mch, mchc, mcv)
    results["Random Forest"] = {"prediction": rf_pred, "proba": list(rf_proba)}

    voting_pred = predict_voting(gender, hemoglobin, mch, mchc, mcv)
    voting_proba = predict_proba_voting(gender, hemoglobin, mch, mchc, mcv)
    results["Voting Classifier"] = {"prediction": voting_pred, "proba": list(voting_proba)}

    return results