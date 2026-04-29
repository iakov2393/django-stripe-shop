# Create your tests here.
from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from .models import Item, Order, Discount, Tax, PaymentLog
import json


class TotalPriceTest(TestCase):
    def setUp(self):
        self.item1 = Item.objects.create(
            name="Item 1", description="desc", price=1000, currency="usd"
        )
        self.item2 = Item.objects.create(
            name="Item 2", description="desc", price=500, currency="usd"
        )
        self.order = Order.objects.create()
        self.order.items.set([self.item1, self.item2])

    def test_total_without_discount_tax(self):
        self.assertEqual(self.order.total_price(), 1500)

    def test_total_with_discount(self):
        discount = Discount.objects.create(name="10% off", percent=Decimal("10.00"))
        discount.orders.add(self.order)

        self.assertEqual(self.order.total_price(), 1350)

    def test_total_with_tax(self):
        tax = Tax.objects.create(name="VAT 20%", percent=Decimal("20.00"))
        tax.orders.add(self.order)

        self.assertEqual(self.order.total_price(), 1800)

    def test_total_discount_then_tax(self):
        discount = Discount.objects.create(name="10% off", percent=Decimal("10.00"))
        discount.orders.add(self.order)
        tax = Tax.objects.create(name="VAT 20%", percent=Decimal("20.00"))
        tax.orders.add(self.order)

        self.assertEqual(self.order.total_price(), 1620)

    def test_quantize_no_lost_cents(self):
        discount = Discount.objects.create(name="33.33% off", percent=Decimal("33.33"))
        order = Order.objects.create()
        order.items.set([self.item1])
        discount.orders.add(order)
        self.assertEqual(order.total_price(), 667)


class WebhookIdempotencyTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.item = Item.objects.create(
            name="Item", description="desc", price=1000, currency="usd"
        )
        self.order = Order.objects.create()
        self.order.items.add(self.item)

    def _make_event(self, event_id="evt_test123"):
        return {
            "id": event_id,
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_test123",
                    "metadata": {"order_id": str(self.order.id)},
                }
            },
        }

    @patch("stripe.Webhook.construct_event")
    def test_webhook_sets_is_paid(self, mock_construct):
        event_data = self._make_event()

        
        mock_event = MagicMock()
        mock_event.__getitem__ = lambda s, k: event_data[k]
        mock_event.to_dict = lambda: event_data

        mock_construct.return_value = mock_event

        response = self.client.post(
            "/stripe/webhook/",
            data=json.dumps(event_data),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="t=1,v1=test",
        )
        self.order.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.order.is_paid)

    @patch("stripe.Webhook.construct_event")
    def test_webhook_idempotent(self, mock_construct):
        event_data = self._make_event()

        mock_event = MagicMock()
        mock_event.__getitem__ = lambda s, k: event_data[k]
        mock_event.to_dict = lambda: event_data

        mock_construct.return_value = mock_event

        self.client.post(
            "/stripe/webhook/",
            data=json.dumps(event_data),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="t=1,v1=test",
        )
        self.client.post(
            "/stripe/webhook/",
            data=json.dumps(event_data),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="t=1,v1=test",
        )

        self.assertEqual(
            PaymentLog.objects.filter(stripe_event_id="evt_test123").count(), 1
        )
