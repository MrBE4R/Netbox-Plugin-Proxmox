import re
import proxmoxer
import logging
from django.contrib.contenttypes.models import ContentType
from virtualization.models import virtualmachines as nb_vms
from dcim.models import devices as nb_devices
from ipam.models import ip as nb_ip
from .utils import (
    get_or_create_ip,
    get_or_create_interface,
    get_or_create_mac_address,
)


logger = logging.getLogger(__name__)


def get_or_create_and_update_qemu(
    qemu_proxmox_json,
    netbox_config,
    netbox_cluster,
    netbox_node,
    proxmox_node,
    proxmox_client,
):
    logger.info(
        f"Working on qemu {qemu_proxmox_json.get('vmid')} - {qemu_proxmox_json.get('name')}"
    )
    yield f"<p>Working on qemu {qemu_proxmox_json.get('vmid')} - {qemu_proxmox_json.get('name')}</p>"
    vm_config = (
        proxmox_client.nodes(proxmox_node)
        .qemu(qemu_proxmox_json.get("vmid"))
        .config.get()
    )
    proxmox_cleaned_json = {
        "cpus": int(qemu_proxmox_json.get("cpus")),
        "memory": int(vm_config.get("memory")),
        "status": "active"
        if qemu_proxmox_json.get("status") == "running"
        else "offline",
        "name": qemu_proxmox_json.get("name"),
        "maxdisk": int(int(qemu_proxmox_json.get("maxdisk")) / (1024 * 1024 * 1024)),
        "network": [],
    }
    for interface in [
        {key: val}
        for key, val in vm_config.items()
        if re.search("^net*", key) is not None
    ]:
        for ifname in interface:
            _mac_addr = ""
            _mtu = 1500
            _vlan = None
            _bridge = None
            for _conf_str in interface[ifname].split(","):
                _k_s = _conf_str.split("=")
                if re.match(
                    "[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", _k_s[1].lower()
                ):
                    _mac_addr = _k_s[1].upper()
                elif _k_s[0] == "bridge":
                    _bridge = _k_s[1].lower()
                elif _k_s[0] == "mtu":
                    if int(_k_s[1]) == 1:
                        if _bridge is not None:
                            node = nb_devices.Device.objects.get(
                                name=proxmox_node, cluster=netbox_cluster
                            )
                            brg = get_or_create_interface(
                                device_id=node.id, if_name=_bridge
                            )
                            _mtu = int(brg.mtu or 1500)
                    else:
                        _mtu = int(_k_s[1])
                elif _k_s[0] == "tag":
                    _vlan = int(_k_s[1])
            proxmox_cleaned_json["network"].append(
                {"name": ifname, "mac_address": _mac_addr, "mtu": _mtu}
            )
    proxmox_vmid = f"{str(netbox_cluster.name).replace(' ', '_').lower()}.{str(qemu_proxmox_json.get('vmid'))}"
    try:
        netbox_qemu = nb_vms.VirtualMachine.objects.get(
            custom_field_data__proxmox_vmid=proxmox_vmid
        )
        netbox_qemu.name = qemu_proxmox_json.get("name")
        netbox_qemu.status = (
            "active" if qemu_proxmox_json.get("status") == "running" else "offline"
        )
        netbox_qemu.cluster = netbox_cluster
        netbox_qemu.role_id = netbox_config.get("vm_role_id")
        netbox_qemu.vcpus = int(qemu_proxmox_json.get("cpus"))
        netbox_qemu.memory = int(vm_config.get("memory"))
        netbox_qemu.disk = int(
            int(qemu_proxmox_json.get("maxdisk")) / (1024 * 1024 * 1024)
        )
    except nb_vms.VirtualMachine.DoesNotExist:
        netbox_qemu = nb_vms.VirtualMachine(
            name=qemu_proxmox_json.get("name"),
            role_id=netbox_config.get("vm_role_id"),
            status="active"
            if qemu_proxmox_json.get("status") == "running"
            else "offline",
            cluster=netbox_cluster,
            device=netbox_node,
            vcpus=int(qemu_proxmox_json.get("cpus")),
            memory=int(vm_config.get("memory")),
            disk=int(int(qemu_proxmox_json.get("maxdisk")) / (1024 * 1024 * 1024)),
        )
    netbox_qemu.custom_field_data["proxmox_vmid"] = proxmox_vmid
    netbox_qemu.device = netbox_node
    netbox_qemu.save()
    netbox_qemu_json = netbox_qemu_to_json(netbox_qemu)
    with_addresses = False

    if netbox_qemu.status == "active" and proxmox_cleaned_json["status"] == "active":
        logger.debug("Trying to get ip addresses from Proxmox")
        try:
            if_config = (
                proxmox_client.nodes(proxmox_node)
                .qemu(qemu_proxmox_json.get("vmid"))
                .agent("network-get-interfaces")
                .get()
                .get("result")
            )
            for interface in proxmox_cleaned_json.get("network"):
                myidx = proxmox_cleaned_json.get("network").index(interface)
                pmx_iface = next(
                    (
                        item
                        for item in if_config
                        if item.get("hardware-address").upper()
                        == interface.get("mac_address").upper()
                    ),
                    None,
                )
                if pmx_iface is not None:
                    addresses = []
                    for pmx_addr in pmx_iface.get("ip-addresses", []):
                        addresses.append(
                            "%(addr)s/%(prefix)s"
                            % {
                                "addr": pmx_addr.get("ip-address"),
                                "prefix": pmx_addr.get("prefix"),
                            }
                        )
                    proxmox_cleaned_json["network"][myidx] = interface | {
                        "addresses": sorted(addresses)
                    }
            netbox_qemu_json = netbox_qemu_to_json(netbox_qemu, with_addresses=True)
            with_addresses = True
        except proxmoxer.core.ResourceException as e:
            logger.warning(e.content)
    proxmox_cleaned_json["network"] = sorted(
        proxmox_cleaned_json.get("network"), key=lambda d: d["name"]
    )
    if not proxmox_cleaned_json == netbox_qemu_json:
        logger.debug(
            "Netbox Virtual Machine is different from the one we got from Proxmox, updating."
        )
        for interface in proxmox_cleaned_json.get("network"):
            iface = get_or_create_interface(
                if_name=interface.get("name"), vm_id=netbox_qemu.id
            )
            iface.mtu = interface.get("mtu", 1500)
            mac_address = get_or_create_mac_address(interface.get("mac_address"))
            iface.primary_mac_address_id = mac_address.id
            iface.save()
            for address in interface.get("addresses", []):
                ip = get_or_create_ip(address)
                ip.assigned_object_id = iface.id
                ip.assigned_object = iface
                ip.save()
        netbox_qemu_json = netbox_qemu_to_json(
            netbox_qemu, with_addresses=with_addresses
        )
        if not proxmox_cleaned_json == netbox_qemu_json:
            logger.debug(
                "Netbox Virtual Machine is still different from the one we got from Proxmox, removing old interfaces."
            )
            for interface in netbox_qemu_json.get("network"):
                if interface not in proxmox_cleaned_json.get("network"):
                    iface = nb_vms.VMInterface.objects.get(
                        name=interface.get("name"), virtual_machine_id=netbox_qemu.id
                    )
                    iface.delete()


