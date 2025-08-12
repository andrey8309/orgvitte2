from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_equipment, name='list_equipment'),
    path('add/', views.add_equipment, name='add_equipment'),
    path('edit/<int:pk>/', views.edit_equipment, name='edit_equipment'),
    path('delete/<int:pk>/', views.delete_equipment, name='delete_equipment'),
]
