# Stripe Shop

Simple Django project with Stripe integration.

## Features
- Item model (name, description, price)
- Stripe Checkout Session
- Payment success page

## Endpoints
- /item/<id>/ - item page
- /buy/<id>/ - create Stripe session
- /success/ - success page
- /cancel/ - cancel page

## Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
