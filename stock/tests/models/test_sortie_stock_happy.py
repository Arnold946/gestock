import pytest
from stock.models import SortieStock

@pytest.mark.django_db
def test_happy_sortie_stock_creation(produit, unite_base):
    """[HAPPY] Une sortie de stock valide est bien créée"""
    sortie = SortieStock.objects.create(
        produit=produit,
        quantite=5,
        unite_utilisee=unite_base,
        type_sortie="don",
    )
    assert sortie.produit == produit
    assert sortie.quantite == 5
    assert sortie.unite_utilisee == unite_base
    assert sortie.type_sortie == "don"

@pytest.mark.django_db
def test_happy_sortie_stock_conversion(produit, unite_conversion):
    """[HAPPY] Conversion automatique en unité de base (g)"""
    sortie = SortieStock.objects.create(
        produit=produit,
        quantite=2,  # 2 kg
        unite_utilisee=unite_conversion,
        type_sortie="usage_interne",
    )
    assert sortie.quantite_en_unite_base() == 2000  # 2000 g
