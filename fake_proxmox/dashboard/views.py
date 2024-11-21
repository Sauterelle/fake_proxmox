from django.shortcuts import render
from django.http import HttpResponse
from .utils.kvm_python import get_hypervisor_info_json
from .models import VirtualMachine
import libvirt


def index(request):
    remote_user = "root"
    remote_hosts = "172.16.136.156"
    conn = libvirt.open("qemu+ssh://" + remote_user + "@" + remote_hosts + "/system")
    hypervisor_info = get_hypervisor_info_json(conn)
    vms = VirtualMachine.objects.all()
    return render(request, "index.html", {"vms": vms, "info": hypervisor_info})
