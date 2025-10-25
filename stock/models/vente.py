from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.core.exceptions import ValidationError

from stock.models import Produit


class Vente(models.Model):
    client = models.ForeignKey('Client', on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    mode_paiement = models.ForeignKey('ModePaiement', on_delete=models.SET_NULL, null=True, blank=True)

    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    montant_paye = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    reliquat_client = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    reliquat_magasin = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    remarque = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    # 🔹 Ajout de la traçabilité
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ventes_creees'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ventes_modifiees'
    )

    def __str__(self):
        client_name = str(self.client) if self.client else "Sans client"
        return f"Vente #{self.id} - {client_name} - {self.date.strftime('%Y-%m-%d %H:%M')}"

    def calculer_total(self):
        """Recalcule le total de la vente à partir des lignes."""
        self.total = sum(l.sous_total for l in self.lignes.all())
        self.save(update_fields=['total'])

    def calculer_reliquat(self):
        """Calcule le reliquat côté client et côté magasin."""
        if self.montant_paye < self.total:
            self.reliquat_client = self.total - self.montant_paye
            self.reliquat_magasin = 0
        elif self.montant_paye > self.total:
            self.reliquat_client = 0
            self.reliquat_magasin = self.montant_paye - self.total
        else:
            self.reliquat_client = 0
            self.reliquat_magasin = 0
        self.save(update_fields=['reliquat_client', 'reliquat_magasin'])


    def soft_delete(self):
        """
        Annuler une vente complète :
        - Restitue le stock de toutes les lignes actives
        - Désactive les lignes
        - Met les montants de la vente à zéro
        """
        with transaction.atomic():
            for ligne in self.lignes.filter(is_active=True).select_for_update():
                produit = Produit.objects.select_for_update().get(pk=ligne.produit_id)
                qte = produit.convertir_en_unite_base(ligne.quantite, ligne.unite_utilisee)
                produit.stock_actuel += qte
                produit.save(update_fields=['stock_actuel'])

                ligne.is_active = False
                ligne.save(update_fields=['is_active'])

            # Réinitialiser les montants
            self.total = 0
            self.montant_paye = 0
            self.reliquat_client = 0
            self.reliquat_magasin = 0
            self.save(update_fields=['total', 'montant_paye', 'reliquat_client', 'reliquat_magasin'])


class LigneVente(models.Model):
    vente = models.ForeignKey('Vente', on_delete=models.CASCADE, related_name="lignes")
    produit = models.ForeignKey("Produit", on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unite_utilisee = models.ForeignKey('UniteDeMesure', on_delete=models.CASCADE)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    @property
    def sous_total(self):
        return self.quantite * self.prix_unitaire

    def save(self, *args, **kwargs):
        """
        Logique métier robuste :
        - Si modification : restituer le stock de l’ancienne ligne
        - Vérifier stock suffisant AVANT insertion
        - Décrémenter le stock seulement après validation
        - Recalculer le total de la vente
        """
        with transaction.atomic():

            # 1) Si modification → restituer l’ancien stock
            if self.pk:
                ancien = type(self).objects.select_for_update().get(pk=self.pk)
                produit_old = Produit.objects.select_for_update().get(pk=ancien.produit_id)
                qte_old = produit_old.convertir_en_unite_base(ancien.quantite, ancien.unite_utilisee)
                produit_old.stock_actuel += qte_old
                produit_old.save(update_fields=['stock_actuel'])

            # 2) Vérifier la nouvelle quantité AVANT de sauver
            produit_new = Produit.objects.select_for_update().get(pk=self.produit_id)
            qte_new = produit_new.convertir_en_unite_base(self.quantite, self.unite_utilisee)

            if not qte_new or qte_new <= 0:
                raise ValidationError("Quantité ou unité invalide")
            if produit_new.stock_actuel < qte_new:
                raise ValidationError("Stock insuffisant pour ce produit")

            # 3) Sauvegarde de la ligne (si tout est OK)
            super().save(*args, **kwargs)

            # 4) Mise à jour du stock
            produit_new.stock_actuel -= qte_new
            produit_new.save(update_fields=["stock_actuel"])

            # 5) Recalcul du total de la vente
            self.vente.calculer_total()

    def soft_delete(self):
        """Annuler la ligne et restituer le stock sans la supprimer physiquement"""
        if self.is_active:
            with transaction.atomic():
                produit = Produit.objects.select_for_update().get(pk=self.produit_id)
                qte = produit.convertir_en_unite_base(self.quantite, self.unite_utilisee)
                produit.stock_actuel += qte
                produit.save(update_fields=['stock_actuel'])

                self.is_active = False
                self.save(update_fields=['is_active'])
                self.vente.calculer_total()
