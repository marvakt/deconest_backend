from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserViewSet,
    ProductViewSet,
    WishlistViewSet,
    CartItemViewSet,
    OrderViewSet,
    register,
    login_view,
    logout_view,
)

router = DefaultRouter()

# ✅ Add basename arguments where queryset isn’t defined inside ViewSet
router.register(r'users', UserViewSet, basename='user')
router.register(r'products', ProductViewSet, basename='product')  # important fix
router.register(r'wishlist', WishlistViewSet, basename='wishlist')
router.register(r'cart', CartItemViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),

    # Auth endpoints
    path('register/', register),
    path('login/', login_view),
    path('logout/', logout_view),

    # JWT Token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
