from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
from .models import Equipment, EquipmentAction, Feedback, FileUpload, RequestTicket, Article, CustomUser
from .forms import EquipmentForm, EquipmentActionForm, RequestTicketForm, FeedbackForm, FileUploadForm, UserEditForm, UserCreateForm, ArticleForm
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
import csv
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
import json
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.db.models.functions import TruncMonth



User = get_user_model()

def public_home(request):
    """Публичная главная страница"""
    return render(request, "public/home.html")

@login_required
def csrf_failure(request, reason=""):
    return render(request, "csrf_failure.html", {"reason": reason}, status=403)


def is_admin(user):
    return user.is_authenticated and user.role == "admin"

@login_required
@user_passes_test(is_admin)
def admin_user_list(request):
    users = User.objects.all()
    return render(request, "admin_user_list.html", {"users": users})

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
def create_request_ticket(request, equipment_id=None):
    """
    Создание заявки
    """
    equipment = None
    if equipment_id:
        equipment = get_object_or_404(Equipment, id=equipment_id)

    if request.method == "POST":
        form = RequestTicketForm(request.POST, initial={"equipment": equipment.id if equipment else None})
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()
            messages.success(request, f"Заявка «{ticket.get_request_type_display()}» успешно создана!")
            return redirect("list_tickets")
        else:
            messages.error(request, "Ошибка при создании заявки. Проверьте введённые данные.")
    else:
        form = RequestTicketForm(initial={"equipment": equipment.id if equipment else None})

    return render(request, "create_ticket.html", {
        "form": form,
        "equipment": equipment,
    })

@login_required
@permission_required('app_orgvitte.change_requestticket', raise_exception=True)
def update_ticket_status(request, ticket_id, new_status):
    ticket = get_object_or_404(RequestTicket, id=ticket_id)

    # Только админ или техник может менять
    if request.user.role not in ["tech", "admin"]:
        return HttpResponseForbidden("Нет прав для изменения статуса заявки.")

    # Если техник — проверяем, назначена ли заявка ему
    if request.user.role == "tech" and ticket.assigned_to != request.user:
        return HttpResponseForbidden("Вы можете изменять только свои заявки.")

    valid_statuses = ["new", "in_progress", "done"]
    if new_status not in valid_statuses:
        messages.error(request, "Недопустимый статус.")
        return redirect("list_tickets")

    ticket.status = new_status
    ticket.save()

    messages.success(request, f"Статус заявки #{ticket.id} изменён на {ticket.get_status_display()}.")
    return redirect("list_tickets")


@login_required
def list_tickets(request):
    if request.user.role == "admin" or request.user.is_superuser:

        tickets = RequestTicket.objects.all().order_by("-created_at")
    elif request.user.role == "tech":

        tickets = RequestTicket.objects.all().order_by("-created_at")
    else:

        tickets = RequestTicket.objects.filter(created_by=request.user).order_by("-created_at")

    tech_users = CustomUser.objects.filter(role="tech")
    context = {
        "tickets": tickets,
        "tech_users": tech_users,
    }
    return render(request, "list_tickets.html", context)


