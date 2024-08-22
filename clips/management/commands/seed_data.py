from django.core.management.base import BaseCommand
from django_seed import Seed
from clips.models import Clip
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Seed data for clips app'

    def handle(self, *args, **options):
        seeder = Seed.seeder()

        # 50 Authors
        seeder.add_entity(User, 10, {
            'is_staff': False,
            'is_superuser': False
        })

        # 100 Clips
        seeder.add_entity(Clip, 10, {
            'author': lambda x: User.objects.get(pk=seeder.faker.random_int(min=1, max=10)),
            'time_start': lambda x: seeder.faker.date(),
            'date': lambda x: seeder.faker.date(),
            'transcript': lambda x: seeder.faker.paragraph(),
            'entities': '',
            'keywords': '',
            'summary': '',
        })

        seeder.execute()
        self.stdout.write(self.style.SUCCESS('Data seeded successfully'))

        