import os
import pickle
import numpy as np
from antrean.models import Layanan

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_model():
    path = os.path.join(CURRENT_DIR, "model_mlr.pkl")

    if not os.path.exists(path):
        raise FileNotFoundError(
            "Model MLR belum dibuat. Jalankan train_mlr terlebih dahulu."
        )

    with open(path, "rb") as f:
        data = pickle.load(f)

    return data["model"], data["fitur"]


def predict_waktu(layanan_id):
    """
    Menghasilkan prediksi waktu pelayanan untuk 1 layanan.
    Input: layanan_id (int)
    Output: prediksi menit (float)
    """

    model, fitur = load_model()

    # layanan target
    layanan_obj = Layanan.objects.get(id=layanan_id)
    layanan_target = (
        layanan_obj.layanan
        .strip()
        .lower()
        .replace(" ", "_")
    )

    # bentuk vektor sesuai fitur training
    arr = []
    for f in fitur:
        nama_layanan = f.replace("layanan_clean_", "")
        arr.append(1 if nama_layanan == layanan_target else 0)

    arr = np.array(arr).reshape(1, -1)

    pred = model.predict(arr)[0]

    return max(float(pred), 0.0)
