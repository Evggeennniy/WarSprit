from django.urls import path

from .views import BasketView, IndexView, ProductDetailsView, basket, order_submit

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path('user/basket/', BasketView.as_view(), name='basket'),
    path(
        "product/<int:pk>/", ProductDetailsView.as_view(), name="product"
    ),
    path("basket/", basket, name="basket-calc"),
    path("submit-order/", order_submit, name="order_submit"),
]
