from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Создаёт суперпользователя, если его ещё нет"

    def handle(self, *args, **options):
        username = "andrey"
        email = "andrey.norsi@gmail.com"
        password = "admin123"  # можешь заменить на свой пароль

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                role="admin"  # добавлено для CustomUser
            )
            self.stdout.write(self.style.SUCCESS(f"Суперпользователь {username} создан"))
        else:
            self.stdout.write(self.style.WARNING(f"Суперпользователь {username} уже существует"))
