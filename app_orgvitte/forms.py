from django import forms
from .models import Equipment, EquipmentAction, Feedback, FileUpload, RequestTicket, Article


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
        fields = ["equipment", "request_type", "description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Если выбрано оборудование — фильтруем типы заявок
        equipment = self.initial.get("equipment") or self.data.get("equipment")
        if equipment:
            try:
                eq = Equipment.objects.get(id=equipment)
                if eq.equipment_type == "Принтер":
                    self.fields["request_type"].choices = [
                        ("cartridge", "Замена картриджа"),
                        ("repair", "Ремонт оборудования"),
                        ("other", "Другое"),
                    ]
                elif eq.equipment_type == "Телефон":
                    self.fields["request_type"].choices = [
                        ("phone_number", "Смена номера телефона"),
                        ("repair", "Ремонт оборудования"),
                        ("other", "Другое"),
                    ]
                else:
                    # Для любого другого оборудования — только ремонт и другое
                    self.fields["request_type"].choices = [
                        ("repair", "Ремонт оборудования"),
                        ("other", "Другое"),
                    ]
            except Equipment.DoesNotExist:
                pass


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content']