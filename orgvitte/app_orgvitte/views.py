from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Equipment
from .forms import EquipmentForm

def list_equipment(request):
    equipment_list = Equipment.objects.all()
    return render(request, 'list_equipment.html', {'equipment_list': equipment_list})

def add_equipment(request):
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Оборудование успешно добавлено!")
            return redirect('list_equipment')
        else:
            messages.error(request, "Ошибка при добавлении оборудования. Проверьте введённые данные.")
    else:
        form = EquipmentForm()
    return render(request, 'add_equipment.html', {'form': form})

def edit_equipment(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        form = EquipmentForm(request.POST, instance=equipment)
        if form.is_valid():
            form.save()
            messages.success(request, "Данные оборудования успешно обновлены!")
            return redirect('list_equipment')
        else:
            messages.error(request, "Ошибка при редактировании оборудования.")
    else:
        form = EquipmentForm(instance=equipment)
    return render(request, 'edit_equipment.html', {'form': form})

def delete_equipment(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    equipment.delete()
    messages.success(request, "Оборудование успешно удалено.")
    return redirect('list_equipment')
