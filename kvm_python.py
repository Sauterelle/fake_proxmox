import libvirt


def domains_to_xml(conn):
    list_domains = conn.listAllDomains()
    with open("vms_info.xml", "w") as file:
        for domain in list_domains:
            file.write(domain.XMLDesc())


def shutdown_vm(domain):
    if domain.isActive():
        domain.destroy()
    else:
        print("domain is already innactive")


def start_vm(domain):
    state = domain.state()
    print(state)


remote_user = "root"
remote_hosts = "172.16.136.156"

conn = libvirt.open("qemu+ssh://" + remote_user + "@" + remote_hosts + "/system")
if not conn:
    raise SystemExit("Failed to open connection to qemu:///system")


domains_to_xml(conn)


# print_active_domains(conn)
# print_all_domains(conn)
# nodeinfo = conn.getInfo()


conn.close()
