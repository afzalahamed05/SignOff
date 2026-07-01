from pydantic import BaseModel
from datetime import datetime

class ClientCreate(BaseModel):
    name: str
    email: str
    company: str | None = None

class ClientUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    company: str | None = None

class ClientResponse(BaseModel):
    id: int
    workspace_id: int
    name: str
    email: str
    company: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}