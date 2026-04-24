import stripe
from django.conf import settings




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
    currency = order.items.first().currency
    secret_key = settings.STRIPE_KEYS.get(currency, {}).get("secret")

    # Создаём tax_rates ОДИН РАЗ для всего заказа
    tax_rate_ids = []
    for tax in order.taxes.all():
        stripe_tax = stripe.TaxRate.create(
            api_key=secret_key,
            display_name=tax.name,
            percentage=float(tax.percent),
            inclusive=False,
        )
        tax_rate_ids.append(stripe_tax.id)

    line_items = []
    for item in order.items.all():
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
            "tax_rates": tax_rate_ids,  # используем готовый список
        })

    stripe_discounts = []
    for discount in order.discounts.all():
        coupon = stripe.Coupon.create(
            api_key=secret_key,
            percent_off=float(discount.percent),
            duration="once",
        )
        stripe_discounts.append({"coupon": coupon.id})

    session = stripe.checkout.Session.create(
        api_key=secret_key,
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
    currency = order.items.first().currency
    secret_key = settings.STRIPE_KEYS.get(currency, {}).get("secret")
    amount = order.total_price()

    intent = stripe.PaymentIntent.create(
        api_key=secret_key,  
        amount=amount,
        currency=currency,
        metadata={"order_id": str(order.id)}
    )
    return intent