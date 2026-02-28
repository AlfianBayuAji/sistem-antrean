from antrean.ml.utils_mlr import predict_waktu
import datetime
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from .decorators import mahasiswa_required
from datetime import timedelta
from django.http import JsonResponse
from .ml import train_model
from django.db.models import Max
from django.db import models
from django.db.models import Sum
from django.db.models import Q
from django.core.paginator import Paginator
import csv
from antrean.ml.update import update_all_prediksi
from django.shortcuts import redirect
from django.contrib.auth.hashers import make_password
from .utils import verify_reset_token
from .models import Mahasiswa
from django.shortcuts import render
from django.core.mail import send_mail
from .models import Mahasiswa
from .utils import generate_reset_token
from django.utils.timezone import now

from antrean.ml.train_mlr_db import train_mlr_by_date
from antrean.ml.update_prediksi import update_prediksi


from .models import Antrean, Mahasiswa, Layanan, User, Jurusan
from .forms import MahasiswaLoginForm, StaffLoginForm, MahasiswaRegisterForm

# coba
from django.http import JsonResponse

# ==========================
# 🔹 Halaman utama / landing
# ==========================
def index(request):
    return render(request, 'antrean/index.html')


# ==========================
# 🔹 Register Mahasiswa
# ==========================
def register(request):
    if request.method == 'POST':
        form = MahasiswaRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('antrean:login_mahasiswa')
    else:
        form = MahasiswaRegisterForm()
    return render(request, 'antrean/register.html', {'form': form})


# ==========================
# 🔹 Login & Logout
# ==========================

def mahasiswa_login_view(request):
    if request.method == "POST":
        form = MahasiswaLoginForm(request.POST)
        if form.is_valid():
            npm = form.cleaned_data.get("npm")
            password = form.cleaned_data.get("password")

            try:
                mahasiswa = Mahasiswa.objects.get(npm=npm)
                if check_password(password, mahasiswa.password):
                    # Simpan sesi login
                    request.session["mahasiswa_id"] = mahasiswa.id
                    request.session["mahasiswa_nama"] = mahasiswa.nama
                    request.session["mahasiswa_role"] = "mahasiswa"
                    messages.success(request, f"Selamat datang, {mahasiswa.nama}!")
                    return redirect("antrean:dashboard_mahasiswa")
                else:
                    messages.error(request, "Password salah.")
            except Mahasiswa.DoesNotExist:
                messages.error(request, "NPM tidak ditemukan.")
    else:
        form = MahasiswaLoginForm()

    return render(request, "antrean/login1.html", {"form": form})

def login_staff(request):
    if request.user.is_authenticated:
        return redirect('antrean:dashboard_staff')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.role in ["staff", "admin"]:
                print("DEBUG ROLE:", user.role)
                login(request, user)
                return redirect("antrean:dashboard_staff")
            else:
                messages.error(request, "Anda tidak memiliki akses sebagai staff/admin.")
        else:
            messages.error(request, "Username atau password salah.")

    return render(request, "staff/staff_login.html")



def logout_mahasiswa(request):
    request.session.flush()  # hapus hanya session mahasiswa
    return redirect("antrean:index")

def logout_staff(request):
    logout(request)
    return redirect("antrean:login_staff")

# ==========================
# 🔹 Dashboard Mahasiswa
# ==========================
# def dashboard_mahasiswa(request):
#     mahasiswa_id = request.session.get("mahasiswa_id")
#     print("Session mahasiswa_id:", mahasiswa_id)

#     if not mahasiswa_id:
#         print("Session tidak ditemukan, redirect ke login.")
#         return redirect("antrean:login_mahasiswa")

#     mahasiswa = Mahasiswa.objects.get(id=mahasiswa_id)
#     print("Masuk ke dashboard:", mahasiswa.nama)
#     return render(request, "antrean/dashboard_mahasiswa.html", {"mahasiswa": mahasiswa})

