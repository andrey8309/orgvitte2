from django import forms
from .models import Equipment, EquipmentAction, Feedback, FileUpload, RequestTicket, Article
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['name', 'inventory_number', 'equipment_type', 'location', 'responsible', 'status']
        widgets = {
            'status': forms.Select(choices=Equipment._meta.get_field('status').choices),
        }

class EquipmentActionForm(forms.ModelForm):
    class Meta:
        model = EquipmentAction
        fields = ['action_type', 'description', 'from_location', 'to_location']

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше имя'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ваш email'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Ваш отзыв'}),
        }


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = FileUpload
        fields = ['file', 'description']



class RequestTicketForm(forms.ModelForm):
    class Meta:
        model = RequestTicket
        fields = ["equipment", "request_type", "description",
                  "department", "contact_info", "photo", "repair_date", "priority"]

        widgets = {
            "equipment": forms.Select(attrs={
                "class": "form-select",
            }),
            "request_type": forms.Select(attrs={
                "class": "form-select",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Опишите проблему подробно...",
            }),
            "department": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Укажите отдел / подразделение",
            }),
            "contact_info": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Телефон, email или внутренний номер",
            }),
            "photo": forms.ClearableFileInput(attrs={
                "class": "form-control",
            }),
            "repair_date": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control",
            }),
            "priority": forms.Select(attrs={
                "class": "form-select",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Сначала ставим все варианты из модели
        self.fields["request_type"].choices = RequestTicket.REQUEST_TYPES

        # определяем equipment_id (с учётом POST, initial или instance)
        equipment_id = None

        # 1) из POST
        data = getattr(self, "data", None)
        if data and data.get("equipment"):
            equipment_id = data.get("equipment")
        # 2) из initial
        elif self.initial.get("equipment"):
            equipment_id = self.initial.get("equipment")
        # 3) из instance
        elif self.instance and getattr(self.instance, "equipment_id", None):
            equipment_id = self.instance.equipment_id

        # нормализуем в int
        try:
            equipment_id_int = int(equipment_id) if equipment_id is not None else None
        except (ValueError, TypeError):
            equipment_id_int = None

        if equipment_id_int:
            try:
                eq = Equipment.objects.get(pk=equipment_id_int)
            except Equipment.DoesNotExist:
                eq = None

            if eq:

                if eq.equipment_type == 'printer':
                    allowed = ("cartridge", "repair", "other")
                elif eq.equipment_type == 'phone':
                    allowed = ("phone_number", "repair", "other")
                else:
                    allowed = ("repair", "other")


                self.fields["request_type"].choices = [
                    (key, label) for key, label in RequestTicket.REQUEST_TYPES if key in allowed
                ]


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content']

class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "role", "is_active"]
        labels = {
            "username": "Логин",
            "email": "Email",
            "role": "Роль",
            "is_active": "Активен",
        }

class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "role", "is_active", "is_staff", "is_superuser"]

class UserCreateForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "role", "is_active", "is_staff", "is_superuser"]