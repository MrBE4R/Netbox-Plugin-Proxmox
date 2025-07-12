from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer, WritableNestedSerializer
from virtualization.api.serializers import ClusterTypeSerializer
from dcim.api.serializers import (
    SiteSerializer,
    DeviceRoleSerializer,
    DeviceTypeSerializer,
)
from netbox_plugin_proxmox.models import ProxmoxCluster, ProxmoxNetboxMapping


class NestedProxmoxNetboxMappingSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_plugin_proxmox-api:proxmoxnetboxmapping-detail"
    )

    class Meta:
        model = ProxmoxNetboxMapping
        fields = ("id", "name", "display", "url")


class NestedProxmoxClusterSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_plugin_proxmox-api:proxmoxcluster-detail"
    )

    class Meta:
        model = ProxmoxNetboxMapping
        fields = ("id", "proxmox_url", "display", "url")


class ProxmoxNetboxMappingSerializer(NetBoxModelSerializer):
    site = SiteSerializer(many=False, nested=True)
    node_role = DeviceRoleSerializer(many=False, nested=True)
    node_device_type = DeviceTypeSerializer(many=False, nested=True)
    vm_role = DeviceRoleSerializer(many=False, nested=True)
    cluster_type = ClusterTypeSerializer(many=False, nested=True)
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_plugin_proxmox-api:proxmoxnetboxmapping-detail"
    )

    class Meta:
        model = ProxmoxNetboxMapping
        fields = (
            "id",
            "display",
            "name",
            "site",
            "node_role",
            "node_device_type",
            "vm_role",
            "cluster_type",
            "keep_interface_config",
            "created",
            "last_updated",
            "tags",
            "url",
        )


class ProxmoxClusterSerializer(NetBoxModelSerializer):
    netbox_mapping = NestedProxmoxNetboxMappingSerializer(many=False)
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_plugin_proxmox-api:proxmoxcluster-detail"
    )

    class Meta:
        model = ProxmoxCluster
        fields = (
            "id",
            "proxmox_url",
            "url",
            "username",
            "token_name",
            "token_value",
            "verify_tls",
            "enabled",
            "netbox_mapping",
            "display",
            "created",
            "last_updated",
            "tags",
        )
