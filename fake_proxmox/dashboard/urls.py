from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),  # TEST
    path("console/<str:vm_id>/", views.vm_console, name="vm_console"),
    path("new-vm/", views.createVm, name="new-vm"),
]
