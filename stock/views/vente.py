from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from users.permissions import HasPermissionFromRole
from ..mixins import UserTrackMixin
from ..models import Vente, LigneVente
from ..serializers import (
    VenteReadSerializer,
    VenteWriteSerializer,
    LigneVenteReadSerializer,
    LigneVenteWriteSerializer,
)

@extend_schema(tags=['Ventes'])
class VenteViewSet(UserTrackMixin,viewsets.ModelViewSet):
    """
    ViewSet pour gérer les ventes avec permissions dynamiques et code propre.
    """
    queryset = Vente.objects.all().order_by('-date')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['client__nom', 'mode_paiement__nom']
    ordering_fields = ['date', 'total', 'montant_paye']

    permission_classes = [IsAuthenticated, HasPermissionFromRole]
    required_permission = "stock.view_vente"  # par défaut

    def get_serializer_class(self):
        """Retourne le serializer selon l'action."""
        if self.action in ['list', 'retrieve']:
            return VenteReadSerializer
        return VenteWriteSerializer

    def get_permissions(self):
        """Définit dynamiquement la permission selon l’action."""
        if self.action == 'create':
            self.required_permission = "stock.add_vente"
        elif self.action in ['update', 'partial_update']:
            self.required_permission = "stock.change_vente"
        elif self.action == 'destroy':
            self.required_permission = "stock.delete_vente"
        else:
            self.required_permission = "stock.view_vente"
        return super().get_permissions()


@extend_schema(tags=['Lignes-vente'])
class LigneVenteViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les lignes de vente avec permissions dynamiques et code propre.
    """
    queryset = LigneVente.objects.all().select_related('vente', 'produit')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['vente__id', 'produit__nom']
    ordering_fields = ['vente__date', 'produit__nom', 'quantite']

    permission_classes = [IsAuthenticated, HasPermissionFromRole]
    required_permission = "stock.view_lignevente"  # par défaut

    def get_serializer_class(self):
        """Retourne le serializer selon l'action."""
        if self.action in ['list', 'retrieve']:
            return LigneVenteReadSerializer
        return LigneVenteWriteSerializer

    def get_permissions(self):
        """Définit dynamiquement la permission selon l’action."""
        if self.action == 'create':
            self.required_permission = "stock.add_lignevente"
        elif self.action in ['update', 'partial_update']:
            self.required_permission = "stock.change_lignevente"
        elif self.action == 'destroy':
            self.required_permission = "stock.delete_lignevente"
        else:
            self.required_permission = "stock.view_lignevente"
        return super().get_permissions()
