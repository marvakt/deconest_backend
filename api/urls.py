from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserViewSet,
    ProductViewSet,
    WishlistViewSet,
    CartItemViewSet,
    OrderViewSet,
    RegisterView,   # CBV
    LoginView,      # CBV
    LogoutView,     # CBV
)

router = DefaultRouter()

# ViewSets
router.register(r'users', UserViewSet, basename='user')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'wishlist', WishlistViewSet, basename='wishlist')
router.register(r'cart', CartItemViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),

    # Auth endpoints (class-based views)
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # JWT Token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
