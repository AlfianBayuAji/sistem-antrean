from antrean.models import Layanan
from antrean.ml.utils_mlr import predict_waktu
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def update_prediksi():
    print("⏳ Menghitung ulang prediksi untuk semua layanan...\n")

    layanan_all = Layanan.objects.all()

    for lay in layanan_all:
        try:
            pred = predict_waktu(lay.id)
            lay.prediksi = round(pred, 2) if pred is not None else None
            print(f"✔ {lay.layanan}: {lay.prediksi} menit")
        except Exception as e:
            print(f"❌ Error pada {lay.layanan}: {e}")

    Layanan.objects.bulk_update(layanan_all, ["prediksi"])
    print("\n✅ Selesai memperbarui semua prediksi!")

# def update_prediksi():
#     print("⏳ Menghitung ulang prediksi untuk semua layanan...\n")

#     layanan_all = Layanan.objects.all()

#     prediksi = []

#     for lay in layanan_all:
#         try:
#             pred = predict_waktu(lay.id)
#             nilai = round(pred, 1) if pred is not None else None

#             prediksi.append({
#                 "id": lay.id,
#                 "prediksi": nilai
#             })

#             print(f"✔ {lay.layanan}: {nilai} menit")

#         except Exception as e:
#             print(f"❌ Error pada {lay.layanan}: {e}")

#     # Simpan ke database (dipisah agar aman)
#     for p in prediksi:
#         Layanan.objects.filter(id=p["id"]).update(
#             prediksi=p["prediksi"]
#         )

#     print("\n✅ Selesai memperbarui semua prediksi!")
