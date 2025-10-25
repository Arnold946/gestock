from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from stock.models import EntreeStock, SortieStock
from stock.serializers import ProduitReadSerializer, FournisseurSerializer, UniteDeMesureSerializer, ClientSerializer
from users.serializers import UserReadSerializer


class EntreeStockReadSerializer(serializers.ModelSerializer):
    produit = ProduitReadSerializer(read_only=True)
    fournisseur = FournisseurSerializer(read_only=True)
    unite_utilisee = UniteDeMesureSerializer(read_only=True)
    type_entree = serializers.CharField(source='get_type_entree_display', read_only=True)
    created_by = UserReadSerializer(read_only=True)
    updated_by = UserReadSerializer(read_only=True)

    class Meta:
        model = EntreeStock
        fields = ['id', 'produit', 'quantite', 'unite_utilisee', 'fournisseur', 'description', 'date', 'type_entree','created_by',
            'updated_by']

class EntreeStockWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntreeStock
        fields = ['produit', 'quantite', 'unite_utilisee', 'fournisseur', 'description', 'type_entree']

    def create(self, validated_data):
        produit = validated_data['produit']
        quantite_convertie = produit.convertir_en_unite_base(
            validated_data['quantite'],
            validated_data['unite_utilisee']
        )

        #creation + mise a jour du stock
        with transaction.atomic():
            entree = super().create(validated_data)
            produit.stock_actuel += quantite_convertie
            produit.save()

        return entree

class SortieStockReadSerializer(serializers.ModelSerializer):
    produit = ProduitReadSerializer(read_only=True)
    client = ClientSerializer(read_only=True)
    unite_utilisee = UniteDeMesureSerializer(read_only=True)
    type_sortie_display = serializers.CharField(source='get_type_sortie_display', read_only=True)
    created_by = UserReadSerializer(read_only=True)
    updated_by = UserReadSerializer(read_only=True)

    class Meta:
        model = SortieStock
        fields = [
            'id',
            'produit',
            'quantite',
            'unite_utilisee',
            'type_sortie',
            'type_sortie_display',
            'client',
            'date',
            'description',
            'created_by',
            'updated_by'
        ]


class SortieStockWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SortieStock
        fields = [
            'produit',
            'quantite',
            'unite_utilisee',
            'type_sortie',
            'client',
            'description',
    ]

    def create(self, validated_data):
        produit = validated_data['produit']
        quantite_convertie = produit.convertir_en_unite_base(
            validated_data['quantite'],
            validated_data['unite_utilisee']
        )
        sortie = super().create(validated_data)

        #verification de la disponibilité du stock
        if produit.stock_actuel < quantite_convertie:
            raise ValidationError("Stock insuffisant pour cette sortie.")

        #création + mise a jour du stock
        with transaction.atomic():
            produit.stock_actuel -= quantite_convertie
            produit.save()

        return sortie
