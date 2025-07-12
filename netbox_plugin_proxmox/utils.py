import logging
from dcim.models import devices as nb_devices, device_components as nb_device_components
from ipam.models import ip as nb_ip, vlans as nb_vlans
from virtualization.models import virtualmachines as nb_vms


logger = logging.getLogger(__name__)


def get_or_create_vlan(vlan_id):
    try:
        vlan = nb_vlans.VLAN.objects.get(vid=vlan_id)
    except nb_vlans.VLAN.DoesNotExist:
        vlan = nb_vlans.VLAN(
            vid=vlan_id,
            name="VLAN %(vid)s [PROXMOX IMPORT]" % {"vid": vlan_id},
            status="active",
        )
        vlan.save()
    return vlan


def get_or_create_ip(ip_address):
    try:
        _ip_address = nb_ip.IPAddress.objects.get(address=ip_address)
    except nb_ip.IPAddress.DoesNotExist:
        _ip_address = nb_ip.IPAddress(address=ip_address, status="active")
        _ip_address.save()
    return _ip_address


def get_or_create_interface(if_name="", device_id=None, vm_id=None):
    if device_id is not None:
        try:
            nb_iface = nb_device_components.Interface.objects.get(
                name=if_name, device_id=device_id
            )
        except nb_device_components.Interface.DoesNotExist:
            nb_iface = nb_device_components.Interface(
                name=if_name, device_id=device_id, type="other"
            )
            nb_iface.save()

    if vm_id is not None:
        try:
            nb_iface = nb_vms.VMInterface.objects.get(
                name=if_name, virtual_machine_id=vm_id
            )
        except nb_vms.VMInterface.DoesNotExist:
            nb_iface = nb_vms.VMInterface(name=if_name, virtual_machine_id=vm_id)
            nb_iface.save()
    return nb_iface


def get_or_create_mac_address(mac_address):
    try:
        mac_address = nb_devices.MACAddress.objects.get(mac_address=mac_address)
    except nb_devices.MACAddress.DoesNotExist:
        mac_address = nb_devices.MACAddress(mac_address=mac_address)
        mac_address.save()
    return mac_address
