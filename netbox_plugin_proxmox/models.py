from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from django.utils.translation import gettext_lazy as _


class ProxmoxCluster(NetBoxModel):
    proxmox_url = models.CharField(max_length=500)
    username = models.CharField(max_length=500)
    token_name = models.CharField(max_length=500)
    token_value = models.CharField(max_length=500)
    verify_tls = models.BooleanField(default=True)
    enabled = models.BooleanField(default=True)
    netbox_mapping = models.ForeignKey(
        to="netbox_plugin_proxmox.ProxmoxNetboxMapping",
        on_delete=models.CASCADE,
        related_name="netbox_config_maping",
        null=False,
        blank=False,
        verbose_name=_("Proxmox to NetBox Mapping"),
    )

    def get_absolute_url(self):
        return reverse("plugins:netbox_plugin_proxmox:proxmoxcluster", args=[self.pk])

    def __str__(self):
        return self.proxmox_url

    def to_config_dict(self):
        return {
            "url": self.proxmox_url,
            "username": self.username,
            "token": {
                "name": self.token_name,
                "value": self.token_value,
            },
            "verify_ssl": self.verify_tls,
            "netbox": self.netbox_mapping.to_config_dict(),
        }


class ProxmoxNetboxMapping(NetBoxModel):
    name = models.CharField(max_length=500)
    site = models.ForeignKey(
        to="dcim.Site",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    node_role = models.ForeignKey(
        to="dcim.DeviceRole",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="node_role_maping",
    )
    node_device_type = models.ForeignKey(
        to="dcim.DeviceType",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    vm_role = models.ForeignKey(
        to="dcim.DeviceRole",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="vm_role_mapping",
    )
    cluster_type = models.ForeignKey(
        to="virtualization.ClusterType",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    keep_interface_config = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse(
            "plugins:netbox_plugin_proxmox:proxmoxnetboxmapping", args=[self.pk]
        )

    def __str__(self):
        return self.name

    def to_config_dict(self):
        return {
            "site_id": self.site.id,
            "node_role_id": self.node_role.id,
            "node_device_type_id": self.node_device_type.id,
            "vm_role_id": self.vm_role.id,
            "cluster_type_id": self.cluster_type.id,
            "keep_interface_config": self.keep_interface_config,
        }
