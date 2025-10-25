from rest_framework import serializers
from django.contrib.auth.models import Permission
from .models import Interface, Role, User


# ------------------------------
# 🔹 SERIALIZER DES PERMISSIONS
# ------------------------------
class PermissionSerializer(serializers.ModelSerializer):
    """
    Sert à afficher les informations d’une permission Django.
    (nom lisible, code interne, et type de contenu associé)
    """
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']
        read_only_fields = fields  # Toutes les permissions sont en lecture seule


# ------------------------------
# 🔹 INTERFACE : READ
# ------------------------------
class InterfaceReadSerializer(serializers.ModelSerializer):
    """
    Sérialiseur de lecture pour afficher une interface
    (ex : Stock, Ventes, Rapports) avec la liste de ses permissions.
    """
    # On inclut ici les détails complets des permissions (lecture seule)
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Interface
        fields = ['id', 'nom', 'description', 'permissions']


# ------------------------------
# 🔹 INTERFACE : WRITE
# ------------------------------
class InterfaceWriteSerializer(serializers.ModelSerializer):
    """
    Sérialiseur d’écriture pour créer/modifier une interface.
    On ne transmet que les IDs des permissions à associer.
    """
    permissions = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all(),  # Autorise toutes les permissions existantes
        required=False
    )

    class Meta:
        model = Interface
        fields = ['nom', 'description', 'permissions']


# ------------------------------
# 🔹 ROLE : READ
# ------------------------------
class RoleReadSerializer(serializers.ModelSerializer):
    """
    Sérialiseur de lecture pour afficher un rôle complet :
    - ses permissions détaillées
    - ses interfaces accessibles
    """
    permissions = PermissionSerializer(many=True, read_only=True)
    interfaces = InterfaceReadSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'nom', 'description', 'permissions', 'interfaces']


# ------------------------------
# 🔹 ROLE : WRITE
# ------------------------------
class RoleWriteSerializer(serializers.ModelSerializer):
    """
    Sérialiseur d’écriture pour créer ou modifier un rôle.
    Les relations sont transmises via leurs IDs.
    """
    permissions = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all(),
        required=False
    )
    interfaces = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Interface.objects.all(),
        required=False
    )

    class Meta:
        model = Role
        fields = ['nom', 'description', 'permissions', 'interfaces']


# ------------------------------
# 🔹 USER : READ
# ------------------------------
class UserReadSerializer(serializers.ModelSerializer):
    """
    Sérialiseur de lecture pour afficher un utilisateur
    avec ses rôles et leurs détails.
    """
    roles = RoleReadSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'roles']


# ------------------------------
# 🔹 USER : WRITE
# ------------------------------
class UserWriteSerializer(serializers.ModelSerializer):
    """
    Sérialiseur d’écriture pour la création/modification d’utilisateur :
    - mot de passe chiffré automatiquement
    - association de rôles via leurs IDs
    """
    roles = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Role.objects.all(),
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'roles']
        extra_kwargs = {
            'password': {'write_only': True},  # On ne renvoie jamais le mot de passe
        }

    def create(self, validated_data):
        """
        Lors de la création, on gère :
        - le hash du mot de passe
        - l’attribution des rôles
        """
        roles = validated_data.pop('roles', [])
        user = User.objects.create_user(**validated_data)  # Utilise la méthode Django sécurisée
        user.roles.set(roles)
        return user

    def update(self, instance, validated_data):
        """
        Lors de la mise à jour :
        - on chiffre le mot de passe s’il est modifié
        - on met à jour les rôles si fournis
        """
        roles = validated_data.pop('roles', None)
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)  # Hash sécurisé
            else:
                setattr(instance, attr, value)
        instance.save()
        if roles is not None:
            instance.roles.set(roles)
        return instance
