from antrean.models import Layanan
from .predict import predict_by_layanan

def update_all_prediksi():
    for layanan in Layanan.objects.all():
        layanan.prediksi = predict_by_layanan(layanan.layanan)
        layanan.save()
