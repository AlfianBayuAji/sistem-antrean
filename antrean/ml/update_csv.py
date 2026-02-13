# from django.utils import timezone
# import csv
# import os

# from antrean.models import Antrean


# def append_csv_today():
#     print("📌 Update CSV dimulai")

#     # Path relatif ke file ini
#     BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#     csv_path = os.path.join(BASE_DIR, "layanan.csv")

#     now = timezone.now()
#     start = now.replace(hour=0, minute=0, second=0, microsecond=0)

#     qs = Antrean.objects.filter(
#         status="Selesai",
#         durasi_pelayanan__isnull=False,
#         waktu_selesai__gte=start,
#         waktu_selesai__lte=now
#     )

#     print(f"📅 Range: {timezone.localtime(start)} → {timezone.localtime(now)}")
#     print(f"📊 Jumlah data: {qs.count()}")

#     if not qs.exists():
#         print("⚠️ Tidak ada data untuk di-append")
#         return

#     file_exists = os.path.exists(csv_path)

#     with open(csv_path, "a", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f)

#         # Header hanya sekali
#         if not file_exists:
#             writer.writerow(["layanan", "waktu_layanan"])

#         for a in qs:
#             writer.writerow([
#                 a.layanan.layanan.lower(),
#                 a.durasi_pelayanan
#             ])

#     print(f"✅ Berhasil append ke {csv_path}")


# # Opsional: tetap bisa dijalankan manual
# if __name__ == "__main__":
#     append_csv_today()
