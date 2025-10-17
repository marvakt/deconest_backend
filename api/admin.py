from django.contrib import admin
from .models import User, Profile, Product, Wishlist, CartItem, Order, OrderItem

# -------------------------------
# 1️⃣ USER & PROFILE
# -------------------------------
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_blocked', 'is_staff', 'is_active')
    list_filter = ('role', 'is_blocked', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'address')
    search_fields = ('user__username', 'phone')


# -------------------------------
# 2️⃣ PRODUCT
# -------------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'room', 'stock', 'is_archived', 'created_at')
    list_filter = ('room', 'is_archived', 'created_at')
    search_fields = ('title', 'room')
    ordering = ('-created_at',)
    list_editable = ('price', 'stock', 'is_archived')


# -------------------------------
# 3️⃣ WISHLIST
# -------------------------------
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')
    search_fields = ('user__username', 'product__title')


# -------------------------------
# 4️⃣ CART ITEMS
# -------------------------------
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')
    search_fields = ('user__username', 'product__title')


# -------------------------------
# 5️⃣ ORDERS
# -------------------------------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total', 'status', 'payment_method', 'date')
    list_filter = ('status', 'payment_method', 'date')
    search_fields = ('user__username', 'id')
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity')
    search_fields = ('order__id', 'product__title')
