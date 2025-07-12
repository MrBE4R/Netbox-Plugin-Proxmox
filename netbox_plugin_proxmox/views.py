from django.http import StreamingHttpResponse
from django.shortcuts import render
from netbox.views import generic
from django.views.generic import View
from django.http import JsonResponse
from .cluster import get_or_create_and_update_clusters
from . import forms, models, tables


class ProxmoxStatus(View):
    def get(self, request):
        return render(request, "netbox_plugin_proxmox/sync_status.html")


def ProxmoxSync(request):
    return StreamingHttpResponse(
        get_or_create_and_update_clusters(), content_type="text/event-stream"
    )


class ProxmoxClusterView(generic.ObjectView):
    queryset = models.ProxmoxCluster.objects.all()


class ProxmoxClusterListView(generic.ObjectListView):
    queryset = models.ProxmoxCluster.objects.all()
    table = tables.ProxmoxClusterTable


class ProxmoxClusterEditView(generic.ObjectEditView):
    queryset = models.ProxmoxCluster.objects.all()
    form = forms.ProxmoxClusterForm


class ProxmoxClusterDeleteView(generic.ObjectDeleteView):
    queryset = models.ProxmoxCluster.objects.all()


class ProxmoxNetboxMappingView(generic.ObjectView):
    queryset = models.ProxmoxNetboxMapping.objects.all()


class ProxmoxNetboxMappingListView(generic.ObjectListView):
    queryset = models.ProxmoxNetboxMapping.objects.all()
    table = tables.ProxmoxNetboxMappingTable


class ProxmoxNetboxMappingEditView(generic.ObjectEditView):
    queryset = models.ProxmoxNetboxMapping.objects.all()
    form = forms.ProxmoxNetboxMappingForm


class ProxmoxNetboxMappingDeleteView(generic.ObjectDeleteView):
    queryset = models.ProxmoxNetboxMapping.objects.all()
