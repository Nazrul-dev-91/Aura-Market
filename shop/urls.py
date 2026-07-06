from django.urls import path
from . import views

urlpatterns = [
    # HTML View Routes
    path('', views.catalog_view, name='catalog'),
    path('track/', views.track_view, name='track'),
    path('seller/', views.seller_view, name='seller'),

    # JSON API Endpoints
    path('api/products/', views.api_products_list, name='api_products_list'),
    path('api/checkout/', views.api_checkout, name='api_checkout'),
    path('api/orders/track/<str:tracking_number>/', views.api_track_order, name='api_track_order'),
    path('api/seller/product/<int:product_id>/stock/', views.api_seller_update_stock, name='api_seller_update_stock'),
    path('api/seller/order/<int:order_id>/status/', views.api_seller_update_order_status, name='api_seller_update_order_status'),
    path('api/seller/product/add/', views.api_seller_add_product, name='api_seller_add_product'),
]
