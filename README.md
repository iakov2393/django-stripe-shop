# Stripe Shop

Django + Stripe integration project.

## Endpoints
- `/item/<id>/` — item page with Buy button
- `/buy/<id>/` — create Stripe Checkout Session
- `/order/<id>/` — order page with PaymentIntent
- `/order/<id>/pay/` — create Stripe PaymentIntent
- `/order/<id>/buy/` — create Stripe Session for Order
- `/stripe/webhook/` — Stripe webhook handler
- `/success/` — success page
- `/cancel/` — cancel page

## Environment variables (.env)