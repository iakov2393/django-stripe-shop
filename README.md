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
```
SECRET_KEY=your-django-secret-key
DEBUG=False
DATABASE_URL=postgresql://...
BASE_URL=https://your-app.railway.app
ALLOWED_HOSTS=your-app.railway.app
STRIPE_SECRET_KEY_USD=sk_test_...
STRIPE_PUBLISHABLE_KEY_USD=pk_test_...
STRIPE_SECRET_KEY_EUR=sk_test_...
STRIPE_PUBLISHABLE_KEY_EUR=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

## Run with Docker
```bash
docker-compose up --build
```

## Run locally
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Live Demo
URL: https://django-stripe-shop-production-7231.up.railway.app

## Admin credentials
URL: https://django-stripe-shop-production-7231.up.railway.app/admin/
Login: admin
Password: admin123

## Test card (Stripe)
Number: 4242 4242 4242 4242
Date: 12/34
CVC: 123