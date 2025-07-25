from urllib.parse import urlencode

from django.core.cache import cache
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from products.filters import ProductFilter
from products.models import Product, Category, Cart, Order
from products.serializers import ProductSerializer, CategorySerializer, CartSerializer, CartItemSerializer, \
    OrderSerializer, OneOrderSerializer


# Create your views here.
status_fields = {
    Order.pending :'pending',
    Order.shipped :'shipped',
    Order.delivered :'delivered',
    Order.canceled :'Canceled',
}
class CategoryCreateListView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to add products. Only admins can perform this action.")
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        query_string = urlencode(request.GET)
        cache_key = f"category_list:{query_string if query_string else 'all'}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        cache.set(cache_key, serializer.data, timeout=3600)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        category = get_object_or_404(Category, pk=pk)
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(category, request)
        serializer = CategorySerializer(page, many=False)
        return paginator.get_paginated_response(serializer.data)

    def put(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(instance=category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return Response({'detail': 'Category deleted'}, status=status.HTTP_204_NO_CONTENT)


class ProductCreateListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        query_string = urlencode(request.GET)
        cache_key = f"product_list:{query_string if query_string else 'all'}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)
        products = Product.objects.select_related('category').all()
        filtered_qs = ProductFilter(request.GET, queryset=products).qs
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(filtered_qs, request)
        serializer = ProductSerializer(page, many=True)
        response= paginator.get_paginated_response(serializer.data)
        cache.set(cache_key, response.data, timeout=3600)
        return response

    def post(self, request):
        if not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to add products. Only admins can perform this action.")
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @classmethod
    def get(cls, request, pk=None):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk=None):
        if not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to add products. Only admins can perform this action.")
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        if not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to add products. Only admins can perform this action.")
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return Response({'detail': 'Product deleted'}, status=status.HTTP_204_NO_CONTENT)


class CartCreateListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        carts = Cart.objects.prefetch_related('items').all()
        serializer = CartSerializer(carts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = CartSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CheckOutApiView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = OrderSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            cart = Cart.objects.get(user=request.user)
            cart.is_deleted = True
            cart.save()
            return Response({'detail':'Ordered items Successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        if pk:
            order = Order.objects.filter(pk=pk).select_related('product').first()
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        orders = Order.objects.select_related('product').all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class OrderApiView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        quantity = int(data['quantity'])
        product = get_object_or_404(Product, pk=data['product'])
        if quantity > product.stock:
            return Response({'detail': 'Not enough stock for this product'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = OneOrderSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'data':serializer.data, 'detail':'Ordered Successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateOrderStatusView(APIView):
    def patch(self, request, pk=None):
        order = get_object_or_404(Order, pk=pk)
        order.status = request.data.get('status')
        order.save()
        return Response({"message": f"Order status changed to {status_fields[int(order.status)]}."}, status=status.HTTP_200_OK)
