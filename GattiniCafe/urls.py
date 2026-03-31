from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    RegisterView,
    MeView,
    CategoriaViewSet,
    ProdottoViewSet,
    OrdineViewSet,
)

router = DefaultRouter()
router.register(r'categorie', CategoriaViewSet, basename='categoria')
router.register(r'prodotti', ProdottoViewSet, basename='prodotto')
router.register(r'ordini', OrdineViewSet, basename='ordine')

urlpatterns = [
    # Auth --------------------------------------------------------
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='auth-login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='auth-token-refresh'),
    path('auth/me/', MeView.as_view(), name='auth-me'),

    # Menu + Ordini (via router) -------------------------------------------------------
    path('', include(router.urls)),
]
