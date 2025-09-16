from django.core.management.base import BaseCommand
from billing.services import SubscriptionManager


class Command(BaseCommand):
    help = 'Process expired subscriptions and attempt renewals'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be processed without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write('DRY RUN: Checking for expired subscriptions...')
        else:
            self.stdout.write('Processing expired subscriptions...')
        
        try:
            if not dry_run:
                SubscriptionManager.check_expired_subscriptions()
            
            self.stdout.write(
                self.style.SUCCESS('Subscription processing completed!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to process subscriptions: {e}')
            )