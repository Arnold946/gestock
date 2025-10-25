from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from users.permissions import HasPermissionFromRole
from ..models import Fournisseur
from ..serializers import FournisseurSerializer


@extend_schema(tags=['Fournisseurs'])
class FournisseurViewSet(viewsets.ModelViewSet):
    queryset = Fournisseur.objects.all()
    serializer_class = FournisseurSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'email', 'telephone']
    ordering_fields = ['nom', 'date_creation']

    permission_classes = [IsAuthenticated, HasPermissionFromRole]

    required_permission = "stock.view_fournisseur"

    def get_serializer_class(self):
        return FournisseurSerializer

    def get_permissions(self):
        """
        Définit dynamiquement la permission requise selon l’action.
        """
        if self.action in ['create']:
            self.required_permission = "stock.add_fournisseur"
        elif self.action in ['update', 'partial_update']:
            self.required_permission = "stock.change_fournisseur"
        elif self.action in ['destroy']:
            self.required_permission = "stock.delete_fournisseur"
        else:
            self.required_permission = "stock.view_fournisseur"

        return super().get_permissions()