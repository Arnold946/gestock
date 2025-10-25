from rest_framework.routers import DefaultRouter

from .views import FournisseurViewSet, UniteDeMesureViewSet, CategorieViewSet, ProduitViewSet, ClientViewSet, \
    VenteViewSet, LigneVenteViewSet, EntreeStockViewSet, SortieStockViewSet, ReceptionViewSet, LigneReceptionViewSet, \
    ModePaiementViewSet

app_name = "stock"

router = DefaultRouter()

router.register(r"clients", ClientViewSet, basename="client")
router.register(r"fournisseurs", FournisseurViewSet, basename="fournisseur")
router.register(r"unites", UniteDeMesureViewSet, basename="unite")
router.register(r"modes-paiement", ModePaiementViewSet, basename="mode-paiement" )
router.register(r"categories", CategorieViewSet, basename="categorie")
router.register(r"produits", ProduitViewSet, basename="produit")
router.register(r"ventes", VenteViewSet, basename="vente")
router.register(r"ligne-ventes", LigneVenteViewSet, basename="ligne-vente")
router.register(r"entrees", EntreeStockViewSet, basename="entree-stock")
router.register(r"sorties", SortieStockViewSet, basename="sortie-stock")
router.register(r"receptions", ReceptionViewSet, basename="reception")
router.register(r"ligne-receptions", LigneReceptionViewSet, basename="ligne-reception")

urlpatterns = router.urls
