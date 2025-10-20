from rest_framework import serializers
from .models import User, Product, Wishlist, CartItem, Order, OrderItem




class TimestampSerializerMixin(serializers.ModelSerializer):
    """For models with created/updated timestamps."""
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        abstract = True


class UserReferenceMixin(serializers.ModelSerializer):
    """Automatically assign logged-in user on create."""
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)





class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_blocked', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance




class ProductSerializer(TimestampSerializerMixin):
    class Meta:
        model = Product
        fields = '__all__'




class WishlistSerializer(UserReferenceMixin, serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'product', 'product_id']
        read_only_fields = ['user']

    def validate(self, data):
        """Prevent duplicate wishlist entries."""
        user = self.context['request'].user
        product = data['product']
        if Wishlist.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError("This product is already in your wishlist.")
        return data



class CartItemSerializer(UserReferenceMixin, serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id', 'user', 'product', 'product_id', 'quantity']
        read_only_fields = ['user']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity']



class OrderSerializer(UserReferenceMixin, serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)  # read-only

    class Meta:
        model = Order
        fields = ['id', 'user', 'total', 'address', 'payment_method', 'status', 'date', 'items']
        read_only_fields = ['user', 'status', 'date', 'total']

