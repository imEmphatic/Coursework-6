from django.core.management.base import BaseCommand
from mailing.tasks import send_mailing

class Command(BaseCommand):
    help = 'Отправляет все активные рассылки'

    def handle(self, *args, **options):
        send_mailing()
        self.stdout.write(self.style.SUCCESS('Рассылки успешно отправлены'))