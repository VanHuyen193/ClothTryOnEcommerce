from django.urls import path
from . import views as view

urlpatterns = [
    path('', view.cart, name='cart'),
    path('add/<int:product_id>/', view.add_cart, name='add_cart'),
    path('remove_cart/<int:product_id>/<int:cart_item_id>/', view.remove_cart, name='remove_cart'),
    path('remove_cart_item/<int:product_id>/<int:cart_item_id>/', view.remove_cart_item, name='remove_cart_item'),
    path('checkout/', view.checkout, name='checkout'),
]
