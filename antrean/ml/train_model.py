import os
import pandas as pd
import pickle
from sklearn.linear_model import LinearRegression

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def train_mlr():
    print("📌 Membaca dataset...")
    print("🔥 SCRIPT DIJALANKAN 🔥")

    # Path file relatif terhadap file ini
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(BASE_DIR, "layanan.csv")

    if not os.path.exists(dataset_path):
        raise FileNotFoundError("❌ layanan.csv tidak ditemukan!")

    df = pd.read_csv(dataset_path)

    # Normalisasi nama layanan
    df["layanan_clean"] = (
        df["layanan"]
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # One-hot encoding
    df = pd.get_dummies(df, columns=["layanan_clean"])

    fitur = [c for c in df.columns if c.startswith("layanan_clean_")]

    X = df[fitur]
    y = df["waktu_layanan"]

    print("📌 Melatih model MLR...")
    model = LinearRegression()
    model.fit(X, y)

    # Simpan model + fitur
    model_path = os.path.join(BASE_DIR, "model_mlr.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(
            {
                "model": model,
                "fitur": fitur
            },
            f
        )

    print("✅ Model berhasil disimpan:", model_path)
    print("📌 Fitur yang digunakan:", fitur)


# Opsional: agar bisa dijalankan manual
if __name__ == "__main__":
    train_mlr()