def dashboard_mahasiswa(request):
    mahasiswa_id = request.session.get("mahasiswa_id")

    if not mahasiswa_id:
        return redirect("antrean:login_mahasiswa")

    mahasiswa = Mahasiswa.objects.get(id=mahasiswa_id)

    # antrean aktif mahasiswa
    antrean_saya = (
        Antrean.objects
        .filter(
            mahasiswa=mahasiswa,
            status="Menunggu"
        )
        .select_related("layanan")
        .first()
    )

    antrean_di_depan = []
    jumlah_di_depan = 0
    prediksi_layanan = 0
    estimasi_waktu_tunggu = 0

    if antrean_saya and antrean_saya.layanan.prediksi:
        prediksi_layanan = int(antrean_saya.layanan.prediksi)

        # ============================
        # VIRTUAL QUEUE (SJF + FIFO)
        # ============================
        antrean_di_depan = (
            Antrean.objects
            .filter(status="Menunggu")
            .filter(
                Q(layanan__prediksi__lt=prediksi_layanan) |
                Q(
                    layanan__prediksi=prediksi_layanan,
                    tgl_daftar__lt=antrean_saya.tgl_daftar
                )
            )
            .select_related("layanan")
            .order_by("layanan__prediksi", "tgl_daftar")
        )

        jumlah_di_depan = antrean_di_depan.count()

        estimasi_waktu_tunggu = sum(
            int(a.layanan.prediksi or 0)
            for a in antrean_di_depan
        )

    context = {
        "mahasiswa": mahasiswa,
        "antrean_saya": antrean_saya,
        "jumlah_di_depan": jumlah_di_depan,
        "prediksi_layanan": prediksi_layanan,
        "estimasi_waktu_tunggu": estimasi_waktu_tunggu,
    }

    return render(request, "antrean/dashboard_mahasiswa.html", context)




# ==========================
# 🔹 Ambil Antrean
# ==========================
# @mahasiswa_required
# def ambil_antrean(request):
#     layanan_list = Layanan.objects.all().order_by('-id')
#     alert = request.GET.get('alert', None)
#     return render(request, 'antrean/ambil_antrean.html', {
#         'layanan_list': layanan_list,
#         'alert': alert
#     })
@mahasiswa_required
def ambil_antrean(request):

    mahasiswa_id = request.session.get("mahasiswa_id")
    mahasiswa = Mahasiswa.objects.get(id=mahasiswa_id)

    # 🚫 Kalau masih punya antrean aktif
    if Antrean.objects.filter(
        mahasiswa=mahasiswa,
        status__in=["Menunggu", "Dipanggil"]
    ).exists():

        messages.warning(
            request,
            "Anda masih memiliki antrean aktif. "
            "Selesaikan antrean terlebih dahulu sebelum mengambil layanan lain."
        )
        return redirect("antrean:dashboard_mahasiswa")

    # =========================
    # KODE LAMA
    # =========================
    layanan_list = Layanan.objects.all()
    layanan_with_prediksi = []

    for l in layanan_list:
        layanan_with_prediksi.append({
            "id": l.id,
            "nama": l.layanan,
            "prediksi": l.prediksi,
        })

    return render(
        request,
        "antrean/ambil_antrean.html",
        {
            "layanan_list": layanan_with_prediksi,
        }
    )


# @login_required(login_url='antrean:login_mahasiswa')
def ambil_proses(request, id):
    # 🔹 Cek apakah mahasiswa sudah login
    mahasiswa_id = request.session.get("mahasiswa_id")
    if not mahasiswa_id:
        messages.error(request, "Silakan login terlebih dahulu.")
        return redirect('antrean:login_mahasiswa')

    # 🔹 Ambil data mahasiswa dari session
    try:
        mahasiswa = Mahasiswa.objects.get(id=mahasiswa_id)
    except Mahasiswa.DoesNotExist:
        messages.error(request, "Data mahasiswa tidak ditemukan.")
        return redirect('antrean:login_mahasiswa')

    # 🔹 Ambil layanan yang dipilih
    layanan = get_object_or_404(Layanan, id=id)

    # 🔹 Buat kode antrean unik
    kode_antrean = f"ANT{timezone.now().strftime('%y%m%d')}{layanan.id}{str(mahasiswa.id)[-2:]}"

    # 🔹 Simpan antrean baru
    Antrean.objects.create(
        layanan=layanan,
        mahasiswa=mahasiswa,
        nomor_antrean=kode_antrean,
        status="Menunggu",
        tgl_daftar=timezone.now(),
    )

    messages.success(request, f"Antrean untuk {layanan.layanan} berhasil diambil!")
    return redirect('antrean:dashboard_mahasiswa')




