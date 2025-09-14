from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import Equipment, EquipmentAction, Feedback, FileUpload, RequestTicket, Article
from .forms import EquipmentForm, EquipmentActionForm, RequestTicketForm, FeedbackForm, FileUploadForm
from django.contrib.auth.decorators import login_required, permission_required
import csv
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
import json

@login_required
@permission_required('app_orgvitte.view_equipment', raise_exception=True)
def list_equipment(request):
    equipment_list = Equipment.objects.all()

    # фильтрация по GET-параметрам
    name = request.GET.get("name")
    inventory_number = request.GET.get("inventory_number")
    status = request.GET.get("status")

    if name:
        equipment_list = equipment_list.filter(name__icontains=name)
    if inventory_number:
        equipment_list = equipment_list.filter(inventory_number__icontains=inventory_number)
    if status and status != "all":
        equipment_list = equipment_list.filter(status=status)

    return render(request, 'list_equipment.html', {
        'equipment_list': equipment_list,
        'filter_name': name or "",
        'filter_inventory_number': inventory_number or "",
        'filter_status': status or "all",
    })

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

            # Автоматическое обновление статуса оборудования
            if action.action_type == 'repair':
                equipment.status = 'under_repair'
            elif action.action_type == 'movement':
                if action.to_location:
                    equipment.location = action.to_location
            elif action.action_type == 'decommission':
                equipment.status = 'written_off'

            equipment.save()

            messages.success(request, f"Действие '{action.get_action_type_display()}' добавлено для {equipment.name}")
            return redirect('equipment_actions', equipment_id=equipment.id)
        else:
            messages.error(request, "Ошибка при добавлении действия.")
    else:
        form = EquipmentActionForm()

    return render(request, 'add_equipment_action.html', {
        'form': form,
        'equipment': equipment
    })


@login_required
@permission_required('app_orgvitte.view_equipmentaction', raise_exception=True)
def equipment_actions(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)
    actions = EquipmentAction.objects.filter(equipment=equipment).order_by('-date')

    return render(request, 'equipment_actions.html', {
        'equipment': equipment,
        'actions': actions
    })

@login_required
@permission_required('app_orgvitte.view_equipment', raise_exception=True)
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


@login_required
def create_request_ticket(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")

        if not title or not description:
            messages.error(request, "Заполните все поля")
        else:
            RequestTicket.objects.create(
                title=title,
                description=description,
                created_by=request.user
            )
            messages.success(request, "Заявка успешно создана")
            return redirect("list_tickets")

    return render(request, "create_request_ticket.html")


@login_required
def list_tickets(request):
    if request.user.is_superuser or request.user.groups.filter(name="Администратор").exists():
        tickets = RequestTicket.objects.all().order_by("-created_at")
    else:
        tickets = RequestTicket.objects.filter(created_by=request.user).order_by("-created_at")

    return render(request, "list_tickets.html", {"tickets": tickets})


@login_required
def feedback_view(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Спасибо! Ваше сообщение отправлено.")
            return redirect("list_equipment")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = FeedbackForm()

    return render(request, "feedback.html", {"form": form})


# ==== Загрузка файлов  ====

@login_required
def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Файл успешно загружен!")
            return redirect('list_files')
        else:
            messages.error(request, "Ошибка при загрузке файла. Проверьте данные.")
    else:
        form = FileUploadForm()

    return render(request, 'upload_file.html', {'form': form})


@login_required
def list_files(request):
    files = FileUpload.objects.all().order_by('-uploaded_at')
    return render(request, 'list_files.html', {'files': files})



# ==== Статьи / справка по системе ====

@login_required
def list_articles(request):
    articles = Article.objects.all().order_by("-created_at")
    return render(request, "articles.html", {"articles": articles})


@login_required
def view_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    return render(request, "view_article.html", {"article": article})

@login_required
def report_tickets(request):
    """Отчёт по заявкам: количество заявок по типам за последние 30 дней"""

    # последние 30 дней
    last_month = timezone.now() - timedelta(days=30)

    stats = (
        RequestTicket.objects.filter(created_at__gte=last_month)
        .values("title")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    # подготовим данные для графика
    labels = [item["title"] for item in stats]
    data = [item["total"] for item in stats]

    return render(
        request,
        "report_tickets.html",
        {
            "stats": stats,
            "labels": json.dumps(labels),
            "data": json.dumps(data),
        },
    )