from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from .models import Mahasiswa, Jurusan
from django.contrib.auth.hashers import make_password

class MahasiswaRegisterForm(forms.ModelForm):
    nama = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama lengkap'})
    )
    npm = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NPM'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    jurusan = forms.ModelChoiceField(
        queryset=Jurusan.objects.all(),
        required=True,
        empty_label="-- Pilih Jurusan --",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

    class Meta:
        model = Mahasiswa
        fields = ['nama', 'npm', 'email', 'jurusan', 'password']

    def save(self, commit=True):
        mahasiswa = super().save(commit=False)
        mahasiswa.nama = self.cleaned_data['nama']
        mahasiswa.npm = self.cleaned_data['npm']
        mahasiswa.email = self.cleaned_data['email']
        mahasiswa.jurusan = self.cleaned_data['jurusan']
        mahasiswa.password = make_password(self.cleaned_data['password'])  # hash password
        if commit:
            mahasiswa.save()
        return mahasiswa
    
# 🔹 Form Registrasi
# class User(forms.ModelForm):
#     nama = forms.CharField(
#         max_length=100, 
#         required=True,
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )
#     npm = forms.CharField(
#         max_length=20, 
#         required=True,
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )
#     email = forms.EmailField(
#         required=True,
#         widget=forms.EmailInput(attrs={'class': 'form-control'})
#     )
#     jurusan = forms.ModelChoiceField(
#         queryset=Jurusan.objects.all(),
#         required=True,
#         empty_label="-- Pilih Jurusan --",
#         widget=forms.Select(attrs={'class': 'form-select'})
#     )
#     password = forms.CharField(
#         label="Password",
#         widget=forms.PasswordInput(attrs={'class': 'form-control'})
#     )

#     class Meta:
#         model = User
#         fields = ['nama', 'npm', 'email', 'jurusan', 'password']

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.first_name = self.cleaned_data['nama']
#         user.npm = self.cleaned_data['npm']
#         user.email = self.cleaned_data['email']
#         user.jurusan = self.cleaned_data['jurusan']
#         user.password = make_password(self.cleaned_data["password"])
#         if commit:
#             user.save()
#         return user


# 🔹 Form Login
# class LoginForm(forms.Form):
#     npm = forms.CharField(
#         max_length=20,
#         widget=forms.TextInput(attrs={
#             "class": "form-control",
#             "placeholder": "Masukkan npm",
#             "id": "npm"
#         })
#     )
#     password = forms.CharField(
#         widget=forms.PasswordInput(attrs={
#             "class": "form-control",
#             "placeholder": "Masukkan password",
#             "id": "password"
#         })
#     )


class MahasiswaLoginForm(forms.Form):
    npm = forms.CharField(
        label="NPM",
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Masukkan NPM"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"})
    )
        


# 🔹 Form Login Staff/Admin (pakai username)
class StaffLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Masukkan Username"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"})
    )

    def confirm_login_allowed(self, user):
        if user.role not in ["staff", "admin"]:
            raise forms.ValidationError("Akun ini bukan petugas/admin.", code="invalid_login")