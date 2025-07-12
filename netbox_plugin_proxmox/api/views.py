from netbox.api.viewsets import NetBoxModelViewSet

from .. import models
from .serializers import ProxmoxNetboxMappingSerializer, ProxmoxClusterSerializer


class ProxmoxNetboxMappingViewSet(NetBoxModelViewSet):
    queryset = models.ProxmoxNetboxMapping.objects.prefetch_related("tags")
    serializer_class = ProxmoxNetboxMappingSerializer


class ProxmoxClusterViewSet(NetBoxModelViewSet):
    queryset = models.ProxmoxCluster.objects.prefetch_related("tags")
    serializer_class = ProxmoxClusterSerializer
