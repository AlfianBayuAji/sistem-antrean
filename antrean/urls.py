from django.urls import path
from . import views
from .views import StaffLoginForm

app_name = 'antrean'  # namespace

urlpatterns = [
    # 🔹 Halaman utama
    path('', views.index, name='index'),

    # 🔹 Autentikasi
    path('login/', views.mahasiswa_login_view, name='login_mahasiswa'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_mahasiswa, name='logout'),

    # 🔹 Dashboard Mahasiswa
    path('dashboard/', views.dashboard_mahasiswa, name='dashboard_mahasiswa'),
    path('beranda/', views.dashboard_mahasiswa, name='beranda'),

    # 🔹 Ambil antrean
    path('ambil-antrean/', views.ambil_antrean, name='ambil_antrean'),
    path('ambil-proses/<int:id>/', views.ambil_proses, name='ambil_proses'),

    # 🔹 Lihat daftar antrean
    path('lihat-antrian/', views.lihat_antrian, name='lihat_antrian'),
    # path('list-antrian/', views.lihat_antrian, name='list_antrian'),

    # 🔹 API Nomor antrean aktif
    path('nomor-antrian/', views.get_nomor_antrian, name='get_nomor_antrian'),

    # 🔹 Dashboard Staff/Admin
    path('login-staff/', views.login_staff, name='login_staff'),
    path('logout-staff/', views.logout_staff, name='logout_staff'),
    path('dashboard-staff/', views.dashboard, name='dashboard_staff'),

    # 🔹 Manajemen Jurusan
    path('jurusan/', views.jurusan_list, name='jurusan_list'),
    path('jurusan/tambah/', views.tambah_jurusan, name='tambah_jurusan'),
    path('jurusan/edit/<int:id>/', views.edit_jurusan, name='edit_jurusan'),
    path('jurusan/hapus/<int:id>/', views.hapus_jurusan, name='hapus_jurusan'),

    # 🔹 Manajemen Layanan
    path('layanan/', views.layanan_list, name='layanan_list'),
    # path('layanan/tambah/', views.layanan_create, name='layanan_create'),
    # path('layanan/edit/<int:id>/', views.layanan_edit, name='layanan_edit'),
    # path('layanan/hapus/<int:id>/', views.layanan_delete, name='layanan_delete'),

    # 🔹 Manajemen Petugas
    path("petugas/", views.petugas_list, name="petugas_list"),
    path("petugas/tambah/", views.petugas_create, name="petugas_create"),
    path("petugas/edit/<int:id>/", views.petugas_edit, name="petugas_edit"),
    path("petugas/hapus/<int:id>/", views.petugas_delete, name="petugas_delete"),

    # 🔹 Manajemen Mahasiswa
    path("mahasiswa/", views.mahasiswa_list, name="mahasiswa_list"),
    path("mahasiswa/tambah/", views.mahasiswa_create, name="mahasiswa_create"),
    path("mahasiswa/edit/<int:id>/", views.mahasiswa_edit, name="mahasiswa_edit"),
    path("mahasiswa/hapus/<int:id>/", views.mahasiswa_delete, name="mahasiswa_delete"),

    #🔹 Manajemen Antrian
    path('laporan/', views.laporan, name='laporan'),
    path("laporan/export/csv/", views.export_layanan_csv, name="export_laporan_csv"),

    path('antrian/', views.antrean_list, name='antrean_list'),
    path('antrean/panggil/', views.panggil_antrean, name='panggil_antrean'),
    path('antrean/lewati/<int:id>/', views.lewati_antrean, name='lewati_antrean'),
    path('antrean/selesai/<int:id>/', views.selesai_antrean, name='selesai_antrean'),

    path("api/antrean-status/", views.antrean_status_api, name="api_antrean_status"),
    path("history/json/", views.antrean_history_json, name="antrean_history_json"),

    path('update-prediksi/', views.update_prediksi, name='update_prediksi'),

    path("retrain-model/", views.retrain_model, name="retrain_model"),

    path("lupa-password/", views.lupa_password, name="lupa_password"),
    path("reset-password/<str:token>/", views.reset_password, name="reset_password"),
    path('antrean-public/', views.list_antrean_public, name='list_antrean_public'),
    path("lewatin-semua/", views.lewatin_semua, name="lewatin_semua"),
]
