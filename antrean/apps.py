import os
from django.apps import AppConfig


class AntreanConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'antrean'

#     def ready(self):
#         # Mencegah scheduler jalan dua kali saat runserver
#         if os.environ.get('RUN_MAIN') != 'true':
#             return

#         from .scheduler.scheduler import start
#         start()
