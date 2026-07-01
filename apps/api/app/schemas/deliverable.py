from pydantic import BaseModel
from datetime import datetime
from app.models import DeliverableStatus

class DeliverableCreate(BaseModel):
    file_name: str
    file_type: str
    file_size: int
    storage_path: str

class DeliverableStatusUpdate(BaseModel):
    status: DeliverableStatus

class DeliverableResponse(BaseModel):
    id: int
    milestone_id: int
    version: int
    file_name: str
    file_type: str
    file_size: int
    storage_path: str
    status: DeliverableStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}