import pytest

from stock.models import EntreeStock


@pytest.mark.django_db
def test_edge_entree_stock_sans_fournisseur_achat(produit, unite_base):
    """[EDGE] Un achat sans fournisseur doit lever une erreur"""
    with pytest.raises(Exception) as excinfo:
        EntreeStock.objects.create(
            produit=produit,
            quantite=5,
            unite_utilisee=unite_base,
            type_entree="achat",
            fournisseur=None,
        )
    assert "Un fournisseur est requis" in str(excinfo.value)


@pytest.mark.django_db
def test_edge_entree_stock_quantite_negative(produit, unite_base, fournisseur):
    """[EDGE] Empêche une entrée avec une quantité négative"""
    with pytest.raises(Exception):
        EntreeStock.objects.create(
            produit=produit,
            quantite=-10,
            unite_utilisee=unite_base,
            type_entree="achat",
            fournisseur=fournisseur,
        )


@pytest.mark.django_db
def test_edge_entree_stock_sans_unite(produit, fournisseur):
    """[EDGE] Une entrée sans unité doit échouer"""
    with pytest.raises(Exception):
        EntreeStock.objects.create(
            produit=produit,
            quantite=5,
            unite_utilisee=None,
            type_entree="achat",
            fournisseur=fournisseur,
        )