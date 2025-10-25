import pytest

from stock.models import Categorie, UniteDeMesure, Produit, Fournisseur


@pytest.fixture
def categorie(db):
    return Categorie.objects.create(nom="Catégorie Test")

@pytest.fixture
def unite_base(db):
    return UniteDeMesure.objects.create(nom="Gramme", symbole="g")

@pytest.fixture
def unite_conversion(db):
    return UniteDeMesure.objects.create(nom="Kilogramme", symbole="kg")

@pytest.fixture
def produit(db, categorie, unite_base, unite_conversion):
    return Produit.objects.create(
        nom="Produit Test",
        reference="REF123",
        categorie=categorie,
        unite=unite_base,
        unite_conversion=unite_conversion,
        facteur_conversion=1000,
        prix_unitaire=10.00,
        stock_actuel=0
    )

@pytest.fixture
def fournisseur(db):
    return Fournisseur.objects.create(nom="Fournisseur Test")