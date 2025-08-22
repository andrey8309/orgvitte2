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
]
