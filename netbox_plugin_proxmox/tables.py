import django_tables2 as tables
from netbox.tables import NetBoxTable, ChoiceFieldColumn
from .models import ProxmoxCluster, ProxmoxNetboxMapping


class ProxmoxClusterTable(NetBoxTable):
    class Meta(NetBoxTable.Meta):
        model = ProxmoxCluster
        fields = (
            "pk",
            "proxmox_url",
            "username",
            "verify_tls",
            "enabled",
            "netbox_mapping",
            "actions",
        )
        default_columns = ("proxmox_url",)

    proxmox_url = tables.Column(linkify=True)


class ProxmoxNetboxMappingTable(NetBoxTable):
    class Meta(NetBoxTable.Meta):
        model = ProxmoxNetboxMapping
        fields = (
            "pk",
            "name",
            "site",
            "cluster_type",
            "node_role",
            "node_device_type",
            "vm_role",
            "actions",
        )
        default_columns = ("name",)

    name = tables.Column(linkify=True)
