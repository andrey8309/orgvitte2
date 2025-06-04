from django.shortcuts import render, redirect
from .forms import EquipmentForm

def add_equipment(request):
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_equipment')  # Можно перенаправить куда нужно
    else:
        form = EquipmentForm()
    return render(request, 'add_equipment.html', {'form': form})