# ==========================
# 🔹 Lihat daftar antrean (Staff/Admin)
# ==========================

def lihat_antrian(request):
    antrean = (
        Antrean.objects
        .select_related('mahasiswa', 'layanan')
        .filter(status__iexact='menunggu')
        .order_by('-panggil', 'layanan__prediksi', 'id')
    )
    return render(request, 'antrean/lihat_antrian.html', {'antrean': antrean})

def status_antrean(request, antre_id):
    antre = get_object_or_404(Antrean, id=antre_id)

    # Hitung estimasi selesai otomatis
    if antre.waktu_mulai and antre.layanan:
        antre.waktu_selesai_otomatis = antre.waktu_mulai + timezone.timedelta(
            seconds=antre.layanan.proses
        )

    return render(request, "status_antrean.html", {"antre": antre})


# ==========================
# 🔹 API: nomor antrean aktif
# ==========================
def get_nomor_antrian(request):
    antrean_aktif = Antrean.objects.filter(status__iexact="proses").order_by('-id').first()
    nomor = antrean_aktif.antrean if antrean_aktif else "Tidak ada antrean"
    return HttpResponse(nomor)


def jurusan_list(request):
    jurusan_list = Jurusan.objects.all().order_by('-id')
    return render(request, 'staff/sidebar_staff/jurusan_list.html', {
        'jurusan_list': jurusan_list
    })

def tambah_jurusan(request):
    if request.method == "POST":
        nama = request.POST.get("jurusan")

        if nama.strip() == "":
            messages.error(request, "Nama jurusan tidak boleh kosong.")
        else:
            Jurusan.objects.create(jurusan=nama)
            messages.success(request, "Berhasil menambah jurusan.")
            return redirect("antrean:jurusan_list")

    return render(request, "staff/sidebar_staff/jurusan_tambah.html")
def edit_jurusan(request, id):
    jurusan = get_object_or_404(Jurusan, id=id)

    if request.method == "POST":
        nama = request.POST.get("jurusan")

        if nama.strip() == "":
            messages.error(request, "Nama jurusan tidak boleh kosong.")
        else:
            jurusan.jurusan = nama
            jurusan.save()
            messages.success(request, "Berhasil mengedit jurusan.")
            return redirect("antrean:jurusan_list")

    return render(request, "staff/sidebar_staff/jurusan_edit.html", {
        'jurusan': jurusan
    })

def hapus_jurusan(request, id):
    jurusan = get_object_or_404(Jurusan, id=id)
    jurusan.delete()
    messages.success(request, "Berhasil menghapus jurusan.")
    return redirect("antrean:jurusan_list")

def layanan_list(request):
    data = Layanan.objects.all().order_by('-id')
    return render(request, 'staff/sidebar_staff/layanan_list.html', {'data': data})


# def layanan_create(request):
#     if request.method == 'POST':
#         layanan = request.POST.get('layanan')
#         proses = request.POST.get('proses')

#         Layanan.objects.create(
#             layanan=layanan,
#             proses=proses
#         )
#         messages.success(request, "Berhasil menambah data!")
#         return redirect('antrean:layanan_list')

#     return render(request, 'staff/sidebar_staff/layanan_edit.html', {'mode': 'tambah'})


# def layanan_edit(request, id):
#     layanan_obj = get_object_or_404(Layanan, id=id)

#     if request.method == 'POST':
#         layanan_obj.layanan = request.POST.get('layanan')
#         layanan_obj.proses = request.POST.get('proses')
#         layanan_obj.save()

#         messages.success(request, "Berhasil mengedit data!")
#         return redirect('antrean:layanan_list')

#     return render(request, 'staff/sidebar_staff/layanan_edit.html', {
#         'mode': 'edit',
#         'layanan': layanan_obj
#     })


# from django.views.decorators.http import require_POST

# @require_POST
# def layanan_delete(request, id):
#     layanan_obj = get_object_or_404(Layanan, id=id)
#     layanan_obj.delete()
#     messages.success(request, "Berhasil menghapus data!")
#     return redirect('antrean:layanan_list')


def petugas_list(request):
    petugas = User.objects.filter(role="staff").order_by("-id")
    return render(request, "staff/sidebar_staff/petugas_list.html", {"petugas": petugas})


