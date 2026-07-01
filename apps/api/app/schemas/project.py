from pydantic import BaseModel
from datetime import datetime
from app.models import ProjectStatus

class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    client_id: int | None = None
    status: ProjectStatus = ProjectStatus.ACTIVE

class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    client_id: int | None = None
    status: ProjectStatus | None = None

class ProjectResponse(BaseModel):
    id: int
    workspace_id: int
    client_id: int | None
    name: str
    description: str | None
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}