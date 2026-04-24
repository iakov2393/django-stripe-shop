import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(item):
    secret_key = settings.STRIPE_KEYS.get(item.currency, {}).get("secret")
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            api_key=secret_key,
            line_items=[
                {
                    "price_data": {
                        "currency": item.currency,
                        "product_data": {
                            "name": item.name,
                            "description": item.description,
                        },
                        "unit_amount": item.price,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=f"{settings.BASE_URL}/success/",
            cancel_url=f"{settings.BASE_URL}/cancel/",
        )
        return session
    except Exception as e:
        print("Stripe Error:", repr(e))
        raise


def create_checkout_session_for_order(order):
    line_items = []

    for item in order.items.all():
        tax_rates = []
        for tax in order.taxes.all():
            stripe_tax = stripe.TaxRate.create(
                display_name=tax.name,
                percentage=float(tax.percent),
                inclusive=False,
            )
            tax_rates.append(stripe_tax.id)

        line_items.append({
            "price_data": {
                "currency": item.currency,
                "product_data": {
                    "name": item.name,
                    "description": item.description,
                },
                "unit_amount": item.price,
            },
            "quantity": 1,
            "tax_rates": tax_rates,  
        })

    stripe_discounts = []
    for discount in order.discounts.all():
        coupon = stripe.Coupon.create(
            percent_off=float(discount.percent),
            duration="once",
        )
        stripe_discounts.append({"coupon": coupon.id})

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        mode="payment",
        success_url=f"{settings.BASE_URL}/success/",
        cancel_url=f"{settings.BASE_URL}/cancel/",
        discounts=stripe_discounts if stripe_discounts else [],
        metadata={"order_id": str(order.id)},
        client_reference_id=str(order.id),
    )

    return session

def create_payment_intent_for_order(order):
    amount = order.total_price()

    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency=order.items.first().currency,
        metadata={
            "order_id": str(order.id)
        }
    )

    return intent