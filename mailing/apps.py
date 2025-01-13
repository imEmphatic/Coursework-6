from django.apps import AppConfig
from django.conf import settings


class MailingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mailing'

    def ready(self):
        import os
        if os.environ.get('RUN_MAIN'):
            from django_apscheduler.jobstores import DjangoJobStore
            from apscheduler.schedulers.background import BackgroundScheduler
            from apscheduler.triggers.cron import CronTrigger
            from .tasks import send_mailing

            scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)

            # Проверяем, существует ли уже jobstore с псевдонимом "default"
            if 'default' not in scheduler._jobstores:
                scheduler.add_jobstore(DjangoJobStore(), "default")

            scheduler.add_job(
                send_mailing,
                trigger=CronTrigger(minute=0),
                id="send_mailing",
                max_instances=1,
                replace_existing=True,
            )

            scheduler.start()