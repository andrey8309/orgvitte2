from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Администратор"),
        ("tech", "Техник"),
        ("user", "Пользователь"),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="user",
        verbose_name="Роль"
    )

    def is_admin(self):
        return self.role == "admin"

    def is_tech(self):
        return self.role == "tech"

    def is_user(self):
        return self.role == "user"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Equipment(models.Model):
    EQUIPMENT_TYPES = [
        ('printer', 'Принтер/МФУ'),
        ('phone', 'Телефон'),
        ('other', 'Другое'),
    ]

    name = models.CharField(max_length=255, verbose_name="Название")
    inventory_number = models.CharField(max_length=100, unique=True, verbose_name="Инвентарный номер")
    equipment_type = models.CharField(max_length=20, choices=EQUIPMENT_TYPES, default='other', verbose_name="Тип оборудования")
    location = models.CharField(max_length=255, verbose_name="Местоположение")
    responsible = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Ответственный")
    status = models.CharField(max_length=20, choices=[
        ('active', 'В работе'),
        ('under_repair', 'В ремонте'),
        ('written_off', 'Списано'),
    ], default='active', verbose_name="Статус")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    def __str__(self):
        return f"{self.name} ({self.inventory_number})"

class EquipmentAction(models.Model):
    ACTION_TYPES = [
        ('repair', 'Ремонт'),
        ('movement', 'Перемещение'),
        ('decommission', 'Списание'),
    ]

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, verbose_name="Оборудование")
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES, verbose_name="Тип действия")
    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата действия")
    from_location = models.CharField(max_length=255, blank=True, null=True, verbose_name="Откуда")
    to_location = models.CharField(max_length=255, blank=True, null=True, verbose_name="Куда")
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Выполнил")

    def __str__(self):
        return f"{self.get_action_type_display()} - {self.equipment}"

class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Пользователь")
    name = models.CharField(max_length=100, verbose_name="Имя", blank=True, null=True)
    email = models.EmailField(verbose_name="Email", blank=True, null=True)
    message = models.TextField(verbose_name="Сообщение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")

    def __str__(self):
        return f"Обратная связь от {self.user.username if self.user else 'Аноним'}"

class FileUpload(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name="files", verbose_name="Оборудование")
    file = models.FileField(upload_to="uploads/", verbose_name="Файл")
    description = models.CharField(max_length=255, blank=True, verbose_name="Описание файла")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")

    def __str__(self):
        return f"Файл {self.description or self.file.name} для {self.equipment}"

class RequestTicket(models.Model):
    REQUEST_TYPES = [
        ("cartridge", "Замена картриджа"),
        ("phone_number", "Смена номера телефона"),
        ("repair", "Ремонт оборудования"),
        ("other", "Другое"),
    ]

    equipment = models.ForeignKey(
        Equipment, on_delete=models.CASCADE, verbose_name="Оборудование", null=True, blank=True
    )
    request_type = models.CharField(max_length=50, choices=REQUEST_TYPES, verbose_name="Тип заявки")
    description = models.TextField(verbose_name="Описание проблемы")
    status = models.CharField(
        max_length=20,
        choices=[("new", "Новая"), ("in_progress", "В обработке"), ("done", "Выполнена")],
        default="new",
        verbose_name="Статус заявки",
    )
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Создатель")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"{self.get_request_type_display()} ({self.status})"

class Article(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок статьи")
    content = models.TextField(verbose_name="Содержание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Автор")

    def __str__(self):
        return self.title

