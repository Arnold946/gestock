from rest_framework import serializers

from stock.models import ModePaiement


class ModePaiementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModePaiement
        fields = ['id', 'nom', 'description']