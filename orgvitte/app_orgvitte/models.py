from django.db import models
from django.contrib.auth.models import User


class Equipment(models.Model):
    barcode = models.CharField(max_length=100, unique=True, verbose_name="Штрих-код")
    inventory_number = models.CharField(max_length=100, unique=True, verbose_name="Инвентарный номер")
    name = models.CharField(max_length=200, verbose_name="Наименование")
    equipment_type = models.CharField(max_length=100, verbose_name="Тип оборудования")
    location = models.CharField(max_length=200, verbose_name="Расположение")
    responsible = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Ответственный")
    status = models.CharField(max_length=50, choices=[
        ('in_use', 'В эксплуатации'),
        ('under_repair', 'В ремонте'),
        ('written_off', 'Списано')
    ], verbose_name="Статус")
    added_at = models.DateTimeField(auto_now_add=True)

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
    date = models.DateField(verbose_name="Дата")
    from_location = models.CharField(max_length=255, blank=True, null=True, verbose_name="Откуда")
    to_location = models.CharField(max_length=255, blank=True, null=True, verbose_name="Куда")
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Выполнил")

    def __str__(self):
        return f"{self.get_action_type_display()} - {self.equipment}"
