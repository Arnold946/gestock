from rest_framework import serializers

from stock.models import Fournisseur


class FournisseurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fournisseur
        fields = ['id', 'nom', 'email', 'telephone', 'adresse']