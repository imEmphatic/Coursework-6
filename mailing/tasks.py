from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Mailing, MailingAttempt, MailingLog, Client
import logging

logger = logging.getLogger(__name__)


def send_mailing():
    current_time = timezone.now()
    mailings = Mailing.objects.filter(start_time__lte=current_time, status='running')

    for mailing in mailings:
        log_message = f"Начало отправки рассылки {mailing.id}"
        MailingLog.objects.create(mailing=mailing, status='start', message=log_message)
        logger.info(log_message)

        for client in mailing.clients.all():
            try:
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.body,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[client.email],
                    fail_silently=False,
                )
                status = True
                server_response = "Success"
                error_message = ""
            except Exception as e:
                status = False
                server_response = str(e)
                error_message = f"Ошибка при отправке: {str(e)}"
                logger.error(f"Ошибка при отправке рассылки {mailing.id} клиенту {client.email}: {str(e)}")

            MailingAttempt.objects.create(
                mailing=mailing,
                client=client,
                status=status,
                server_response=server_response,
                error_message=error_message
            )

        log_message = f"Завершение отправки рассылки {mailing.id}"
        MailingLog.objects.create(mailing=mailing, status='end', message=log_message)
        logger.info(log_message)

        # Обновление времени следующей отправки в зависимости от периодичности
        if mailing.periodicity == 'daily':
            mailing.start_time = current_time + timezone.timedelta(days=1)
        elif mailing.periodicity == 'weekly':
            mailing.start_time = current_time + timezone.timedelta(weeks=1)
        elif mailing.periodicity == 'monthly':
            mailing.start_time = current_time + timezone.timedelta(days=30)  # Примерно месяц
        elif mailing.periodicity == 'once':
            mailing.status = 'completed'

        mailing.save()