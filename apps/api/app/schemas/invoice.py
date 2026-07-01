from pydantic import BaseModel
from datetime import datetime
from app.models import InvoiceStatus

class InvoiceResponse(BaseModel):
    id: int
    milestone_id: int
    stripe_invoice_id: str | None
    amount: float
    status: InvoiceStatus
    issued_at: datetime
    due_at: datetime | None
    paid_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}