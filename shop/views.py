import stripe
import logging
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from .models import Item, Order, PaymentLog
from .services import (
    create_checkout_session,
    create_checkout_session_for_order,
    create_payment_intent_for_order,
)


logger = logging.getLogger(__name__)


# Create your views here.
def item_page(request, id):
    item = get_object_or_404(Item, id=id)
    publishable_key = settings.STRIPE_KEYS.get(item.currency, {}).get("publishable")

    return render(
        request,
        "item.html",
        {
            "item": item,
            "stripe_public_key": publishable_key,
        },
    )


def buy_item(request, id):
    item = get_object_or_404(Item, id=id)

    try:
        session = create_checkout_session(item)
        return JsonResponse({"id": session.id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def buy_order(request, id):
    order = get_object_or_404(Order, id=id)

    try:
        session = create_checkout_session_for_order(order)
        return JsonResponse({"id": session.id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def success(request):
    return HttpResponse("Payment SUCCESS")


def cancel(request):
    return HttpResponse("Payment CANCELLED")


def order_page(request, id):
    order = get_object_or_404(Order, id=id)
    publishable_key = settings.STRIPE_KEYS.get(order.items.first().currency, {}).get(
        "publishable"
    )
    return render(
        request,
        "order.html",
        {
            "order": order,
            "stripe_public_key": publishable_key,
        },
    )


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    except ValueError:
        return HttpResponse(status=400)

    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        order_id = intent["metadata"].get("order_id") if intent["metadata"] else None

        order = Order.objects.filter(id=order_id).first() if order_id else None

        log, created = PaymentLog.objects.get_or_create(
            stripe_event_id=event["id"],
            defaults={
                "event_type": event["type"],
                "payload": event.to_dict(),
                "order": order,
            },
        )
        if not created:
            return HttpResponse(status=200)

        if order:
            updated = Order.objects.filter(id=order_id, is_paid=False).update(
                is_paid=True,
                stripe_payment_intent_id=intent["id"],
            )

    else:
        PaymentLog.objects.get_or_create(
            stripe_event_id=event["id"],
            defaults={
                "event_type": event["type"],
                "payload": event.to_dict(),
                "order": None,
            },
        )

    return HttpResponse(status=200)


def pay_order(request, id):
    order = get_object_or_404(Order, id=id)

    intent = create_payment_intent_for_order(order)

    return JsonResponse({"clientSecret": intent.client_secret})
