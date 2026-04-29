from django.urls import path
from . import views

urlpatterns = [
    path("item/<int:id>/", views.item_page, name="item_page"),
    path("buy/<int:id>/", views.buy_item, name="buy_item"),
    path("order/<int:id>/buy/", views.buy_order, name="buy_order"),
    path("success/", views.success, name="success"),
    path("cancel/", views.cancel, name="cancel"),
    path("order/<int:id>/", views.order_page, name="order_page"),
    path("stripe/webhook/", views.stripe_webhook, name="stripe_webhook"),
    path("order/<int:id>/pay/", views.pay_order, name="pay_order"),
]
