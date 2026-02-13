import os
import pickle
import numpy as np
from antrean.models import Layanan

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_model():
    with open(os.path.join(BASE_DIR, "model_mlr.pkl"), "rb") as f:
        data = pickle.load(f)
    return data["model"], data["fitur"]

def predict_by_layanan(layanan_nama):
    model, fitur = load_model()

    layanan_clean = layanan_nama.strip().lower().replace(" ", "_")

    x = [
        1 if f.replace("layanan_clean_", "") == layanan_clean else 0
        for f in fitur
    ]

    pred = model.predict(np.array(x).reshape(1, -1))[0]
    return max(float(pred), 0.0)
