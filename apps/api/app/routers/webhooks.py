from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.core.database import get_db
from app.core.stripe import verify_webhook_signature
from app.models import Invoice, InvoiceStatus

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = verify_webhook_signature(payload, sig_header)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    event_type = event["type"]
    
    if event_type in ["invoice.paid", "invoice.payment_failed"]:
        invoice_data = event["data"]["object"]
        stripe_id = invoice_data["id"]
        
        result = await db.execute(select(Invoice).where(Invoice.stripe_invoice_id == stripe_id))
        invoice = result.scalar_one_or_none()
        
        if invoice:
            if event_type == "invoice.paid":
                invoice.status = InvoiceStatus.PAID
                invoice.paid_at = datetime.utcnow()
            elif event_type == "invoice.payment_failed":
                invoice.status = InvoiceStatus.OVERDUE
                
            await db.commit()
            
    return {"received": True}