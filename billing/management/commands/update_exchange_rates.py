from django.core.management.base import BaseCommand
from billing.currency import CurrencyConverter


class Command(BaseCommand):
    help = 'Update exchange rates from external API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if rates were recently updated',
        )

    def handle(self, *args, **options):
        self.stdout.write('Updating exchange rates...')
        
        try:
            CurrencyConverter.update_exchange_rates()
            self.stdout.write(
                self.style.SUCCESS('Exchange rates updated successfully!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to update exchange rates: {e}')
            )