# =========================
# TAMBAH PETUGAS
# =========================
def petugas_create(request):
    if request.method == "POST":
        nama = request.POST.get("nama")
        username = request.POST.get("username")
        password = request.POST.get("password")

        User.objects.create_user(
            username=username,
            password=password,
            role="staff",
            nama=nama
        )
        messages.success(request, "Berhasil menambah data!")
        return redirect("antrean:petugas_list")

    return render(request, "staff/sidebar_staff/petugas_tambah.html")


# =========================
# EDIT PETUGAS
# =========================
def petugas_edit(request, id):
    petugas = get_object_or_404(User, id=id)

    if request.method == "POST":
        petugas.nama = request.POST.get("nama")
        petugas.username = request.POST.get("username")

        new_password = request.POST.get("password")
        if new_password:
            petugas.set_password(new_password)

        petugas.save()
        messages.success(request, "Berhasil mengedit data!")
        return redirect("petugas_list")

    return render(request, "staff/sidebar_staff/petugas_edit.html", {"petugas": petugas})


# =========================
# HAPUS PETUGAS
# =========================
def petugas_delete(request, id):
    if request.method != "POST":
        messages.error(request, "Penghapusan hanya boleh lewat tombol Hapus!")
        return redirect("antrean:petugas_list")

    petugas = get_object_or_404(User, id=id)
    petugas.delete()
    messages.success(request, "Berhasil menghapus data!")
    return redirect("antrean:petugas_list")

def mahasiswa_list(request):
    qs = Mahasiswa.objects.select_related("jurusan").order_by("-id")

    paginator = Paginator(qs, 10)  # 10 per halaman
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "staff/sidebar_staff/mahasiswa_list.html",
        {"page_obj": page_obj}
    )


# CREATE
def mahasiswa_create(request):
    jurusan = Jurusan.objects.all()

    if request.method == "POST":
        nama = request.POST["nama"]
        npm = request.POST["npm"]
        jurusan_id = request.POST["jurusan"]
        email = request.POST["email"]
        password = request.POST["password"]

        Mahasiswa.objects.create(
            nama=nama,
            npm=npm,
            jurusan=Jurusan.objects.get(id=jurusan_id),
            email=email,
            password=make_password(password),
        )

        messages.success(request, "Berhasil menambahkan data mahasiswa!")
        return redirect("antrean:mahasiswa_list")

    return render(request, "staff/sidebar_staff/mahasiswa_tambah.html", {"jurusan": jurusan})


# EDIT
def mahasiswa_edit(request, id):
    mahasiswa = get_object_or_404(Mahasiswa, id=id)
    jurusan = Jurusan.objects.all()

    if request.method == "POST":
        mahasiswa.nama = request.POST["nama"]
        mahasiswa.npm = request.POST["npm"]
        mahasiswa.jurusan_id = request.POST["jurusan"]
        mahasiswa.email = request.POST["email"]

        if request.POST.get("password"):
            mahasiswa.password = make_password(request.POST["password"])

        mahasiswa.save()

        messages.success(request, "Berhasil mengedit data mahasiswa!")
        return redirect("antrean:mahasiswa_list")

    return render(request, "staff/sidebar_staff/mahasiswa_edit.html", {
        "mahasiswa": mahasiswa,
        "jurusan": jurusan,
    })


# DELETE
def mahasiswa_delete(request, id):
    mahasiswa = get_object_or_404(Mahasiswa, id=id)
    mahasiswa.delete()
    messages.success(request, "Berhasil menghapus data mahasiswa!")
    return redirect("antrean:mahasiswa_list")

