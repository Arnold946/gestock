import pytest

from stock.models import SortieStock


@pytest.mark.django_db
def test_edge_sortie_stock_quantite_negative(produit, unite_base):
    """[EDGE] Empêche une sortie avec une quantité négative"""
    with pytest.raises(Exception):
        SortieStock.objects.create(
            produit=produit,
            quantite=-5,
            unite_utilisee=unite_base,
            type_sortie="perte",
        )


@pytest.mark.django_db
def test_edge_sortie_stock_unite_invalide(produit):
    """[EDGE] Empêche une sortie avec une unité non valide pour le produit"""
    with pytest.raises(Exception):
        SortieStock.objects.create(
            produit=produit,
            quantite=5,
            unite_utilisee="km",
            type_sortie="autre",
        )


@pytest.mark.django_db
def test_edge_sortie_stock_type_invalide(produit, unite_base):
    """[EDGE] Empêche une sortie avec un type_sortie invalide"""
    with pytest.raises(Exception):
        SortieStock.objects.create(
            produit=produit,
            quantite=1,
            unite_utilisee=unite_base,
            type_sortie="invalide",  # ⚠️ pas dans la liste
        )