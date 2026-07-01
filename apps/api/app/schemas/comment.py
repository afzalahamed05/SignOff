from pydantic import BaseModel
from datetime import datetime

class CommentCreate(BaseModel):
    content: str
    x_coord: float | None = None
    y_coord: float | None = None
    parent_id: int | None = None

class CommentUpdate(BaseModel):
    content: str

class CommentResponse(BaseModel):
    id: int
    deliverable_id: int
    user_id: int
    content: str
    x_coord: float | None
    y_coord: float | None
    parent_id: int | None
    created_at: datetime
    updated_at: datetime
    user_name: str | None = None
    user_avatar: str | None = None
    replies: list["CommentResponse"] = []

    model_config = {"from_attributes": True}

# Required for Pydantic v2 to handle recursive self-referencing models
CommentResponse.model_rebuild()