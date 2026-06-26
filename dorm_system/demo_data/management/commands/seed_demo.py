from django.core.management.base import BaseCommand

from dorm_system.demo_data.seed import seed


class Command(BaseCommand):
    help = "Seed the dormitory demo with synthetic data (FR-14)."

    def handle(self, *args, **options):
        seed()
