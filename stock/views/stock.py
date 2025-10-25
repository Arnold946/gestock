from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from users.permissions import HasPermissionFromRole
from ..mixins import UserTrackMixin
from ..models import EntreeStock, SortieStock
from ..serializers import (
    EntreeStockReadSerializer,
    EntreeStockWriteSerializer,
    SortieStockReadSerializer,
    SortieStockWriteSerializer,
)

@extend_schema(tags=['Entree_stock'])
class EntreeStockViewSet(UserTrackMixin,viewsets.ModelViewSet):
    """
    ViewSet pour gérer les entrées de stock.
    """
    queryset = EntreeStock.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['produit__nom', 'fournisseur__nom']
    ordering_fields = ['date_entree', 'produit__nom']
    permission_classes = [IsAuthenticated, HasPermissionFromRole]

    def get_permissions(self):
        """
        Définit dynamiquement la permission requise selon l’action.
        """
        if self.action in ['list', 'retrieve']:
            self.required_permission = "stock.view_entreestock"
        elif self.action in ['create']:
            self.required_permission = "stock.add_entreestock"
        elif self.action in ['update', 'partial_update']:
            self.required_permission = "stock.change_entreestock"
        elif self.action == 'destroy':
            self.required_permission = "stock.delete_entreestock"
        else:
            self.required_permission = "stock.view_entreestock"
        return super().get_permissions()

    def get_serializer_class(self):
        """
        Choisit le serializer selon l’action.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return EntreeStockWriteSerializer
        return EntreeStockReadSerializer


@extend_schema(tags=['Sortie_stock'])
class SortieStockViewSet(UserTrackMixin,viewsets.ModelViewSet):
    """
    ViewSet pour gérer les sorties de stock.
    """
    queryset = SortieStock.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['produit__nom', 'client__nom']
    ordering_fields = ['date_sortie', 'produit__nom']
    permission_classes = [IsAuthenticated, HasPermissionFromRole]

    def get_permissions(self):
        """
        Définit dynamiquement la permission requise selon l’action.
        """
        if self.action in ['list', 'retrieve']:
            self.required_permission = "stock.view_sortiestock"
        elif self.action in ['create']:
            self.required_permission = "stock.add_sortiestock"
        elif self.action in ['update', 'partial_update']:
            self.required_permission = "stock.change_sortiestock"
        elif self.action == 'destroy':
            self.required_permission = "stock.delete_sortiestock"
        else:
            self.required_permission = "stock.view_sortiestock"
        return super().get_permissions()

    def get_serializer_class(self):
        """
        Choisit le serializer selon l’action.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return SortieStockWriteSerializer
        return SortieStockReadSerializer
