from drf_spectacular.utils import extend_schema
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from users.permissions import HasPermissionFromRole
from ..models import UniteDeMesure
from ..serializers import UniteDeMesureSerializer

@extend_schema(tags=['Unites'])
class UniteDeMesureViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les unités de mesure.
    """
    queryset = UniteDeMesure.objects.all()
    serializer_class = UniteDeMesureSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'abreviation']
    ordering_fields = ['nom', 'abreviation']

    permission_classes = [IsAuthenticated, HasPermissionFromRole]

    required_permission = "stock.view_unitedemesure"

    def get_permissions(self):
        """
        Définit dynamiquement la permission requise selon l’action.
        """
        if self.action in ['create']:
            self.required_permission = "stock.add_unitedemesure"
        elif self.action in ['update', 'partial_update']:
            self.required_permission = "stock.change_unitedemesure"
        elif self.action in ['destroy']:
            self.required_permission = "stock.delete_unitedemesure"
        else:
            self.required_permission = "stock.view_unitedemesure"

        return super().get_permissions()