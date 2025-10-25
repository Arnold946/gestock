from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from users.permissions import HasPermissionFromRole
from ..models import ModePaiement
from ..serializers import ModePaiementSerializer


@extend_schema(tags=['Mode_paiement'])
class ModePaiementViewSet(viewsets.ModelViewSet):
    queryset = ModePaiement.objects.all()
    serializer_class = ModePaiementSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'description']
    ordering_fields = ['nom']

    permission_classes = [IsAuthenticated, HasPermissionFromRole]

    required_permission = "stock.view_modepaiement"

    def get_serializer_class(self):
        return ModePaiementSerializer

    def get_permissions(self):
        """
        Définit dynamiquement la permission requise selon l’action.
        """
        if self.action in ['create']:
            self.required_permission = "stock.add_modepaiement"
        elif self.action in ['update', 'partial_update']:
            self.required_permission = "stock.change_modepaiement"
        elif self.action in ['destroy']:
            self.required_permission = "stock.delete_modepaiement"
        else:
            self.required_permission = "stock.view_modepaiement"

        return super().get_permissions()