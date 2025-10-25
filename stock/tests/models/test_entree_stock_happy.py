import pytest

from stock.models import EntreeStock


@pytest.mark.django_db
def test_happy_entree_stock_ajout_quantite(produit, unite_base, fournisseur):
    """[HAPPY] Vérifie que le stock augmente correctement avec une entrée classique"""
    entree = EntreeStock.objects.create(
        produit=produit,
        quantite=5,
        unite_utilisee=unite_base,
        type_entree="achat",
        fournisseur=fournisseur,
    )
    assert entree.id is not None
    assert entree.quantite_en_unite_base() == 5

    produit.refresh_from_db()
    assert produit.stock_actuel == 5


@pytest.mark.django_db
def test_happy_entree_stock_autre_type_sans_fournisseur(produit, unite_base):
    """[HAPPY] Vérifie qu’un don peut être enregistré sans fournisseur"""
    entree = EntreeStock.objects.create(
        produit=produit,
        quantite=5,
        unite_utilisee=unite_base,
        type_entree="don_recu",
        fournisseur=None,
    )
    assert entree.id is not None
    assert entree.quantite_en_unite_base() == 5

    produit.refresh_from_db()
    assert produit.stock_actuel == 5


@pytest.mark.django_db
def test_happy_entree_stock_conversion_unite(produit, unite_conversion, fournisseur):
    """[HAPPY] Vérifie la conversion d’unités lors d’une entrée"""
    entree = EntreeStock.objects.create(
        produit=produit,
        quantite=2,  # 2 kg
        unite_utilisee=unite_conversion,
        type_entree="achat",
        fournisseur=fournisseur,
    )
    assert entree.id is not None
    assert entree.quantite_en_unite_base() == 2000  # 2000 g

    produit.refresh_from_db()
    assert produit.stock_actuel == 2000