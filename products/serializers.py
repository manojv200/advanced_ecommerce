from rest_framework import serializers

from products.models import Product, Category, Cart, CartItem, Order


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ('created_at', 'updated_at')

    def create(self, validated_data):
        category, created = Category.objects.get_or_create(**validated_data)
        return category


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category',
                                                     write_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'stock', 'category_id', 'created_at', 'updated_at']
        read_only_fields = ('created_at', 'updated_at')

    def create(self, validated_data):
        product, created = Product.objects.get_or_create(**validated_data)
        return product


class CartItemSerializer(serializers.ModelSerializer):
    sub_total_price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CartItem
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def get_sub_total_price(self, obj):
        return obj.total_price


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(),
                                                    source='product',
                                                    write_only=True)
    product = ProductSerializer(read_only=True)
    quantity = serializers.IntegerField(write_only=True)
    total_price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'product_id', 'product', 'items', 'quantity', 'total_price', 'is_deleted', 'user', 'created_at',
                  'updated_at']
        read_only_fields = ('created_at', 'updated_at')

    def get_total_price(self, obj):
        return obj.total_price

    def create(self, validated_data):
        cart, created = Cart.objects.get_or_create(user=validated_data['user'])
        product = validated_data['product']
        if validated_data['quantity'] > product.stock:
            raise serializers.ValidationError('The product has not enough stock')
        if CartItem.objects.filter(product=validated_data['product'],
                                   cart__user__id=validated_data['user'].id).exists():
            cart_item = CartItem.objects.get(product=validated_data['product'],
                                             cart__user__id=validated_data['user'].id)
            cart_item.quantity += validated_data['quantity']
            cart_item.save()
            return cart
        cart_item = CartItem.objects.create(cart=cart, product=validated_data['product'],
                                            quantity=validated_data['quantity'])
        return cart


class OrderSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    total_price = serializers.FloatField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'product', 'total_price', 'user', 'created_at', 'updated_at']
        read_only_fields = ('created_at', 'updated_at')

    def create(self, validated_data):
        cart = Cart.objects.filter(user=validated_data['user']).first()
        for item in cart.items.all():
            order, created = Order.objects.get_or_create(user=validated_data['user'], product=item.product,
                                                         total_price=item.total_price)
            item.product.stock -= item.quantity
            item.product.save()
        return True


class OneOrderSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(read_only=True)
    total_price = serializers.FloatField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'product', 'total_price', 'user', 'quantity', 'created_at', 'updated_at']
        read_only_fields = ('created_at', 'updated_at')

    def create(self, validated_data):
        product = validated_data['product']
        quantity = int(validated_data['quantity'])
        order, created = Order.objects.get_or_create(user=validated_data['user'], product=product,
                                                     total_price=quantity * product.price)
        product.stock -= quantity
        product.save()
        return order
