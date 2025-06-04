from django import forms
from .models import Equipment

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['barcode', 'inventory_number', 'name', 'equipment_type', 'location', 'responsible', 'status']
        widgets = {
            'status': forms.Select(choices=Equipment._meta.get_field('status').choices),
        }
