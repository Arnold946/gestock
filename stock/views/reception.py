from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from users.permissions import HasPermissionFromRole
from ..mixins import UserTrackMixin
from ..models import Reception, LigneReception
from ..serializers.reception import (
    ReceptionReadSerializer,
    ReceptionWriteSerializer,
    LigneReceptionReadSerializer,
    LigneReceptionWriteSerializer,
)


@extend_schema(tags=['Receptions'])
class ReceptionViewSet(UserTrackMixin,viewsets.ModelViewSet):
    queryset = Reception.objects.all().prefetch_related("lignes", "fournisseur")
    permission_classes = [IsAuthenticated, HasPermissionFromRole]
    required_permission = "stock.view_reception"

    def get_permissions(self):
        """
        Définit dynamiquement la permission requise selon l’action.
        """
        if self.action in ['list', 'retrieve']:
            self.required_permission = "stock.view_reception"
        elif self.action in ['create']:
            self.required_permission = "stock.add_reception"
        elif self.action in ['update', 'partial_update']:
            self.required_permission = "stock.change_reception"
        elif self.action == 'destroy':
            self.required_permission = "stock.delete_reception"
        else:
            self.required_permission = "stock.view_reception"
        return super().get_permissions()

    def get_serializer_class(self):
        """
        Sélectionne le serializer adapté à l’action.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return ReceptionWriteSerializer
        return ReceptionReadSerializer


@extend_schema(tags=['Lignes-reception'])
class LigneReceptionViewSet(viewsets.ModelViewSet):
    queryset = LigneReception.objects.all().select_related("produit", "reception")
    permission_classes = [IsAuthenticated, HasPermissionFromRole]
    required_permission = "stock.view_lignereception"

    def get_permissions(self):
        """
        Définit dynamiquement la permission requise selon l’action.
        """
        if self.action in ['list', 'retrieve']:
            self.required_permission = "stock.view_lignereception"
        elif self.action in ['create']:
            self.required_permission = "stock.add_lignereception"
        elif self.action in ['update', 'partial_update']:
            self.required_permission = "stock.change_lignereception"
        elif self.action == 'destroy':
            self.required_permission = "stock.delete_lignereception"
        else:
            self.required_permission = "stock.view_lignereception"
        return super().get_permissions()

    def get_serializer_class(self):
        """
        Sélectionne le serializer adapté à l’action.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return LigneReceptionWriteSerializer
        return LigneReceptionReadSerializer
