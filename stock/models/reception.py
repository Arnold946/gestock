from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone

from stock.models import Produit


class Reception(models.Model):
    fournisseur = models.ForeignKey('Fournisseur', on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True, null=True)

    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    montant_paye = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    reliquat_fournisseur = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    reliquat_magasin = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    remarque = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    # Ajout de la traçabilité
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='receptions_creees'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='receptions_modifiees'
    )

    def __str__(self):
        return f"Réception #{self.id}"

    def calculer_reliquat(self):
        """Calcule le reliquat fournisseur/magasin en fonction du paiement."""
        if self.montant_paye < self.total:
            self.reliquat_fournisseur = self.total - self.montant_paye
            self.reliquat_magasin = 0
        elif self.montant_paye > self.total:
            self.reliquat_fournisseur = 0
            self.reliquat_magasin = self.montant_paye - self.total
        else:
            self.reliquat_fournisseur = 0
            self.reliquat_magasin = 0

        self.save(update_fields=['reliquat_fournisseur', 'reliquat_magasin'])

    def calculer_total(self):
        """Recalcule le total de la réception en fonction des lignes actives."""
        total = 0
        for ligne in self.lignes_reception.filter(is_active=True):
            total += ligne.quantite * ligne.produit.prix_unitaire
        self.total = total
        self.save(update_fields=['total'])
        self.calculer_reliquat()

    def soft_delete(self):
        """
        Annuler une réception complète :
        - Restitue le stock de toutes les lignes actives
        - Désactive les lignes
        - Met les montants à zéro
        """
        with transaction.atomic():
            for ligne in self.lignes_reception.filter(is_active=True).select_for_update():
                produit = Produit.objects.select_for_update().get(pk=ligne.produit_id)
                qte = produit.convertir_en_unite_base(ligne.quantite, ligne.unite_utilisee)
                produit.stock_actuel -= qte
                produit.save(update_fields=['stock_actuel'])

                ligne.is_active = False
                ligne.save(update_fields=['is_active'])

            self.total = 0
            self.montant_paye = 0
            self.reliquat_fournisseur = 0
            self.reliquat_magasin = 0
            self.is_active = False
            self.save(update_fields=['total', 'montant_paye', 'reliquat_fournisseur', 'reliquat_magasin', 'is_active'])


class LigneReception(models.Model):
    reception = models.ForeignKey('Reception', on_delete=models.CASCADE, related_name='lignes_reception')
    produit = models.ForeignKey("Produit", on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    unite_utilisee = models.ForeignKey("UniteDeMesure", on_delete=models.CASCADE)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, default=1000)
    is_active = models.BooleanField(default=True)

    @property
    def sous_total(self):
        return self.quantite * self.prix_unitaire

    def __str__(self):
        return f"{self.produit.nom} x {self.quantite} ({self.reception})"

    def clean(self):
        if self.quantite <= 0:
            raise ValidationError("La quantité doit être strictement positive.")

    def save(self, *args, **kwargs):
        self.clean()
        qte_new = self.produit.convertir_en_unite_base(self.quantite, self.unite_utilisee)

        if not qte_new or qte_new <= 0:
            raise ValidationError("Quantité ou unité invalide.")

        with transaction.atomic():
            if self.pk:  # Modification
                ancien = type(self).objects.select_for_update().get(pk=self.pk)
                if ancien.is_active:
                    produit_old = Produit.objects.select_for_update().get(pk=ancien.produit_id)
                    qte_old = produit_old.convertir_en_unite_base(ancien.quantite, ancien.unite_utilisee)
                    produit_old.stock_actuel -= qte_old
                    produit_old.save(update_fields=["stock_actuel"])

            super().save(*args, **kwargs)

            if self.is_active:
                produit_new = Produit.objects.select_for_update().get(pk=self.produit_id)
                produit_new.stock_actuel += qte_new
                produit_new.save(update_fields=["stock_actuel"])

                # Mise à jour du total de la réception
                self.reception.calculer_total()

    def soft_delete(self):
        """Annuler la ligne et restituer le stock sans la supprimer physiquement"""
        if self.is_active:
            with transaction.atomic():
                produit = Produit.objects.select_for_update().get(pk=self.produit_id)
                qte = produit.convertir_en_unite_base(self.quantite, self.unite_utilisee)
                produit.stock_actuel -= qte
                produit.save(update_fields=['stock_actuel'])

                self.is_active = False
                self.save(update_fields=['is_active'])

                self.reception.calculer_total()
