from sys import flags
import xml.etree.ElementTree as ET
import libvirt

"""
TODO à faire

- Ajouter une connexion QUEMU/KVM

  ---------Network---------
import xml.etree.ElementTree as ET
    Crée un nouveau réseau  

  ---------VM---------
  migrer vm 
  demarrer
  suspendre
  eteindre
  redémarer
  cloners
  supprimer
  snapshot
  cree une vm (template ??): fait (pas d'interface graphique pour l'instant, à voir avec spice ou vnc)
  ---------Gestion disque---------
  creer un pool 
  Cree un volume qcow2 : fait (par défaut dans le pool "default")
  Supprimer volume qcow2 : fait
"""


# connection utils
def connect_hypervisor(uri="qemu:///system"):
    try:
        return libvirt.open(uri)
    except libvirt.libvirtError as e:
        raise RuntimeError(f"erreur de connection à libvirt : {e}")


# Storage utils


def isVolumeExist(pool, volName):
    if pool.isActive():
        for name in pool.listVolumes():
            if name == volName:
                return True
    return False


def createStoragePoolVolume(pool, volName, capacity=10):
    if not isVolumeExist(pool, volName):
        stpVolXML = (
            """
            <volume>
              <name>"""
            + volName
            + """</name>
              <allocation>0</allocation>
              <capacity unit="G">"""
            + str(capacity)
            + """</capacity>
              <target>
                <format type="qcow2"/>
              </target>
            </volume>
            """
        )
        stpVol = pool.createXML(stpVolXML, 0)
        return stpVol
    else:
        return 0


def deleteStoragePoolVolume(volume):
    volume.delete()


def list_storage_pool(conn):
    pools = conn.listAllStoragePools(0)

    for pool in pools:
        if pool.isActive():
            stgvols = pool.listVolumes()
            print("Storage pool: " + pool.name())

            for stgvol in stgvols:
                print("     Storage vol: " + stgvol)


# VM utils
def get_domain_xml(conn, uuid):
    domain = conn.lookupByUUIDString(uuid)
    xml_desc = domain.XMLDesc()
    return xml_desc


def get_vm_info(domain):
    info = domain.info()
    vm_info = {
        "name": domain.name(),
        "uuid": domain.UUIDString(),
        "state": info[0],
        "max_memory_kb": info[1],
        "memory_used_kb": info[2],
        "vcpu_count": info[3],
        "cpu_time_ns": info[4],
    }

    return vm_info


def get_hypervisor_info_json(conn):
    info = conn.getInfo()
    hypervisor_info = {
        "uri": conn.getURI(),
        "hostname": conn.getHostname(),
        "cpu_model": info[0],
        "memory_size_mb": info[1],
        "cpu_count": info[2],
        "cpu_frequency_mhz": info[3],
        "numa_nodes": info[4],
        "cpu_sockets_per_node": info[5],
        "cores_per_socket": info[6],
        "threads_per_core": info[7],
        "domains": [],
    }

    for domain_id in conn.listDomainsID():
        domain = conn.lookupByID(domain_id)
        hypervisor_info["domains"].append(get_vm_info(domain))

    for domain_name in conn.listDefinedDomains():
        domain = conn.lookupByName(domain_name)
        hypervisor_info["domains"].append(get_vm_info(domain))

    return hypervisor_info


def createVm(uri, name, volume, iso_path, vcpu=1, memory=1):
    conn = connect_hypervisor(uri)
    try:
        xml_config = (
            """
            <domain type='qemu'>
            <name>"""
            + name
            + """</name>
            <memory unit='G'>"""
            + str(memory)
            + """</memory> <!-- 1 Go de RAM -->
            <vcpu placement='static'>"""
            + str(vcpu)
            + """</vcpu>    <!-- 1 vCPU -->
            <os>
                <type arch='x86_64' machine='pc-i440fx-7.2'>hvm</type>
            </os>
            <devices>
                <disk type='file' device='disk'>
                <driver name='qemu' type='qcow2'/>
                <source file='"""
            + volume.path()
            + """'/>
                <target dev='vda' bus='virtio'/>
                </disk>
                <disk type='file' device='cdrom'>
                    <driver name='qemu' type='raw'/>
                    <source file='"""
            + iso_path
            + """'/>
                    <target dev='hda' bus='ide'/>
                    <readonly/>
                </disk>
                <interface type='network'>
                <source network='default'/>
                </interface>
                <graphics type="vnc" port="5900" listen="0.0.0.0" autoport="yes">
                    <listen type="address" address="0.0.0.0"/>
                </graphics>
            </devices>
            </domain>
            """
        )
        dom = conn.createXML(xml_config)

        if dom is None:
            print("Failed to create a domain fom an XML definition.")
            exit(1)
        print("Guest " + dom.name() + " has booted")
    except libvirt.libvirtError as e:
        raise RuntimeError(f"Erreur à la creation de la vm : {e}")
    finally:
        conn.close()


