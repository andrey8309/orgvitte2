from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import Equipment, EquipmentAction
from .forms import EquipmentForm, EquipmentActionForm
from django.contrib.auth.decorators import login_required, permission_required
import csv

@login_required
@permission_required('app_orgvitte.view_equipment', raise_exception=True)
def list_equipment(request):
    equipment_list = Equipment.objects.all()
    return render(request, 'list_equipment.html', {'equipment_list': equipment_list})

@login_required
@permission_required('app_orgvitte.add_equipment', raise_exception=True)
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

@login_required
@permission_required('app_orgvitte.change_equipment', raise_exception=True)
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

@login_required
@permission_required('app_orgvitte.delete_equipment', raise_exception=True)
def delete_equipment(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    equipment.delete()
    messages.success(request, "Оборудование успешно удалено.")
    return redirect('list_equipment')

def list_actions(request):
    actions = EquipmentAction.objects.select_related("equipment").all()
    return render(request, "list_actions.html", {"actions": actions})

# Добавление действия (ремонт, перемещение, списание)
@login_required
@permission_required('app_orgvitte.add_equipmentaction', raise_exception=True)
def add_equipment_action(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)

    if request.method == 'POST':
        form = EquipmentActionForm(request.POST)
        if form.is_valid():
            action = form.save(commit=False)
            action.equipment = equipment
            action.performed_by = request.user
            action.save()

            # обновим статус оборудования
            if action.action_type == 'repair':
                equipment.status = 'under_repair'
            elif action.action_type == 'movement':
                if action.to_location:
                    equipment.location = action.to_location
            elif action.action_type == 'decommission':
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


@permission_required('app_orgvitte.view_equipmentaction', raise_exception=True)
def equipment_actions(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)
    actions = EquipmentAction.objects.filter(equipment=equipment).order_by('-date')
    return render(request, 'equipment_actions.html', {
        'equipment': equipment,
        'actions': actions
    })

def export_equipment_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="equipment.csv"'

    writer = csv.writer(response, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    writer.writerow([
        'ID',
        'Инвентарный номер',
        'Название',
        'Тип оборудования',
        'Местоположение',
        'Ответственный',
        'Статус',
        'Дата добавления'
    ])

    equipment = Equipment.objects.all()
    for eq in equipment:
        writer.writerow([
            eq.id,
            eq.inventory_number,
            eq.name,
            eq.equipment_type,
            eq.location,
            eq.responsible.username if eq.responsible else "—",
            eq.get_status_display(),
            eq.added_at.strftime("%Y-%m-%d %H:%M")
        ])

    return response


