from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Создание суперпользователя автоматически (если его нет)'

    def handle(self, *args, **kwargs):
        username = "admin"
        password = "Admin12345"
        email = "admin@example.com"

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f'Суперпользователь {username} создан'))
        else:
            self.stdout.write(self.style.WARNING(f'Суперпользователь {username} уже существует'))