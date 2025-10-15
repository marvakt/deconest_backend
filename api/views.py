from rest_framework import viewsets, status, permissions, mixins, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Q

from .models import User, Profile, Product, Wishlist, CartItem, Order, OrderItem
from .serializers import (
    UserSerializer,
    ProductSerializer,
    WishlistSerializer,
    CartItemSerializer,
    OrderSerializer,
)

# -----------------------------
# JWT TOKEN HELPER
# -----------------------------
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# -----------------------------
# REGISTER CBV
# -----------------------------
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            Profile.objects.get_or_create(user=user)
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# -----------------------------
# LOGIN CBV
# -----------------------------
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user:
            if getattr(user, 'is_blocked', False):
                return Response({'error': 'User is blocked'}, status=status.HTTP_403_FORBIDDEN)

            Profile.objects.get_or_create(user=user)

            tokens = get_tokens_for_user(user)
            user_data = UserSerializer(user).data
            return Response({
                'message': 'Login successful',
                'tokens': tokens,
                'user': user_data
            }, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# -----------------------------
# LOGOUT CBV
# -----------------------------
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

# -----------------------------
# USER VIEWSET (Admin Only)
# -----------------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

# -----------------------------
# PRODUCT VIEWSET
# -----------------------------
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.filter(is_archived=False)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(room__icontains=search)
            )
        return queryset

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [perm() for perm in permission_classes]

# -----------------------------
# WISHLIST VIEWSET
# -----------------------------
class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# -----------------------------
# CART VIEWSET
# -----------------------------
class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# -----------------------------
# ORDER VIEWSET (Auto-create items from cart)
# -----------------------------
class OrderViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or getattr(user, 'role', None) == 'admin':
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        cart_items = CartItem.objects.filter(user=self.request.user)
        if not cart_items.exists():
            raise serializers.ValidationError("Cart is empty.")

        total = sum(item.product.price * item.quantity for item in cart_items)
        order = serializer.save(user=self.request.user, total=total)

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )

        cart_items.delete()
