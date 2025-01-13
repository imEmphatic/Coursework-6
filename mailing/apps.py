import os

from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_migrate


class MailingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mailing"

    def ready(self):
        # Подключаем сигнал post_migrate, чтобы запустить планировщик после миграций
        post_migrate.connect(self.start_scheduler, sender=self)

    def start_scheduler(self, **kwargs):
        # Проверяем, что мы не находимся в процессе инициализации
        if os.environ.get("RUN_MAIN"):
            from apscheduler.schedulers.background import BackgroundScheduler
            from apscheduler.triggers.cron import CronTrigger
            from django_apscheduler.jobstores import DjangoJobStore

            from .tasks import send_mailing

            scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)

            # Проверяем, существует ли уже jobstore с псевдонимом "default"
            if "default" not in scheduler._jobstores:
                scheduler.add_jobstore(DjangoJobStore(), "default")

            scheduler.add_job(
                send_mailing,
                trigger=CronTrigger(minute=0),
                id="send_mailing",
                max_instances=1,
                replace_existing=True,
            )

            scheduler.start()
