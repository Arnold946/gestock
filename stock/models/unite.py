from django.db import models


class UniteDeMesure(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    symbole = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.nom} ({self.symbole})" if self.symbole else self.nom