from fastapi import APIRouter, Depends, HTTPException
import uuid
from app.core.auth import get_current_user
from app.core.deps import get_workspace_member
from app.core.storage import get_presigned_upload_url, get_presigned_download_url
from app.models import User, WorkspaceMember

router = APIRouter(prefix="/workspaces/{workspace_id}/storage", tags=["storage"])

@router.get("/presigned-url")
async def get_presigned_url_endpoint(
    workspace_id: int,
    filename: str,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
):
    unique_id = str(uuid.uuid4())
    file_path = f"{workspace_id}/{unique_id}_{filename}"
    return get_presigned_upload_url("deliverables", file_path)

@router.get("/download-url")
async def get_download_url_endpoint(
    workspace_id: int,
    file_path: str,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
):
    """Generates a secure, time-limited URL to download a private file."""
    if not file_path.startswith(f"{workspace_id}/"):
        raise HTTPException(status_code=403, detail="Access denied to this file")
        
    url = get_presigned_download_url("deliverables", file_path, 3600)
    return {"url": url}