from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.utils import timezone
from .tasks import send_mailing


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Запускаем задачу каждую минуту
    scheduler.add_job(send_mailing, 'interval', minutes=1, name='send_mailing', jobstore='default')

    scheduler.start()