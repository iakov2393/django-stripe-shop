from django.contrib import admin
from .models import Item, Order, PaymentLog


# Register your models here.
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "currency")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at")
    filter_horizontal = ("items",)


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = ("id", "event_type", "stripe_event_id", "created_at")
    readonly_fields = ("event_type", "stripe_event_id", "payload", "created_at")
