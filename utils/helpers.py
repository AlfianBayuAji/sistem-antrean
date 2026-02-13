from django.db import connection
from datetime import datetime

def query_select(table, role=None):
    role = role or {}
    sql = f"SELECT * FROM {table}"

    if "join" in role:
        sql += f" JOIN {role['join']}"
    if "where" in role:
        sql += f" WHERE {role['where']}"
    if "orderby" in role:
        sql += f" ORDER BY {role['orderby']}"
    if "limit" in role:
        sql += f" LIMIT {role['limit']}"

    with connection.cursor() as cursor:
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return rows


def rupiah(angka: int) -> str:
    return "Rp " + format(angka, ",").replace(",", ".")


def tgl_indo(tanggal):
    bulan = [
        "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]
    if isinstance(tanggal, str):
        tgl = datetime.strptime(tanggal, "%Y-%m-%d")
    else:
        tgl = tanggal
    return f"{tgl.day} {bulan[tgl.month]} {tgl.year}"


def validate_password(password: str):
    errors = []

    if len(password) < 5:
        errors.append("Password terlalu pendek. Minimal 5 karakter.")
    elif len(password) > 8:
        errors.append("Password terlalu panjang. Maksimal 8 karakter.")

    if not any(c.isalpha() for c in password):
        errors.append("Password harus mengandung setidaknya satu huruf.")

    if not any(c.isdigit() for c in password):
        errors.append("Password harus mengandung setidaknya satu angka.")

    return errors