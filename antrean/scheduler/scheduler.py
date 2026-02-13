# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.cron import CronTrigger

# from antrean.ml.train_model import train_mlr
# from antrean.ml.update_csv import append_csv_today
# from antrean.ml.update_prediksi import update_prediksi

# scheduler = BackgroundScheduler(timezone="Asia/Jakarta")


# def start():
#     if scheduler.running:
#         return

#     scheduler.add_job(
#         append_csv_today,
#         CronTrigger(hour=4, minute=0),
#         id="update_csv_job",
#         replace_existing=True
#     )

#     scheduler.add_job(
#         train_mlr,
#         CronTrigger(hour=1, minute=0),
#         id="train_model_job",
#         replace_existing=True
#     )

#     scheduler.add_job(
#         update_prediksi,
#         CronTrigger(hour=1, minute=10),
#         id="update_prediksi_job",
#         replace_existing=True
#     )

#     scheduler.start()
