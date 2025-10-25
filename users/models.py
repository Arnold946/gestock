# accounts/models.py
from django.contrib.auth.models import AbstractUser, Permission
from django.db import models


class Interface(models.Model):
    """Zone fonctionnelle de l'application (Stock, Ventes, Rapports)."""
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, blank=True, related_name="interfaces")

    def __str__(self):
        return self.nom


class Role(models.Model):
    """Rôle métier = ensemble de permissions et d’interfaces."""
    nom = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, blank=True, related_name="roles")
    interfaces = models.ManyToManyField(Interface, blank=True, related_name="roles")

    def __str__(self):
        return self.nom


class User(AbstractUser):
    """Utilisateur avec un ou plusieurs rôles."""
    roles = models.ManyToManyField(Role, blank=True, related_name="users")

    def get_all_permissions(self):
        """Retourne toutes les permissions (directes + via rôles)."""
        user_permissions = set(self.user_permissions.all())
        role_permissions = Permission.objects.filter(roles__users=self)
        return user_permissions.union(role_permissions)

    def has_perm(self, perm, obj=None):
        """Vérifie si l’utilisateur possède une permission donnée."""
        all_perms = {f"{p.content_type.app_label}.{p.codename}" for p in self.get_all_permissions()}
        return perm in all_perms

    def has_module_perms(self, app_label):
        """Vérifie si l’utilisateur a accès à un module (app)."""
        return any(p.content_type.app_label == app_label for p in self.get_all_permissions())