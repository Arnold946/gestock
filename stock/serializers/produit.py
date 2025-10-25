from rest_framework import serializers

from stock.models import Categorie, Produit
from .unite import UniteDeMesureSerializer

class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ['id', 'nom']

class ProduitReadSerializer(serializers.ModelSerializer):
    categorie = CategorieSerializer(read_only=True)
    unite = UniteDeMesureSerializer(read_only=True)
    unite_conversion = UniteDeMesureSerializer(read_only=True)

    class Meta:
        model = Produit
        fields = [
            'id',
            'nom',
            'reference',
            'categorie',
            'unite',
            'unite_conversion',
            'facteur_conversion',
            'prix_unitaire',
            'description',
            'seuil_alerte',
            'stock_actuel',
            'date_ajout',
        ]
        read_only_fields = ['date_ajout']

class ProduitWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = [
            'nom',
            'reference',
            'categorie',
            'unite',
            'unite_conversion',
            'facteur_conversion',
            'prix_unitaire',
            'description',
            'seuil_alerte',
        ]