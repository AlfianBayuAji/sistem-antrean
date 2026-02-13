from django.core import signing

def generate_reset_token(email):
    return signing.dumps(email)

def verify_reset_token(token, max_age=900):  # 15 menit
    try:
        return signing.loads(token, max_age=max_age)
    except signing.BadSignature:
        return None
