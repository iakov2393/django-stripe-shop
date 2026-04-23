from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.conf import settings

from .models import Item, Order
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