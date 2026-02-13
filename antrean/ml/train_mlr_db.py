import os
import pickle
import pandas as pd
from sklearn.linear_model import LinearRegression
from antrean.models import Antrean

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def train_mlr_by_date(start_date=None, end_date=None):
    qs = Antrean.objects.filter(
        status="Selesai",
        durasi_pelayanan__isnull=False
    )

    if start_date:
        qs = qs.filter(tgl_daftar__date__gte=start_date)

    if end_date:
        qs = qs.filter(tgl_daftar__date__lte=end_date)

    if not qs.exists():
        raise ValueError("Data training kosong pada rentang tanggal tersebut")

    data = list(
        qs.values(
            "layanan__layanan",
            "durasi_pelayanan"
        )
    )

    df = pd.DataFrame(data)
    df.rename(columns={"layanan__layanan": "layanan"}, inplace=True)

    df["layanan_clean"] = (
        df["layanan"]
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    df = pd.get_dummies(df, columns=["layanan_clean"])
    fitur = [c for c in df.columns if c.startswith("layanan_clean_")]

    X = df[fitur]
    y = df["durasi_pelayanan"]

    model = LinearRegression()
    model.fit(X, y)

    model_path = os.path.join(BASE_DIR, "model_mlr.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(
            {"model": model, "fitur": fitur},
            f
        )

    return len(df)
