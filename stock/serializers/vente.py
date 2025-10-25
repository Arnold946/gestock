from django.db import transaction
from rest_framework import serializers

from users.serializers import UserReadSerializer
from . import UniteDeMesureSerializer
from .client import ClientSerializer
from .paiement import ModePaiementSerializer
from ..models import Vente, LigneVente, SortieStock
from .produit import ProduitReadSerializer


class LigneVenteReadSerializer(serializers.ModelSerializer):
    produit = ProduitReadSerializer(read_only=True)
    unite = UniteDeMesureSerializer(read_only=True)
    class Meta:
        model = LigneVente
        fields = ['id', 'produit', 'unite', 'quantite', 'prix_unitaire', 'sous_total']


class LigneVenteWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = LigneVente
        fields = ['produit', 'unite_utilisee', 'quantite', 'prix_unitaire']


class VenteReadSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    mode_paiement = ModePaiementSerializer(read_only=True)
    lignes = LigneVenteReadSerializer(many=True, read_only=True)
    created_by = UserReadSerializer(read_only=True)
    updated_by = UserReadSerializer(read_only=True)

    class Meta:
        model = Vente
        fields = ['id', 'client', 'date', 'total', 'mode_paiement', 'remarque', 'lignes','created_by',
            'updated_by']


class VenteWriteSerializer(serializers.ModelSerializer):
    lignes = LigneVenteWriteSerializer(many=True)

    class Meta:
        model = Vente
        fields = ['client', 'mode_paiement', 'remarque', 'lignes']

    def create(self, validated_data):
        lignes_data = validated_data.pop('lignes')

        with transaction.atomic():
            vente = Vente.objects.create(**validated_data)

            total_vente = 0
            for ligne_data in lignes_data:
                produit = ligne_data['produit']
                quantite = ligne_data['quantite']
                prix_unitaire = ligne_data['prix_unitaire']
                unite = ligne_data['unite_utilisee']

                # Conversion en unité de base
                quantite_en_unite_base = produit.convertir_en_unite_base(quantite, unite)

                # Vérification du stock disponible
                if produit.stock_actuel < quantite_en_unite_base:
                    raise serializers.ValidationError(
                        f"Le stock du produit {produit.nom} est insuffisant pour la quantité demandée."
                    )

                # Création de la ligne de vente
                ligne = LigneVente.objects.create(
                    vente=vente,
                    produit=produit,
                    quantite=quantite,
                    prix_unitaire=prix_unitaire,
                    unite_utilisee=unite
                )

                # Mise à jour du stock du produit
                produit.stock_actuel -= quantite_en_unite_base
                produit.save()

                # Création de la sortie de stock liée à la vente
                SortieStock.objects.create(
                    produit=produit,
                    quantite=quantite,
                    unite_utilisee=unite,
                    type_sortie='vente',
                    client=vente.client,
                    description=f"Sortie automatique liée à la vente n°{vente.id}"
                )

                # Calcul du total
                total_vente += quantite * prix_unitaire

        # Mise à jour du total de la vente
        vente.total = total_vente
        vente.save(update_fields=['total'])

        return vente


