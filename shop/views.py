import stripe
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from .models import Item, Order, PaymentLog
from .services import create_checkout_session, create_checkout_session_for_order


# Create your views here.
def item_page(request, id):
    item = get_object_or_404(Item, id=id)

    return render(
        request,
        "item.html",
        {
            "item": item,
            "stripe_public_key": settings.STRIPE_PUBLISHABLE_KEY,
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

    return render(
        request,
        "order.html",
        {
            "order": order,
            "stripe_public_key": settings.STRIPE_PUBLISHABLE_KEY,
        },
    )

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return HttpResponse(status=400)

    PaymentLog.objects.create(
        order_id=None,
        event_type=event["type"],
        stripe_event_id=event["id"],
        payload=event.to_dict()   
    )

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        session_id = session.get("id")
        order_id = session.get("metadata", {}).get("order_id")

        if not order_id:
            return HttpResponse(status=200)

        try:
            order = Order.objects.get(id=int(order_id))

            if order.is_paid:
                return HttpResponse(status=200)

            if order.stripe_session_id == session_id:
                return HttpResponse(status=200)

            order.is_paid = True
            order.stripe_session_id = session_id
            order.save()

        except Order.DoesNotExist:
            print("ORDER NOT FOUND", order_id)

    return HttpResponse(status=200)
