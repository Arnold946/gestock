from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from users.permissions import HasPermissionFromRole
from ..models import Categorie, Produit
from ..serializers import CategorieSerializer, ProduitReadSerializer, ProduitWriteSerializer


@extend_schema(tags=['Categories'])
class CategorieViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les catégories de produits.
    """
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom']
    ordering_fields = ['nom', 'date_creation']

    # Permissions par défaut : lecture seule
    permission_classes = [IsAuthenticated, HasPermissionFromRole]
    required_permission = "stock.view_categorie"

    def get_permissions(self):
        """
        Change dynamiquement la permission Django selon l’action.
        """
        if self.action == 'create':
            self.required_permission = "stock.add_categorie"
        elif self.action in ['update', 'partial_update']:
            self.required_permission = "stock.change_categorie"
        elif self.action == 'destroy':
            self.required_permission = "stock.delete_categorie"
        else:
            self.required_permission = "stock.view_categorie"
        return super().get_permissions()


@extend_schema(tags=['Produits'])
class ProduitViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les produits.
    """
    queryset = Produit.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'reference', 'categorie__nom']
    ordering_fields = ['nom', 'quantite_stock', 'date_ajout']

    permission_classes = [IsAuthenticated, HasPermissionFromRole]
    required_permission = "stock.view_produit"  # par défaut

    def get_permissions(self):
        """
        Définit dynamiquement la permission Django requise selon l’action.
        """
        if self.action == 'create':
            self.required_permission = "stock.add_produit"
        elif self.action in ['update', 'partial_update']:
            self.required_permission = "stock.change_produit"
        elif self.action == 'destroy':
            self.required_permission = "stock.delete_produit"
        else:
            self.required_permission = "stock.view_produit"
        return super().get_permissions()

    def get_serializer_class(self):
        """
        Sélectionne le serializer adapté à l’action :
        - Lecture : ProduitReadSerializer
        - Écriture : ProduitWriteSerializer
        """
        if self.action in ['list', 'retrieve']:
            return ProduitReadSerializer
        return ProduitWriteSerializer
