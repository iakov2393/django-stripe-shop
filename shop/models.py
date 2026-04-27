from decimal import Decimal
from django.db import models

CURRENCY_CHOICES = [
    ("usd", "USD"),
    ("eur", "EUR"),
]


# Create your models here.
class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.IntegerField()
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="usd")

    def __str__(self):
        return self.name


class Order(models.Model):
    items = models.ManyToManyField(Item)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    stripe_payment_intent_id = models.CharField(
        max_length=255, blank=True, null=True, unique=True
    )

    def total_price(self):
        total = Decimal(sum(item.price for item in self.items.all()))

        for discount in self.discounts.all().order_by("id"):
            total = discount.apply(total)

        for tax in self.taxes.all().order_by("id"):
            total = tax.apply(total)

        return int(total)


class PaymentLog(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    event_type = models.CharField(max_length=255)
    stripe_event_id = models.CharField(max_length=255, unique=True)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


class Discount(models.Model):
    name = models.CharField(max_length=255)
    percent = models.DecimalField(
        max_digits=5, decimal_places=2
    )  # например 10.00 = 10%
    orders = models.ManyToManyField("Order", related_name="discounts", blank=True)

    def __str__(self):
        return f"{self.name} ({self.percent}%)"

    def apply(self, total):
        return total - (total * (self.percent / Decimal("100")))


class Tax(models.Model):
    name = models.CharField(max_length=255)
    percent = models.DecimalField(
        max_digits=5, decimal_places=2
    )  # например 20.00 = 20%

    orders = models.ManyToManyField("Order", related_name="taxes", blank=True)

    def __str__(self):
        return f"{self.name} ({self.percent}%)"

    def apply(self, total):
        return total + (total * self.percent / Decimal("100"))
