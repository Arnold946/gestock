from django.core.exceptions import ValidationError
from django.db import models


class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom

class Produit(models.Model):
    nom = models.CharField(max_length=150)
    reference = models.CharField(max_length=100, unique=True)
    categorie = models.ForeignKey('Categorie', on_delete=models.CASCADE)
    unite = models.ForeignKey('UniteDeMesure', on_delete=models.CASCADE, related_name='produits')
    unite_conversion = models.ForeignKey('UniteDeMesure', on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='produits_convertibles')
    facteur_conversion = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True, null=True)
    seuil_alerte = models.IntegerField(default=5)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    date_ajout = models.DateTimeField(auto_now_add=True)
    stock_actuel = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nom} ({self.reference})"

    def convertir_en_unite_base(self, quantite, unite_utilisee):
        from .unite import UniteDeMesure
        
        if unite_utilisee == self.unite:
            return quantite
        elif unite_utilisee == self.unite_conversion and self.facteur_conversion:
            return quantite * self.facteur_conversion
        return None

    def clean(self):
        """Validation métier avant sauvegarde"""
        if self.facteur_conversion <= 0:
            raise ValidationError("Le facteur de conversion doit être strictement positif.")
        if self.stock_actuel < 0:
            raise ValidationError("Le stock actuel ne peut pas être négatif.")