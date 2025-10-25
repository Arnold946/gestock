from rest_framework import serializers

from stock.models import UniteDeMesure


class UniteDeMesureSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniteDeMesure
        fields = ['id', 'nom', 'symbole']