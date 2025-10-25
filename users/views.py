from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from users.permissions import HasPermissionFromRole

from .models import Interface, Role, User
from .serializers import (
    InterfaceReadSerializer, InterfaceWriteSerializer,
    RoleReadSerializer, RoleWriteSerializer,
    UserReadSerializer, UserWriteSerializer
)

# ============================================================
# 🔹 INTERFACE VIEWSET
# ============================================================
@extend_schema(tags=['Interfaces'])
class InterfaceViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les interfaces :
    - Lecture (GET)
    - Création (POST)
    - Modification (PUT/PATCH)
    - Suppression (DELETE)
    """
    queryset = Interface.objects.all()

    # 🔒 Permissions de sécurité
    permission_classes = [IsAuthenticated, HasPermissionFromRole]
    required_permission = "users.view_interface"

    def get_serializer_class(self):
        """Renvoie le serializer selon l’action"""
        if self.action in ['create', 'update', 'partial_update']:
            return InterfaceWriteSerializer
        return InterfaceReadSerializer

    def get_permissions(self):
        """Définit dynamiquement la permission Django selon l’action"""
        if self.action == 'create':
            self.required_permission = "users.add_interface"
        elif self.action in ['update', 'partial_update']:
            self.required_permission = "users.change_interface"
        elif self.action == 'destroy':
            self.required_permission = "users.delete_interface"
        else:
            self.required_permission = "users.view_interface"
        return super().get_permissions()


# ============================================================
# 🔹 ROLE VIEWSET
# ============================================================
@extend_schema(tags=['Roles'])
class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les rôles :
    - Chaque rôle peut avoir plusieurs permissions et interfaces associées.
    """
    queryset = Role.objects.prefetch_related('interfaces', 'permissions').all()

    permission_classes = [IsAuthenticated, HasPermissionFromRole]
    required_permission = "users.view_role"

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RoleWriteSerializer
        return RoleReadSerializer

    def get_permissions(self):
        """Définit dynamiquement la permission Django selon l’action"""
        if self.action == 'create':
            self.required_permission = "users.add_role"
        elif self.action in ['update', 'partial_update']:
            self.required_permission = "users.change_role"
        elif self.action == 'destroy':
            self.required_permission = "users.delete_role"
        else:
            self.required_permission = "users.view_role"
        return super().get_permissions()


# ============================================================
# 🔹 USER VIEWSET
# ============================================================
@extend_schema(tags=['Users'])
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les utilisateurs :
    - Gère aussi l’association des rôles
    - Précharge les rôles et leurs permissions pour optimiser les requêtes
    """
    queryset = User.objects.prefetch_related('roles__interfaces', 'roles__permissions')

    permission_classes = [IsAuthenticated, HasPermissionFromRole]
    required_permission = "users.view_user"

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UserWriteSerializer
        return UserReadSerializer

    def get_permissions(self):
        """Définit dynamiquement la permission Django selon l’action"""
        if self.action == 'create':
            self.required_permission = "users.add_user"
        elif self.action in ['update', 'partial_update']:
            self.required_permission = "users.change_user"
        elif self.action == 'destroy':
            self.required_permission = "users.delete_user"
        else:
            self.required_permission = "users.view_user"
        return super().get_permissions()
