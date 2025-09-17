from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_equipment, name='list_equipment'),
    path('add/', views.add_equipment, name='add_equipment'),
    path('edit/<int:pk>/', views.edit_equipment, name='edit_equipment'),
    path('delete/<int:pk>/', views.delete_equipment, name='delete_equipment'),
    path('actions/', views.list_actions, name='list_actions'),
    path('equipment/<int:equipment_id>/action/', views.add_equipment_action, name='add_equipment_action'),
    path('equipment/<int:equipment_id>/actions/', views.equipment_actions, name='equipment_actions'),
    path('equipment/export/csv/', views.export_equipment_csv, name='export_equipment_csv'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('files/delete/<int:pk>/', views.delete_file, name='delete_file'),
    path('tickets/new/', views.create_request_ticket, name='create_ticket'),
    path('tickets/', views.list_tickets, name='list_tickets'),
    path('articles/', views.list_articles, name='list_articles'),
    path('articles/<int:article_id>/', views.view_article, name='view_article'),
    path('reports/tickets/', views.report_tickets, name='report_tickets'),
    path('feedback/list/', views.list_feedback, name='list_feedback'),
    path('feedback/<int:pk>/', views.feedback_detail, name='feedback_detail'),
    path('feedback/delete/<int:pk>/', views.delete_feedback, name='delete_feedback'),
    path('equipment/<int:equipment_id>/files/', views.equipment_files, name='equipment_files'),
    path('equipment/<int:equipment_id>/files/upload/', views.upload_file, name='upload_file'),
    path('tickets/<int:ticket_id>/status/<str:new_status>/', views.update_ticket_status, name='update_ticket_status'),

]