def laporan(request):

    start = request.GET.get("start")
    end = request.GET.get("end")

    # ✅ Kalau tanggal kosong
    if not start or not end:
        messages.warning(
            request,
            "Silakan pilih rentang tanggal terlebih dahulu."
        )

        context = {
            "antrean": None,
            "total_masuk": 0,
            "total_terlewat": 0,
            "total_selesai": 0,
        }

        return render(
            request,
            "staff/sidebar_staff/laporan.html",
            context
        )

    # =========================
    # QUERY HISTORI
    # =========================
    antrean_qs = (
        Antrean.objects
        .exclude(status="Menunggu")
        .select_related("mahasiswa", "layanan", "mahasiswa__jurusan")
        .filter(tgl_daftar__date__gte=start)
        .filter(tgl_daftar__date__lte=end)
    )

    antrean_list = antrean_qs.order_by("-tgl_daftar")

    # ✅ Pagination 10 data
    paginator = Paginator(antrean_list, 10)
    page_number = request.GET.get("page")
    antrean = paginator.get_page(page_number)

    total_masuk = antrean_qs.count()
    total_terlewat = antrean_qs.filter(status="Terlewat").count()
    total_selesai = antrean_qs.filter(status="Selesai").count()

    context = {
        "antrean": antrean,
        "total_masuk": total_masuk,
        "total_terlewat": total_terlewat,
        "total_selesai": total_selesai,
    }

    return render(
        request,
        "staff/sidebar_staff/laporan.html",
        context
    )

def antrean_list(request):

    antrean_proses = (
        Antrean.objects
        .filter(status="Proses")
        .select_related("mahasiswa", "layanan")
    )

    antrean_menunggu_qs = (
        Antrean.objects
        .filter(status="Menunggu")
        .select_related("mahasiswa", "layanan")
        .order_by("layanan__prediksi", "tgl_daftar")  # SJF
    )

    # ===== PAGINATION (10 DATA PER HALAMAN) =====
    paginator = Paginator(antrean_menunggu_qs, 10)
    page_number = request.GET.get("page")
    antrean_menunggu = paginator.get_page(page_number)
    # ==========================================

    context = {
        "antrean_proses": antrean_proses,
        "antrean_menunggu": antrean_menunggu,
    }

    return render(
        request,
        "staff/sidebar_staff/antrean_list.html",
        context
    )


# def antrean_list(request):
#     antrean_list =(
#                 Antrean.objects
#         .filter(status__in=["Menunggu", "Dipanggil"])  # hanya tampil yg belum selesai
#         .order_by('waktu_selesai_otomatis')
#     )
#     for a in antrean_list:
#         if (
#             a.status == "Dipanggil" and
#             a.waktu_selesai_otomatis is not None and
#             timezone.now() >= a.waktu_selesai_otomatis
#         ):
#             a.status = "Selesai"
#             a.save()

#     return render(request, "staff/sidebar_staff/antrean_list.html", {
#         "antrean_list": antrean_list
#     })



# def antrean_list(request):
#     alert = request.GET.get("alert")

#     # Query sesuai PHP:
#     antrean = (
#         Antrean.objects
#         .select_related('mahasiswa', 'layanan')
#         .filter(status__iexact='menunggu')
#         .order_by('-panggil', 'layanan__proses', 'id')
#     )

#     context = {
#         "alert": alert,
#         "antrean_list": antrean,
#         "user_level": request.session.get("level"),  # pengganti $_SESSION['level']
#     }

#     return render(request, "staff/sidebar_staff/antrean_list.html", context)

# def panggil_antrean(request, id):
#     antrean = get_object_or_404(Antrean, id=id)

#     antrean.status = "Dipanggil"
#     antrean.panggil = True
#     antrean.waktu_mulai = timezone.now()

#     # waktu selesai otomatis berdasarkan durasi layanan
#     antrean.waktu_selesai_otomatis = antrean.waktu_mulai + timedelta(
#         minutes=antrean.layanan.proses
#     )

#     antrean.save()

#     return redirect("antrean:antrean_list")


def panggil_antrean(request):

    now = timezone.now()

    aksi_lewati = request.GET.get("lewati")

    # ===============================
    # 1. SELESAIKAN ANTREAN PROSES
    # ===============================
    current = Antrean.objects.filter(status="Proses").first()

    if current and current.waktu_mulai:
        current.waktu_selesai = now

        durasi = (current.waktu_selesai - current.waktu_mulai).total_seconds() / 60
        current.durasi_pelayanan = round(durasi)

        current.prediksi_mlr = current.layanan.prediksi
        current.error_mlr = (
            current.durasi_pelayanan - current.prediksi_mlr
        )

        current.status = "Selesai"
        current.save()

    # ===============================
    # 2. AMBIL ANTREAN BERIKUTNYA (SJF)
    # ===============================
    next_antrean = (
        Antrean.objects
        .filter(status="Menunggu")
        .select_related("layanan")
        .order_by("layanan__prediksi", "tgl_daftar")
        .first()
    )

    if next_antrean:

        if aksi_lewati:
            # 👉 Kalau klik LEWATI
            next_antrean.status = "Terlewat"
            next_antrean.save()

        else:
            # 👉 Normal (Panggil)
            next_antrean.status = "Proses"
            next_antrean.waktu_mulai = now
            next_antrean.save()

    return redirect("antrean:antrean_list")

