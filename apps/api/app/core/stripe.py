import stripe
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def get_or_create_customer(email: str, name: str) -> str:
    """Finds an existing Stripe customer by email or creates a new one."""
    customers = stripe.Customer.list(email=email, limit=1)
    if customers.data:
        return customers.data[0].id
    customer = stripe.Customer.create(email=email, name=name)
    return customer.id

def create_stripe_invoice(customer_id: str, amount: float, description: str) -> dict:
    """Creates a Stripe Invoice Item and finalizes the Invoice."""
    amount_cents = int(amount * 100)
    
    stripe.InvoiceItem.create(
        customer=customer_id,
        amount=amount_cents,
        currency="usd",
        description=description
    )
    
    invoice = stripe.Invoice.create(
        customer=customer_id,
        auto_advance=True, # Automatically moves from Draft to Open (Sent)
    )
    
    return {
        "id": invoice.id,
        "hosted_invoice_url": invoice.hosted_invoice_url
    }

def verify_webhook_signature(payload: bytes, sig_header: str) -> dict:
    """Verifies the Stripe webhook signature for security."""
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        return event
    except ValueError:
        raise ValueError("Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise ValueError("Invalid signature")