from pydantic import BaseModel
from datetime import datetime, date
from app.models import MilestoneStatus
from app.schemas.invoice import InvoiceResponse

class MilestoneCreate(BaseModel):
    name: str
    description: str | None = None
    due_date: date | None = None
    amount: float = 0.0

class MilestoneUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    due_date: date | None = None
    amount: float | None = None
    status: MilestoneStatus | None = None

class MilestoneResponse(BaseModel):
    id: int
    project_id: int
    name: str
    description: str | None
    due_date: date | None
    amount: float
    status: MilestoneStatus
    created_at: datetime
    updated_at: datetime
    invoice: InvoiceResponse | None = None # NEW

    model_config = {"from_attributes": True}