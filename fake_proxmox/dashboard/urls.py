from django.urls import path
from . import views

urlpatterns = [
    path('', views.hypervisor_list, name='hypervisor_list'),
    path('hypervisor/<int:hypervisor_id>/add_vm/', views.add_vm, name='add_vm'),
    path('hypervisor/<int:hypervisor_id>/delete/', views.delete_hypervisor, name='delete_hypervisor'),
    path('hypervisor/<int:hypervisor_id>/vm/<str:vm_uuid>/', views.vm_detail, name='vm_detail'),
    path('hypervisor/<int:hypervisor_id>/vm/<str:vm_uuid>/delete/', views.delete_vm, name='delete_vm'),
    path('add_hypervisor/', views.add_hypervisor, name='add_hypervisor'),
    path('create_vm/', views.create_vm, name='create_vm'),
    path('hypervisor/<int:hypervisor_id>/vms/', views.vm_list, name='vm_list'),

]
