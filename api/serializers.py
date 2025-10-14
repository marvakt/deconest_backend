from rest_framework import serializers
from .models import User, Product, Wishlist, CartItem, Order, OrderItem

# -------------------------
# 1️⃣ USER SERIALIZER
# -------------------------
class UserSerializer(serializers.ModelSerializer):
    # Include password field for write-only access
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_blocked', 'password']

    # Override create to hash password properly
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # ✅ hash the password
        user.save()
        return user

    # Optional: override update if you allow password change
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


# -------------------------
# 2️⃣ PRODUCT SERIALIZER
# -------------------------
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


# -------------------------
# 3️⃣ WISHLIST SERIALIZER
# -------------------------
class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'product', 'product_id']


# -------------------------
# 4️⃣ CART SERIALIZER
# -------------------------
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id', 'user', 'product', 'product_id', 'quantity']


# -------------------------
# 5️⃣ ORDER SERIALIZER
# -------------------------
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'total', 'address', 'payment_method', 'status', 'date', 'items']
