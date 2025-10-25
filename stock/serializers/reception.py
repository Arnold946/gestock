from django.db import transaction
from rest_framework import serializers

from . import UniteDeMesureSerializer
from .fournisseur import FournisseurSerializer
from ..models import Reception, LigneReception, EntreeStock
from .produit import ProduitReadSerializer


class LigneReceptionReadSerializer(serializers.ModelSerializer):
    produit = ProduitReadSerializer(read_only=True)
    unite = UniteDeMesureSerializer(read_only=True)

    class Meta:
        model = LigneReception
        fields = ['id', 'produit', 'unite', 'quantite', 'prix_unitaire', 'sous_total']


class LigneReceptionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = LigneReception
        fields = ['produit', 'unite_utilisee', 'quantite', 'prix_unitaire']


class ReceptionReadSerializer(serializers.ModelSerializer):
    fournisseur = FournisseurSerializer(read_only=True)
    lignes = LigneReceptionReadSerializer(many=True, read_only=True)

    class Meta:
        model = Reception
        fields = ['id', 'fournisseur', 'date', 'total', 'remarque', 'lignes']


class ReceptionWriteSerializer(serializers.ModelSerializer):
    lignes = LigneReceptionWriteSerializer(many=True)

    class Meta:
        model = Reception
        fields = ['fournisseur', 'remarque', 'lignes']

    def create(self, validated_data):
        lignes_data = validated_data.pop('lignes')

        with transaction.atomic():
            reception = Reception.objects.create(**validated_data)

            total_reception = 0
            for ligne_data in lignes_data:
                produit = ligne_data['produit']
                quantite = ligne_data['quantite']
                prix_unitaire = ligne_data['prix_unitaire']
                unite = ligne_data['unite_utilisee']

                # Conversion en unité de base
                quantite_en_unite_base = produit.convertir_en_unite_base(quantite, unite)

                # Création de la ligne de réception
                ligne = LigneReception.objects.create(
                    reception=reception,
                    produit=produit,
                    quantite=quantite,
                    prix_unitaire=prix_unitaire,
                    unite_utilisee=unite
                )

                # Mise à jour du stock du produit
                produit.stock_actuel += quantite_en_unite_base
                produit.save()

                # Création de l'entrée de stock liée à la réception
                EntreeStock.objects.create(
                    produit=produit,
                    quantite=quantite,
                    unite_utilisee=unite,
                    type_entree='achat',
                    fournisseur=reception.fournisseur,
                    description=f"Entrée automatique liée à la réception n°{reception.id}"
                )

                # Calcul du total
                total_reception += quantite * prix_unitaire

        # Mise à jour du total de la réception
        reception.total = total_reception
        reception.save(update_fields=['total'])

        return reception
