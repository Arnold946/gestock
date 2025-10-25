import pytest
from django.core.exceptions import ValidationError

from stock.models import UniteDeMesure


#--------------------------- TESTS ---------------------------#
def test_creation_produit(produit):
    assert produit.id is not None

def test_conversion_depuis_unite_base(produit, unite_base, unite_conversion):
    assert produit.convertir_en_unite_base(1, unite_base) == 1  # 1 g = 1 g

def test_conversion_depuis_unite_conversion(produit, unite_base, unite_conversion):
    assert produit.convertir_en_unite_base(2, unite_conversion) == 2000  # 2 kg = 2000 g

def test_conversion_unite_invalide(produit):
    autre = UniteDeMesure.objects.create(nom="Litre", symbole="L")
    quantite_invalide = produit.convertir_en_unite_base(1, autre)
    assert quantite_invalide is None  # Unité non reconnue

def test_facteur_conversion_zero_invalide(produit, unite_conversion):
    produit.facteur_conversion = 0
    with pytest.raises(ValidationError):
        produit.full_clean()