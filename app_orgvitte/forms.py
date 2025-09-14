from django import forms
from .models import Equipment, EquipmentAction, Feedback, FileUpload, RequestTicket, Article


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['barcode', 'inventory_number', 'name', 'equipment_type', 'location', 'responsible', 'status']
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
        fields = ['title', 'description', 'request_type']

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content']