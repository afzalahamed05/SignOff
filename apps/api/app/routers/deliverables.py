from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.deps import get_workspace_member
from app.core.websocket import manager
from app.models import User, WorkspaceMember, Project, Milestone, Deliverable, UserRole, DeliverableStatus
from app.schemas.deliverable import DeliverableCreate, DeliverableStatusUpdate, DeliverableResponse

router = APIRouter(prefix="/workspaces/{workspace_id}/projects/{project_id}/milestones/{milestone_id}/deliverables", tags=["deliverables"])

async def verify_milestone_in_workspace(workspace_id: int, project_id: int, milestone_id: int, db: AsyncSession):
    result = await db.execute(
        select(Milestone)
        .join(Project)
        .where(
            Milestone.id == milestone_id,
            Project.id == project_id,
            Project.workspace_id == workspace_id
        )
    )
    milestone = result.scalar_one_or_none()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found in this workspace/project")
    return milestone

@router.post("/", response_model=DeliverableResponse, status_code=status.HTTP_201_CREATED)
async def create_deliverable(
    workspace_id: int,
    project_id: int,
    milestone_id: int,
    deliverable_in: DeliverableCreate,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    if member.role not in [UserRole.ADMIN, UserRole.PM, UserRole.CREATIVE]:
        raise HTTPException(status_code=403, detail="Only team members can upload deliverables")
        
    await verify_milestone_in_workspace(workspace_id, project_id, milestone_id, db)
    
    result = await db.execute(
        select(Deliverable).where(Deliverable.milestone_id == milestone_id).order_by(Deliverable.version.desc())
    )
    last_deliverable = result.scalars().first()
    next_version = (last_deliverable.version + 1) if last_deliverable else 1
    
    deliverable = Deliverable(
        milestone_id=milestone_id,
        version=next_version,
        file_name=deliverable_in.file_name,
        file_type=deliverable_in.file_type,
        file_size=deliverable_in.file_size,
        storage_path=deliverable_in.storage_path
    )
    db.add(deliverable)
    await db.commit()
    await db.refresh(deliverable)
    return deliverable

@router.get("/", response_model=list[DeliverableResponse])
async def list_deliverables(
    workspace_id: int,
    project_id: int,
    milestone_id: int,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    await verify_milestone_in_workspace(workspace_id, project_id, milestone_id, db)
    
    result = await db.execute(
        select(Deliverable).where(Deliverable.milestone_id == milestone_id).order_by(Deliverable.version.desc())
    )
    return result.scalars().all()

@router.patch("/{deliverable_id}/status", response_model=DeliverableResponse)
async def update_deliverable_status(
    workspace_id: int,
    project_id: int,
    milestone_id: int,
    deliverable_id: int,
    status_update: DeliverableStatusUpdate,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    await verify_milestone_in_workspace(workspace_id, project_id, milestone_id, db)
    
    result = await db.execute(
        select(Deliverable).where(Deliverable.id == deliverable_id, Deliverable.milestone_id == milestone_id)
    )
    deliverable = result.scalar_one_or_none()
    if not deliverable:
        raise HTTPException(status_code=404, detail="Deliverable not found")
        
    if status_update.status == DeliverableStatus.APPROVED:
        if member.role not in [UserRole.ADMIN, UserRole.PM, UserRole.CLIENT]:
            raise HTTPException(status_code=403, detail="Only Admins, PMs, and Clients can approve deliverables")
            
    deliverable.status = status_update.status
    await db.commit()
    await db.refresh(deliverable)
    
    # Broadcast the status change via Redis/WebSocket
    response_data = DeliverableResponse.model_validate(deliverable)
    await manager.broadcast(deliverable_id, {
        "type": "deliverable_status_update",
        "payload": response_data.model_dump(mode="json")
    })
    
    return response_data