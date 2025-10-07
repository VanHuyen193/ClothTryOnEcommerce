from django.urls import path
from . import views as view

urlpatterns = [
    path('', view.cart, name='cart'),
    path('add/<int:product_id>/', view.add_cart, name='add_cart'),
]