def lewatin_semua(request):

    today = now().date()

    total = Antrean.objects.filter(
        status="Menunggu",
        tgl_daftar__date=today
    ).update(status="Terlewat")

    if total > 0:
        messages.warning(request, f"{total} antrean hari ini dilewati.")
    else:
        messages.info(request, "Tidak ada antrean hari ini.")

    return redirect("antrean:antrean_list")

def panggil_berikutnya(request):
    # Tutup antrean yang sedang berjalan jika ada
    antre_sedang = Antrean.objects.filter(status="Dipanggil").first()
    if antre_sedang:
        antre_sedang.waktu_selesai = timezone.now()
        antre_sedang.durasi_pelayanan = int((antre_sedang.waktu_selesai - antre_sedang.waktu_mulai).total_seconds())

        # Hitung error MLR (jika ada prediksi)
        if antre_sedang.prediksi_mlr:
            antre_sedang.error_mlr = antre_sedang.durasi_pelayanan - antre_sedang.prediksi_mlr

        antre_sedang.status = "Selesai"
        antre_sedang.save()

    # Ambil antrean berikutnya
    antre_selanjutnya = Antrean.objects.filter(status="Menunggu").order_by("tgl_daftar").first()

    if antre_selanjutnya:
        antre_selanjutnya.status = "Dipanggil"
        antre_selanjutnya.panggil = True
        antre_selanjutnya.waktu_mulai = timezone.now()
        antre_selanjutnya.save()

        return JsonResponse({
            "status": True,
            "nomor": antre_selanjutnya.nomor_antrean,
            "nama": antre_selanjutnya.mahasiswa.nama,
            "layanan": antre_selanjutnya.layanan.layanan,
        })

    return JsonResponse({"status": False, "message": "Tidak ada antrean"})


def lewati_antrean(request, id):
    antrean = get_object_or_404(Antrean, id=id)
    antrean.status = "Terlewat"
    antrean.panggil = False
    antrean.save()

    return redirect("antrean:antrean_list")

def selesai_antrean(request, id):
    antrean = get_object_or_404(Antrean, id=id)
    antrean.status = "selesai"
    antrean.panggil = False
    antrean.save()

    return redirect("antrean:antrean_list")


def dashboard(request):
    context = {
        "total_layanan": Layanan.objects.count(),
        "total_mahasiswa": Mahasiswa.objects.count(),
        "total_jurusan": Jurusan.objects.count(),
        "total_antrean": Antrean.objects.count(),
        "total_terlewat": Antrean.objects.filter(status="Terlewat").count(),
        "total_selesai": Antrean.objects.filter(status="Selesai").count(),
    }
    return render(request, "staff/sidebar_staff/dashboard_staff.html", context)

def antrean_status_api(request):
    antrean = (
        Antrean.objects
        .filter(status__in=["Menunggu", "Dipanggil"])
        .order_by('nomor_antrean')
    )

    data = []
    for a in antrean:
        data.append({
            "id": a.id,
            "nomor_antrean": a.nomor_antrean,
            "nama": a.mahasiswa.nama,
            "npm": a.mahasiswa.npm,
            "jurusan": a.mahasiswa.jurusan.jurusan,
            "layanan": a.layanan.layanan,
            "status": a.status,
            "waktu_selesai_otomatis": a.waktu_selesai_otomatis.timestamp() if a.waktu_selesai_otomatis else None
        })

    return JsonResponse({"data": data})

def antrean_history_json(request):
    antrean = Antrean.objects.all().order_by('-id')
    data = []

    for a in antrean:
        data.append({
            'npm': a.mahasiswa.npm,
            'nama': a.mahasiswa.nama,
            'jurusan': a.mahasiswa.jurusan.jurusan,
            'layanan': a.layanan.layanan,
            'status': "Proses.." if a.status == "Dipanggil" else a.status,
        })

    return JsonResponse({'data': data})


