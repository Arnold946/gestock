from rest_framework.routers import DefaultRouter

from users.views import InterfaceViewSet, RoleViewSet, UserViewSet

app_name = "users"

router = DefaultRouter()

router.register(r'interfaces', InterfaceViewSet, basename='interface')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = router.urls