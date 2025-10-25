from rest_framework.permissions import BasePermission


class HasPermissionFromRole(BasePermission):
    """
    Vérifie si l'utilisateur connecté possède la permission Django requise
    pour accéder à une vue donnée.
    """

    def has_permission(self, request, view):
        """
        Méthode principale appelée par Django REST Framework avant d'exécuter la vue.
        Retourne True si l'utilisateur a la permission requise, sinon False.
        """

        # Vérifier si l'utilisateur est authentifié
        # Si ce n'est pas le cas, on refuse l'accès immédiatement
        if not request.user.is_authenticated:
            return False

        # Récupérer la permission requise depuis la vue
        # Certaines vues peuvent définir un attribut 'required_permission'
        # ex: required_permission = "stock.view_produit"
        required_permission = getattr(view, 'required_permission', None)

        # Si la vue ne définit pas de permission spécifique,
        # on autorise l'accès par défaut (optionnel selon la politique de sécurité)
        if not required_permission:
            return True

        # Vérifier si l'utilisateur possède la permission requise
        # La méthode has_perm() est héritée du modèle User
        # Elle prend en compte les permissions directes et celles héritées via les rôles
        return request.user.has_perm(required_permission)
