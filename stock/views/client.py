from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from users.permissions import HasPermissionFromRole

from ..models import Client
from ..serializers import ClientSerializer


@extend_schema(tags=['Clients'])
class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les clients :
    - Lecture, création, modification, suppression
    - Avec permissions dynamiques basées sur les rôles
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'email', 'telephone']
    ordering_fields = ['nom', 'date_creation']

    # Permissions globales
    permission_classes = [IsAuthenticated, HasPermissionFromRole]

    # Par défaut, lecture
    required_permission = "stock.view_client"

    def get_serializer_class(self):
        """
        Utilise le même serializer pour lecture et écriture.
        """
        return ClientSerializer

    def get_permissions(self):
        """
        Définit dynamiquement la permission requise selon l’action.
        """
        if self.action in ['create']:
            self.required_permission = "stock.add_client"
        elif self.action in ['update', 'partial_update']:
            self.required_permission = "stock.change_client"
        elif self.action in ['destroy']:
            self.required_permission = "stock.delete_client"
        else:
            self.required_permission = "stock.view_client"

        return super().get_permissions()
