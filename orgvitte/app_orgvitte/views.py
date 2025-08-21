from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Equipment, EquipmentAction
from .forms import EquipmentForm, EquipmentActionForm

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

def list_actions(request):
    actions = EquipmentAction.objects.select_related("equipment").all()
    return render(request, "list_actions.html", {"actions": actions})

# Добавление действия (ремонт, перемещение, списание)
def add_equipment_action(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)

    if request.method == 'POST':
        form = EquipmentActionForm(request.POST)
        if form.is_valid():
            action = form.save(commit=False)
            action.equipment = equipment
            action.performed_by = request.user
            action.save()

            # обновим статус оборудования (например, при ремонте или списании)
            if action.action_type == 'repair':
                equipment.status = 'under_repair'
            elif action.action_type == 'move':
                equipment.location = action.description  # допустим, новое место хранится в описании
            elif action.action_type == 'write_off':
                equipment.status = 'written_off'
            equipment.save()

            messages.success(request, f"Действие '{action.get_action_type_display()}' успешно добавлено для {equipment.name}")
            return redirect('list_equipment')
        else:
            messages.error(request, "Ошибка при добавлении действия. Проверьте введённые данные.")
    else:
        form = EquipmentActionForm()

    return render(request, 'add_equipment_action.html', {
        'form': form,
        'equipment': equipment
    })