@login_required
def feedback_view(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Спасибо! Ваше сообщение отправлено.")
            return redirect("feedback")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = FeedbackForm()

    return render(request, "feedback.html", {"form": form})


# ==== Загрузка файлов  ====

@login_required
def upload_file(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_upload = form.save(commit=False)
            file_upload.equipment = equipment  # ← автоматическая привязка
            file_upload.save()
            messages.success(request, f"Файл успешно загружен для {equipment.name}!")
            return redirect('equipment_files', equipment_id=equipment.id)
        else:
            messages.error(request, "Ошибка при загрузке файла. Проверьте данные.")
    else:
        form = FileUploadForm()

    return render(request, 'upload_file.html', {'form': form, 'equipment': equipment})

@login_required
def equipment_files(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)
    files = equipment.files.all()
    return render(request, 'equipment_files.html', {
        'equipment': equipment,
        'files': files
    })

@login_required
def list_files(request):
    files = FileUpload.objects.select_related("equipment").order_by("-uploaded_at")
    return render(request, "list_files.html", {"files": files})

@login_required
@permission_required("app_orgvitte.delete_fileupload", raise_exception=True)
def delete_file(request, pk):
    file = get_object_or_404(FileUpload, pk=pk)
    file.delete()
    messages.success(request, "Файл удалён.")
    return redirect("list_files")


# ==== Статьи / справка по системе ====

@login_required
def list_articles(request):
    articles = Article.objects.all().order_by("-created_at")
    return render(request, "list_articles.html", {"articles": articles})


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
        .values("request_type")
        .annotate(total=Count("id"))
        .order_by("-total")
    )


    labels = [dict(RequestTicket.REQUEST_TYPES)[item["request_type"]] for item in stats]
    data = [item["total"] for item in stats]

    tickets_by_tech = (
        RequestTicket.objects.filter(status="done", created_at__gte=last_month)
        .values("assigned_to__username")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    tech_labels = [item["assigned_to__username"] or "Не назначен" for item in tickets_by_tech]
    tech_data = [item["count"] for item in tickets_by_tech]

    return render(
        request,
        "report_tickets.html",
        {
            "stats": stats,
            "labels": json.dumps(labels),
            "data": json.dumps(data),
            "tech_labels": json.dumps(tech_labels),
            "tech_data": json.dumps(tech_data),
        },
    )

@login_required
@permission_required('app_orgvitte.view_feedback', raise_exception=True)
def list_feedback(request):
    feedbacks = Feedback.objects.order_by('-created_at')
    return render(request, 'list_feedback.html', {'feedbacks': feedbacks})

@login_required
@permission_required('app_orgvitte.view_feedback', raise_exception=True)
def feedback_detail(request, pk):
    feedback = get_object_or_404(Feedback, pk=pk)
    return render(request, 'feedback_detail.html', {'feedback': feedback})

@login_required
@permission_required('app_orgvitte.delete_feedback', raise_exception=True)
def delete_feedback(request, pk):
    feedback = get_object_or_404(Feedback, pk=pk)
    feedback.delete()
    messages.success(request, "Отзыв успешно удалён.")
    return redirect('list_feedback')




@login_required
@user_passes_test(lambda u: u.is_superuser or u.role == "admin")
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == "POST":
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Данные пользователя обновлены ✅")
            return redirect("admin_user_list")
    else:
        form = UserEditForm(instance=user)
    return render(request, "edit_user.html", {"form": form, "user": user})


@login_required
@user_passes_test(lambda u: u.is_superuser or u.role == "admin")
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == "POST":
        user.delete()
        messages.success(request, "Пользователь удалён 🗑")
        return redirect("admin_user_list")
    return render(request, "delete_user.html", {"user": user})


@login_required
@user_passes_test(lambda u: u.is_superuser or u.role == "admin")
def change_password(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == "POST":
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Пароль обновлён 🔑")
            return redirect("admin_user_list")
    else:
        form = SetPasswordForm(user)
    return render(request, "change_password.html", {"form": form, "user": user})


@login_required
def create_user(request):
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Пользователь успешно создан!")
            return redirect("admin_user_list")
        else:
            messages.error(request, "Ошибка при создании пользователя. Проверьте данные.")
    else:
        form = UserCreateForm()

    return render(request, "create_user.html", {"form": form})


@login_required
def dashboard(request):
    """Распределяем пользователя в нужный кабинет"""
    if request.user.role == "admin":
        return redirect("admin_dashboard")
    elif request.user.role == "tech":
        return redirect("tech_dashboard")
    else:
        return redirect("user_dashboard")


@login_required
def admin_dashboard(request):
    """Панель администратора"""
    return render(request, "admin_dashboard.html")


@login_required
def tech_dashboard(request):
    """Панель техника"""
    return render(request, "tech_dashboard.html")


@login_required
def user_dashboard(request):
    """Панель обычного пользователя"""
    return render(request, "user_dashboard.html")


@login_required
def update_ticket_status(request, ticket_id, new_status):
    ticket = get_object_or_404(RequestTicket, id=ticket_id)

    if request.user.role not in ["tech", "admin"]:
        return HttpResponseForbidden("У вас нет прав для изменения статуса заявки.")

    # Если техник берёт заявку в работу
    if new_status == "in_progress" and request.user.role == "tech":
        ticket.assigned_to = request.user

    ticket.status = new_status
    ticket.save()

    # Логирование выполненной заявки
    if new_status == "done" and ticket.equipment:
        action_type = None
        description = f"Заявка #{ticket.id}: {ticket.get_request_type_display()}"
        if ticket.request_type == "cartridge":
            action_type = "repair"
        elif ticket.request_type == "phone_number":
            action_type = "movement"
        elif ticket.request_type == "repair":
            action_type = "repair"
        elif ticket.request_type == "other":
            action_type = "decommission"

        if action_type:
            EquipmentAction.objects.create(
                equipment=ticket.equipment,
                action_type=action_type,
                description=description,
                performed_by=request.user
            )

    messages.success(request, f"Статус заявки #{ticket.id} изменён на {ticket.get_status_display()}.")
    return redirect("list_tickets")


# Проверка роли: только админ и техник видят аналитику
def is_staff_or_admin(user):
    return user.is_authenticated and user.role in ["admin", "tech"]

def assign_ticket_to_self(request, ticket_id):
    ticket = get_object_or_404(RequestTicket, id=ticket_id)

    if request.user.role != "tech":
        return HttpResponseForbidden("Только техник может назначать заявки.")

    if ticket.assigned_to:
        messages.error(request, f"Заявка #{ticket.id} уже назначена {ticket.assigned_to.username}.")
    else:
        ticket.assigned_to = request.user
        ticket.status = "in_progress"  # сразу ставим "В обработке"
        ticket.save()
        messages.success(request, f"Заявка #{ticket.id} назначена вам и переведена в работу.")

    return redirect("list_tickets")


@login_required
def report_dashboard(request):
    # 1. Получаем параметры фильтра (если переданы в GET)
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    tickets = RequestTicket.objects.all()

    if start_date:
        tickets = tickets.filter(created_at__gte=start_date)
    if end_date:
        tickets = tickets.filter(created_at__lte=end_date)

    # 2. Общая статистика
    total_tickets = tickets.count()
    new_tickets = tickets.filter(status="new").count()
    in_progress_tickets = tickets.filter(status="in_progress").count()
    done_tickets = tickets.filter(status="done").count()

    # 3. Динамика заявок по месяцам
    tickets_by_month = (
        tickets.annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    months = [t["month"].strftime("%B %Y") for t in tickets_by_month]
    month_counts = [t["count"] for t in tickets_by_month]

    # 4. ТОП-5 оборудования
    top_equipment = (
        tickets.values("equipment__name")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )
    equipment_labels = [t["equipment__name"] or "Без оборудования" for t in top_equipment]
    equipment_counts = [t["count"] for t in top_equipment]

    # 5. Нагрузка на техников (по закрытым заявкам)
    tickets_by_tech = (
        tickets.filter(status="done")
        .values("created_by__username")
        .annotate(count=Count("id"))
        .order_by("created_by__username")
    )
    tech_labels = [t["created_by__username"] or "Неизвестно" for t in tickets_by_tech]
    tech_counts = [t["count"] for t in tickets_by_tech]

    context = {
        "total_tickets": total_tickets,
        "new_tickets": new_tickets,
        "in_progress_tickets": in_progress_tickets,
        "done_tickets": done_tickets,
        "months": months,
        "month_counts": month_counts,
        "equipment_labels": equipment_labels,
        "equipment_counts": equipment_counts,
        "tech_labels": tech_labels,
        "tech_counts": tech_counts,
        "start_date": start_date or "",
        "end_date": end_date or "",
    }
    return render(request, "reports/report_dashboard.html", context)


@login_required
def export_tickets_csv(request):
    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = 'attachment; filename="tickets_report.csv"'

    writer = csv.writer(response, delimiter=";", quoting=csv.QUOTE_MINIMAL)

    # Заголовки
    writer.writerow(["ID", "Оборудование", "Тип заявки", "Описание", "Статус", "Создатель", "Дата"])

    tickets = RequestTicket.objects.select_related("equipment", "created_by").all()

    # Фильтрация по датам
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    if start_date and end_date:
        tickets = tickets.filter(created_at__date__range=(start_date, end_date))

    # Данные
    for t in tickets:
        writer.writerow([
            t.id,
            t.equipment.name if t.equipment else "—",
            t.get_request_type_display(),
            t.description,
            t.get_status_display(),
            t.created_by.username if t.created_by else "—",
            t.created_at.strftime("%Y-%m-%d %H:%M")
        ])

    return response


@login_required
def assign_ticket(request, ticket_id):
    ticket = get_object_or_404(RequestTicket, id=ticket_id)

    if request.user.role != "tech":
        return HttpResponseForbidden("Только техник может взять заявку в работу.")

    ticket.assigned_to = request.user
    ticket.status = "in_progress"
    ticket.save()

    messages.success(request, f"Заявка #{ticket.id} назначена вам и переведена в статус 'В работе'.")
    return redirect("list_tickets")

@login_required
def create_article(request):
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, "Статья успешно опубликована!")
            return redirect("list_articles")
    else:
        form = ArticleForm()

    return render(request, "create_article.html", {"form": form})

@login_required
def assign_technician(request, ticket_id):
    """Позволяет администратору назначить техника для заявки."""
    ticket = get_object_or_404(RequestTicket, id=ticket_id)

    if request.user.role != "admin":
        return HttpResponseForbidden("Только администратор может назначать техников.")

    if request.method == "POST":
        tech_id = request.POST.get("technician_id")
        if tech_id:
            technician = CustomUser.objects.filter(id=tech_id, role="tech").first()
            if technician:
                ticket.assigned_to = technician
                ticket.status = "in_progress"  # можно автоматически перевести в "В работе"
                ticket.save()
                messages.success(request, f"Заявка #{ticket.id} назначена технику {technician.username}.")
        return redirect("list_tickets")

    return redirect("list_tickets")


def public_home(request):
    return render(request, "public/home.html")

def about(request):
    return render(request, "public/about.html")

def rules(request):
    return render(request, "public/rules.html")

def links(request):
    return render(request, "public/links.html")

def contacts(request):
    return render(request, "public/contacts.html")

def guide(request):
    return render(request, "public/guide.html")

def news(request):
    return render(request, "public/news.html")

def faq(request):
    return render(request, "public/faq.html")

def privacy(request):
    return render(request, "public/privacy.html")

def public_feedback(request):
    return render(request, "public/feedback.html")