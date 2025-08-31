from django import forms
from .models import Equipment, EquipmentAction

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