# from django.contrib.admin.views.decorators import staff_member_required
# from django.http import HttpResponse
# from .ml.train_model import train_model

# @staff_member_required
# def retrain(request):
#     train_model()
#     return HttpResponse("Model berhasil diperbarui!")

def export_layanan_csv(request):

    # =========================
    # BASE QUERY (HISTORI SAJA)
    # =========================
    antrean_qs = (
        Antrean.objects
        .exclude(status="Menunggu")
        .select_related("layanan")
    )

    # =========================
    # FILTER TANGGAL
    # =========================
    start = request.GET.get("start")
    end = request.GET.get("end")

    if start:
        antrean_qs = antrean_qs.filter(tgl_daftar__date__gte=start)

    if end:
        antrean_qs = antrean_qs.filter(tgl_daftar__date__lte=end)

    # =========================
    # RESPONSE CSV
    # =========================
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="layanan.csv"'

    writer = csv.writer(response)

    # HEADER (SESUI TRAINING)
    writer.writerow(["layanan", "waktu_layanan"])

    for a in antrean_qs:
        if a.waktu_selesai:
            durasi = int(
                (a.waktu_selesai - a.tgl_daftar).total_seconds() / 60
            )

            # Hindari durasi nol / negatif
            if durasi > 0:
                writer.writerow([
                    a.layanan.layanan.lower(),
                    durasi
                ])

    return response

# def update_prediksi(request):
#     update_all_prediksi()
#     messages.success(request, "Prediksi layanan berhasil diperbarui.")
#     return redirect("antrean:layanan_list")

@login_required
def retrain_model(request):
    if request.method == "POST":
        start = request.POST.get("start")
        end = request.POST.get("end")

        # ✅ Validasi jika tanggal kosong
        if not start or not end:
            messages.warning(
                request,
                "Silakan pilih tanggal awal dan tanggal akhir terlebih dahulu."
            )
            return redirect("antrean:retrain_model")

        try:
            total = train_mlr_by_date(start, end)

            MIN_DATA = 100
            if total < MIN_DATA:
                messages.error(
                    request,
                    f"Retrain dibatalkan. Minimal {MIN_DATA} data, "
                    f"namun hanya tersedia {total} data."
                )
                return redirect("antrean:retrain_model")

            update_prediksi()
            update_all_prediksi()

            messages.success(
                request,
                f"Retrain berhasil menggunakan {total} data antrean."
            )

        except Exception as e:
            messages.error(request, str(e))

        return redirect("antrean:retrain_model")

    return render(request, "staff/sidebar_staff/retrain_model.html")

def reset_password(request, token):
    email = verify_reset_token(token)

    if not email:
        return render(request, "token_invalid.html")

    mahasiswa = Mahasiswa.objects.filter(email=email).first()
    if not mahasiswa:
        return render(request, "token_invalid.html")

    if request.method == "POST":
        password = request.POST.get("password")
        mahasiswa.password = make_password(password)
        mahasiswa.save()
        return redirect("antrean:login_mahasiswa")

    return render(request, "antrean/reset_password.html")


def lupa_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        mahasiswa = Mahasiswa.objects.filter(email=email).first()
        if mahasiswa:
            token = generate_reset_token(email)
            link = request.build_absolute_uri(
                f"/reset-password/{token}/"
            )

            send_mail(
                subject="Reset Password Akun Anda",
                message=f"Klik link berikut untuk reset password:\n{link}",
                from_email="noreply@sistem-antrean.ac.id",
                recipient_list=[email],
            )

        # Apapun hasilnya, tampil sukses
        return render(request, "antrean/lupa_password_done.html")

    return render(request, "antrean/lupa_password.html")

def list_antrean_public(request):
    query = request.GET.get('q')

    # QUERY UTAMA
    data = (
        Antrean.objects
        .select_related('mahasiswa', 'layanan')
        .filter(status__iexact='menunggu')
        .order_by('-panggil', 'layanan__prediksi', 'id')
    )

    # SEARCH
    if query:
        data = data.filter(
            Q(nomor_antrean__icontains=query) |
            Q(mahasiswa__npm__icontains=query) |
            Q(mahasiswa__nama__icontains=query)
        )

    # PAGINATION (10 per halaman)
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "antrean/list_antrean_public.html", {
        "page_obj": page_obj,
        "query": query
    })
