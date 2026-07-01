from pydantic import BaseModel
from datetime import datetime
from app.models import UserRole

class WorkspaceCreate(BaseModel):
    name: str
    slug: str

class WorkspaceUpdate(BaseModel):
    name: str | None = None

class WorkspaceResponse(BaseModel):
    id: int
    name: str
    slug: str
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class WorkspaceMemberCreate(BaseModel):
    email: str
    role: UserRole

class WorkspaceMemberResponse(BaseModel):
    id: int
    workspace_id: int
    user_id: int
    role: UserRole
    joined_at: datetime
    user_email: str | None = None
    user_name: str | None = None

    model_config = {"from_attributes": True}