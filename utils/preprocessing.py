# services/preprocessing.py

# Import library
import pandas as pd

# Import scaler
from utils.load_model import scaler


# Preprocessing input
def preprocess_input(
    gender,
    hemoglobin,
    mch,
    mchc,
    mcv
):
    """
    Melakukan preprocessing data input
    sebelum digunakan oleh model.
    """

    # Membentuk dataframe
    input_data = pd.DataFrame({
        "Gender": [gender],
        "Hemoglobin": [hemoglobin],
        "MCH": [mch],
        "MCHC": [mchc],
        "MCV": [mcv]
    })

    # Standardisasi data
    input_scaled = scaler.transform(
        input_data
    )

    return input_scaled