def destroyVm(domain):
    if domain.isActive():
        domain.destroy()
    else:
        print("domain is already innactive")


def startVm(domain):
    if domain.isActive():
        print("VM is already active")
    else:
        domain.create()


def suspend_vm(domain):
    domain.suspend()
    print(f"VM {domain.getHostname()} suspendue.")


def shutdown_vm(domain):
    if not domain.isActive():
        domain.shutdown()
    else:
        print(f"Domain {domain.getHostname()} already shutdown.")


def reboot_vm(domain):
    domain.reboot(flags=0)
    print(f"Domain {domain.getHostname()} rebooted.")


def migrate_vm(vm_name, target_uri):
    conn = connect_hypervisor()
    try:
        vm = conn.lookupByName(vm_name)
        vm.migrate2(
            dconn=libvirt.open(target_uri),
            flags=libvirt.VIR_MIGRATE_LIVE | libvirt.VIR_MIGRATE_UNDEFINE_SOURCE,
            dname=None,
            uri=None,
            bandwidth=0,
        )
        print(f"Migration de {vm_name} terminée.")
    except libvirt.libvirtError as e:
        raise RuntimeError(f"Erreur de migration : {e}")
    finally:
        conn.close()


def delete_vm(vm_name):
    conn = connect_hypervisor()
    try:
        vm = conn.lookupByName(vm_name)
        if vm.isActive():
            vm.destroy()
        vm.undefine()
        print(f"VM {vm_name} deleted.")
    except libvirt.libvirtError as e:
        raise RuntimeError(f"Error while deleting : {e}")
    finally:
        conn.close()


def create_snapshot(vm_name, snapshot_name):
    conn = connect_hypervisor()
    try:
        vm = conn.lookupByName(vm_name)
        snapshot_xml = f"""
        <domainsnapshot>
            <name>{snapshot_name}</name>
        </domainsnapshot>
        """
        vm.snapshotCreateXML(snapshot_xml, 0)
        print(f"Snapshot {snapshot_name} créé pour {vm_name}.")
    except libvirt.libvirtError as e:
        raise RuntimeError(f"Erreur lors de la création du snapshot : {e}")
    finally:
        conn.close()


def restore_snapshot(vm_name, snapshot_name):
    conn = connect_hypervisor()
    try:
        vm = conn.lookupByName(vm_name)
        snapshot = vm.snapshotLookupByName(snapshot_name, 0)
        vm.revertToSnapshot(snapshot)
        print(f"Snapshot {snapshot_name} restauré pour {vm_name}.")
    except libvirt.libvirtError as e:
        raise RuntimeError(f"Erreur lors de la restauration : {e}")
    finally:
        conn.close()


def clone_vm(source_vm_name, clone_vm_name):
    conn = connect_hypervisor()
    try:
        source_vm = conn.lookupByName(source_vm_name)
        xml_desc = source_vm.XMLDesc(0)
        clone_xml = xml_desc.replace(source_vm_name, clone_vm_name)

        clone_vm = conn.defineXML(clone_xml)
        clone_vm.create()

        print(f"{clone_vm_name} has been successfully cloned and created.")
    except libvirt.libvirtError as e:
        raise RuntimeError(f"Erreur lors du clonage : {e}")
    finally:
        conn.close()


# def get_vnc_port(vm_name):
#     conn = connect_hypervisor()
#     domain = conn.lookupByName(vm_name)
#     xml_desc = domain.XMLDesc()
#     root = ET.fromstring(xml_desc)
#     vnc = root.find(".//graphics[@type='vnc']")
#     return int(vnc.get("port"))


# TEST

# remote_user = "root"
# remote_hosts = "172.16.136.156"
# conn = libvirt.open("qemu+ssh://" + remote_user + "@" + remote_hosts + "/system")
# # create storage pools
# pool = conn.storagePoolLookupByName("default")
# vol_name = "caca2.qcow2"
#
# print(isVolumeExist(pool, vol_name))
# if isVolumeExist(pool, vol_name):
#     print("ici")
#     createVm(
#         conn,
#         "mavm",
#         pool.storageVolLookupByName(vol_name),
#         "/mnt/nfs/ISO/debian-12.7.0-amd64-netinst.iso",
#     )
# else:
#     print("la")
#     volume = createStoragePoolVolume(pool, vol_name)
#     if volume:
#         print("dans le volume")
#         createVm(conn, "mavm", volume, "/mnt/nfs/ISO/debian-12.7.0-amd64-netinst.iso")
