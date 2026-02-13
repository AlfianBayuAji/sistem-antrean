# antar/antrean/train_model.py
import pickle
import pandas as pd
from sklearn.linear_model import LinearRegression
from antrean.models import Antrean, Layanan

def train_model(output_path='antar/antrean/model_storage/model.pkl'):
    # Query data antrean yg selesai dan punya durasi
    qs = Antrean.objects.filter(
        waktu_mulai__isnull=False,
        waktu_selesai__isnull=False,
        durasi_pelayanan__isnull=False
    ).values(
        'id', 'layanan_id', 'tgl_daftar', 'waktu_mulai', 'waktu_selesai', 'durasi_pelayanan'
    )

    df = pd.DataFrame(list(qs))
    if df.empty or len(df) < 10:
        print("Data training kurang (<10). Hentikan training.")
        return

    # Convert timestamps ke fitur numerik (contoh: epoch seconds)
    df['tgl_daftar_ts'] = pd.to_datetime(df['tgl_daftar']).astype('int64') // 10**9
    df['waktu_mulai_ts'] = pd.to_datetime(df['waktu_mulai']).astype('int64') // 10**9

    # dynamic one-hot layanan
    layanan_ids = list(Layanan.objects.values_list('id', flat=True))
    for l_id in layanan_ids:
        df[f'layanan_{l_id}'] = (df['layanan_id'] == l_id).astype(int)

    fitur_layanan = [f'layanan_{l}' for l in layanan_ids]
    X = df[fitur_layanan + ['tgl_daftar_ts', 'waktu_mulai_ts']]
    y = df['durasi_pelayanan']  # as integer (detik atau menit, konsisten)

    model = LinearRegression()
    model.fit(X, y)

    # Simpan model + metadata (fitur layanan)
    payload = {
        'model': model,
        'layanan_ids': layanan_ids,
        'features': X.columns.tolist()
    }
    with open(output_path, 'wb') as f:
        pickle.dump(payload, f)

    print("Model tersimpan di:", output_path)
