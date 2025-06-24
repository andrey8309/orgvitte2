from django.db import models
from django.contrib.auth.models import User


class Equipment(models.Model):
    barcode = models.CharField(max_length=100, unique=True)
    inventory_number = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    equipment_type = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    responsible = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=50, choices=[
        ('in_use', 'В эксплуатации'),
        ('under_repair', 'В ремонте'),
        ('written_off', 'Списано')
    ])
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.inventory_number})"