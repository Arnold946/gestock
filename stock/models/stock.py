from django.conf import settings
from django.db import models, transaction
from django.core.exceptions import ValidationError

from stock.models import Produit


class MouvementStock(models.Model):
    produit = models.ForeignKey("Produit", on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    unite_utilisee = models.ForeignKey("UniteDeMesure", on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_crees'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_modifiees'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def quantite_en_unite_base(self):
        return self.produit.convertir_en_unite_base(self.quantite, self.unite_utilisee)

    def delete(self, using=None, keep_parents=False):
        """Soft delete = désactivation + restitution du stock"""
        if not self.is_active:
            return  # déjà supprimé logiquement

        qte = self.quantite_en_unite_base()
        with transaction.atomic():
            prod = Produit.objects.select_for_update().get(pk=self.produit_id)

            # 🔹 Annuler l’impact de ce mouvement
            if isinstance(self, EntreeStock):
                prod.stock_actuel -= qte
            elif isinstance(self, SortieStock):
                prod.stock_actuel += qte

            prod.save(update_fields=["stock_actuel"])

            # Marquer comme inactif
            self.is_active = False
            self.save(update_fields=["is_active"])


class EntreeStock(MouvementStock):
    ENTREE_CHOICES = [
        ('achat', 'Achat'),
        ('retour_client', 'Retour client'),
        ('correction', 'Correction inventaire'),
        ('don_recu', 'Don reçu'),
        ('autre', 'Autre'),
    ]

    type_entree = models.CharField(max_length=20, choices=ENTREE_CHOICES, default='autre')
    fournisseur = models.ForeignKey('Fournisseur', on_delete=models.SET_NULL, null=True, blank=True)

    def clean(self):
        if self.type_entree == 'achat' and self.fournisseur is None:
            raise ValidationError("Un fournisseur est requis pour une entrée de type 'achat'.")

    def save(self, *args, **kwargs):
        self.clean()

        with transaction.atomic():
            if self.pk:
                ancien = type(self).objects.select_for_update().get(pk=self.pk)
                prod_old = Produit.objects.select_for_update().get(pk=ancien.produit_id)
                qte_old = ancien.quantite_en_unite_base()

                prod_old.stock_actuel -= qte_old
                prod_old.save(update_fields=['stock_actuel'])

            prod_new = Produit.objects.select_for_update().get(pk=self.produit_id)
            qte_new = self.quantite_en_unite_base()

            if qte_new<=0:
                raise ValidationError("La quantité doit être un nombre positif.")

            super().save()

            prod_new.stock_actuel += qte_new
            prod_new.save(update_fields=['stock_actuel'])



class SortieStock(MouvementStock):
    SORTIE_CHOICES = [
        ('don', 'Don'),
        ('perte', 'Perte'),
        ('usage_interne', 'Usage interne'),
        ('autre', 'Autre'),
    ]

    type_sortie = models.CharField(max_length=20, choices=SORTIE_CHOICES, default='autre')
    client = models.ForeignKey('Client', on_delete=models.SET_NULL, null=True, blank=True)

    def clean(self):
        if self.client and self.type_sortie == 'autre':
            raise ValidationError("Utilisez le module Vente pour enregistrer une sortie client.")

    def save(self, *args, **kwargs):
        self.clean()

        with transaction.atomic():
            if self.pk:
                ancien = type(self).objects.select_for_update().get(pk=self.pk)
                prod_old = Produit.objects.select_for_update().get(pk=ancien.produit_id)
                qte_old = ancien.quantite_en_unite_base()

                prod_old.stock_actuel += qte_old
                prod_old.save(update_fields=['stock_actuel'])

            prod_new = Produit.objects.select_for_update().get(pk=self.produit_id)
            qte_new = self.quantite_en_unite_base()

            if qte_new<=0:
                raise ValidationError("Quantité invalide !")
            if prod_new.stock_actuel<qte_new:
                raise ValidationError("Stock insuffisant pour cette sortie !")

            super().save(*args, **kwargs)

            prod_new.stock_actuel -= qte_new
            prod_new.save(update_fields=['stock_actuel'])