def netbox_qemu_to_json(netbox_qemu=None, with_addresses=False):
    content_type = ContentType.objects.get(
        app_label="virtualization", model="vminterface"
    )
    netbox_qemu_json = {
        "cpus": int(netbox_qemu.vcpus),
        "memory": int(netbox_qemu.memory),
        "status": str(netbox_qemu.status),
        "name": str(netbox_qemu.name),
        "maxdisk": int(netbox_qemu.disk),
        "network": [],
    }
    for interface in netbox_qemu.interfaces.order_by("name").all():
        _i = {
            "name": str(interface.name),
            "mac_address": str(interface.mac_address).upper(),
            "mtu": int(interface.mtu or 1500),
        }
        if with_addresses:
            addresses = []
            for ip in nb_ip.IPAddress.objects.filter(
                assigned_object_type=content_type, assigned_object_id=interface.id
            ):
                addresses.append(str(ip.address))
            netbox_qemu_json["network"].append(_i | {"addresses": sorted(addresses)})
        else:
            netbox_qemu_json["network"].append(_i)
    netbox_qemu_json["network"] = sorted(
        netbox_qemu_json.get("network"), key=lambda d: d["name"]
    )
    return netbox_qemu_json


def get_or_create_and_update_lxc(lxc_proxmox_json, netbox_config):
    pass
