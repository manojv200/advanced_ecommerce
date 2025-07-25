from django.urls import path

from . import views

urlpatterns = [
    path('categories/', views.CategoryCreateListView.as_view(), name='categories'),
    path('categories/<int:pk>/', views.CategoryUpdateDeleteView.as_view(), name='category'),
    path('products/', views.ProductCreateListView.as_view(), name='products'),
    path('products/<int:pk>/', views.ProductUpdateDeleteView.as_view(), name='product'),

    path('cart/', views.CartCreateListView.as_view(), name='cart'),
    path('orders/', views.CheckOutApiView.as_view(), name='orders'),
    path('orders/<int:pk>/', views.CheckOutApiView.as_view(), name='order'),

    path('order/', views.OrderApiView.as_view(), name='order'),

    path('order_update/<int:pk>/', views.UpdateOrderStatusView.as_view(), name='order-update'),
]
