# Generated by Django 4.2.5 on 2023-10-04 10:09

from django.db import migrations, models
import django.db.models.deletion
import taggit.managers
import utilities.json


def create_initial_data(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    CustomField = apps.get_model("extras", "CustomField")
    content_type = ContentType.objects.get(
        app_label="virtualization", model="virtualmachine"
    )
    try:
        vmid = CustomField.objects.get(
            name="proxmox_vmid", type="integer", object_types=[content_type]
        )
    except:
        vmid = CustomField(
            name="proxmox_vmid",
            type="text",
        )
    vmid.save()
    vmid.object_types.set([content_type.id])
    vmid.filter_logic = "exact"
    vmid.ui_visibility = "read-only"
    vmid.is_cloneable = False
    vmid.save()


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("extras", "0098_webhook_custom_field_data_webhook_tags"),
        ("dcim", "0181_rename_device_role_device_role"),
        ("virtualization", "0036_virtualmachine_config_template"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProxmoxNetboxMapping",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=utilities.json.CustomFieldJSONEncoder,
                    ),
                ),
                ("name", models.CharField(max_length=500)),
                ("keep_interface_config", models.BooleanField(default=True)),
                (
                    "cluster_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="virtualization.clustertype",
                    ),
                ),
                (
                    "node_device_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="dcim.devicetype",
                    ),
                ),
                (
                    "node_role",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="node_role_maping",
                        to="dcim.devicerole",
                    ),
                ),
                (
                    "site",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="dcim.site"
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        through="extras.TaggedItem", to="extras.Tag"
                    ),
                ),
                (
                    "vm_role",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="vm_role_mapping",
                        to="dcim.devicerole",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ProxmoxCluster",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=utilities.json.CustomFieldJSONEncoder,
                    ),
                ),
                ("username", models.CharField(max_length=500)),
                ("token_name", models.CharField(max_length=500)),
                ("token_value", models.CharField(max_length=500)),
                ("verify_tls", models.BooleanField(default=True)),
                ("enabled", models.BooleanField(default=True)),
                ("proxmox_url", models.CharField(max_length=500)),
                (
                    "netbox_mapping",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="netbox_config_maping",
                        to="netbox_plugin_proxmox.proxmoxnetboxmapping",
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        through="extras.TaggedItem", to="extras.Tag"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.RunPython(create_initial_data),
    ]
