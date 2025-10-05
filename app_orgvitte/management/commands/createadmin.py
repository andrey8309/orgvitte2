from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import connection, OperationalError

User = get_user_model()


class Command(BaseCommand):
    help = "Создаёт суперпользователя и тестовых пользователей, если их ещё нет"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("=== Проверка подключения к базе данных... ==="))

        # Проверяем подключение к БД
        try:
            connection.ensure_connection()
            self.stdout.write(self.style.SUCCESS("✅ Подключение к БД установлено"))
        except OperationalError as e:
            self.stdout.write(self.style.ERROR(f"❌ Ошибка подключения к БД: {e}"))
            return

        # Создание суперпользователя
        username = "andrey"
        email = "andrey.norsi@gmail.com"
        password = "admin123"

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                role="admin"
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Суперпользователь '{username}' создан"))
        else:
            self.stdout.write(self.style.WARNING(f"ℹ️ Суперпользователь '{username}' уже существует"))

        # Создание техника
        tech_username = "tech"
        if not User.objects.filter(username=tech_username).exists():
            User.objects.create_user(
                username=tech_username,
                email="tech@example.com",
                password="tech123",
                role="tech"
            )
            self.stdout.write(self.style.SUCCESS("👨‍🔧 Пользователь 'tech' (техник) создан"))
        else:
            self.stdout.write(self.style.WARNING("ℹ️ Пользователь 'tech' уже существует"))

        # Создание обычного пользователя
        user_username = "user"
        if not User.objects.filter(username=user_username).exists():
            User.objects.create_user(
                username=user_username,
                email="user@example.com",
                password="user123",
                role="user"
            )
            self.stdout.write(self.style.SUCCESS("Пользователь 'user' (пользователь) создан"))
        else:
            self.stdout.write(self.style.WARNING("️ Пользователь 'user' уже существует"))

        self.stdout.write(self.style.SUCCESS(" Инициализация пользователей завершена"))
