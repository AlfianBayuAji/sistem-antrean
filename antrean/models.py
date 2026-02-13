from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


# =======================
# 🧩 USER MANAGER
# =======================
class UserManager(BaseUserManager):
    def create_user(self, username, password=None, role="staff", **extra_fields):
        if not username:
            raise ValueError("Username wajib diisi")

        user = self.model(username=username, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, password, role="admin", **extra_fields)


# =======================
# 👤 USER MODEL (Admin & Staff)
# =======================
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("staff", "Staff"),
    )

    username = models.CharField(max_length=100, unique=True)
    nama = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="staff")

    # Default Django auth flags
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # untuk akses admin site
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["nama"]

    def __str__(self):
        return f"{self.nama} ({self.role})"

    # Helpers
    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_staff_role(self):
        return self.role == "staff"


# =======================
# 🎓 MAHASISWA MODEL
# =======================
class Jurusan(models.Model):
    jurusan = models.CharField(max_length=100)

    def __str__(self):
        return self.jurusan


class Mahasiswa(models.Model):
    npm = models.CharField(max_length=20, unique=True)
    nama = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    jurusan = models.ForeignKey(Jurusan, on_delete=models.SET_NULL, null=True, blank=True)
    password = models.CharField(max_length=255)  # Simpan hash, bukan plain text!

    def __str__(self):
        return f"{self.nama} ({self.npm})"


# =======================
# 🏢 LAYANAN
# =======================
class Layanan(models.Model):
    id=models.AutoField(primary_key=True)
    layanan = models.CharField(max_length=100)
    proses = models.IntegerField(default=0)  # estimasi waktu (menit/detik) KEMUNGKINAN BAKALAN DIHILANGKAN
    prediksi = models.FloatField(null=True, blank=True)  # hasil dari MLR
    
    def __str__(self):
        return self.layanan


# =======================
# 🔢 ANTREAN
# =======================
class Antrean(models.Model):
    mahasiswa = models.ForeignKey(Mahasiswa, on_delete=models.CASCADE)
    layanan = models.ForeignKey(Layanan, on_delete=models.CASCADE)
    nomor_antrean = models.CharField(max_length=20)
    status = models.CharField(max_length=50, default="Menunggu")
    panggil = models.BooleanField(default=False)
    tgl_daftar = models.DateTimeField(default=timezone.now)

    waktu_mulai = models.DateTimeField(null=True, blank=True)
    waktu_selesai_otomatis = models.DateTimeField(null=True, blank=True)

    # ================= NEW FIELDS ================= #

    # waktu selesai real
    waktu_selesai = models.DateTimeField(null=True, blank=True)  # NEW

    # durasi pelayanan real
    durasi_pelayanan = models.IntegerField(null=True, blank=True)  # NEW

    # prediksi dari MLR
    prediksi_mlr = models.IntegerField(null=True, blank=True)  # NEW

    # error prediksi vs real
    error_mlr = models.IntegerField(null=True, blank=True)  # NEW

    # ================================================= #

    def __str__(self):
        return f"{self.nomor_antrean} - {self.mahasiswa.nama} - {self.layanan.layanan}"

