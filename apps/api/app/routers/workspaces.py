from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.deps import get_workspace_member
from app.models import User, Workspace, WorkspaceMember, UserRole
from app.schemas.workspace import (
    WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse,
    WorkspaceMemberCreate, WorkspaceMemberResponse
)

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_in: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Workspace).where(Workspace.slug == workspace_in.slug))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Workspace slug already exists")
    
    workspace = Workspace(
        name=workspace_in.name,
        slug=workspace_in.slug,
        owner_id=current_user.id
    )
    db.add(workspace)
    await db.flush()
    
    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=current_user.id,
        role=UserRole.ADMIN
    )
    db.add(member)
    await db.commit()
    await db.refresh(workspace)
    return workspace

@router.get("/", response_model=list[WorkspaceResponse])
async def list_workspaces(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Workspace).join(WorkspaceMember).where(WorkspaceMember.user_id == current_user.id)
    )
    return result.scalars().all()

@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace

@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: int,
    workspace_in: WorkspaceUpdate,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    if member.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can update workspace")
        
    result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()
    
    if workspace_in.name is not None:
        workspace.name = workspace_in.name
        
    await db.commit()
    await db.refresh(workspace)
    return workspace

@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    if workspace.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the owner can delete the workspace")
        
    await db.delete(workspace)
    await db.commit()

# --- Member Management ---

@router.post("/{workspace_id}/members", response_model=WorkspaceMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_member(
    workspace_id: int,
    member_in: WorkspaceMemberCreate,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    if member.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can add members")
        
    result = await db.execute(select(User).where(User.email == member_in.email))
    user_to_add = result.scalar_one_or_none()
    if not user_to_add:
        raise HTTPException(status_code=404, detail="User not found. They must register first.")
        
    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_to_add.id
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User is already a member of this workspace")
        
    new_member = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=user_to_add.id,
        role=member_in.role
    )
    db.add(new_member)
    await db.commit()
    await db.refresh(new_member)
    
    return WorkspaceMemberResponse(
        id=new_member.id,
        workspace_id=new_member.workspace_id,
        user_id=new_member.user_id,
        role=new_member.role,
        joined_at=new_member.joined_at,
        user_email=user_to_add.email,
        user_name=user_to_add.full_name
    )

@router.get("/{workspace_id}/members", response_model=list[WorkspaceMemberResponse])
async def list_members(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(WorkspaceMember).where(WorkspaceMember.workspace_id == workspace_id)
    )
    members = result.scalars().all()
    
    user_ids = [m.user_id for m in members]
    users_result = await db.execute(select(User).where(User.id.in_(user_ids)))
    users = {u.id: u for u in users_result.scalars().all()}
    
    return [
        WorkspaceMemberResponse(
            id=m.id,
            workspace_id=m.workspace_id,
            user_id=m.user_id,
            role=m.role,
            joined_at=m.joined_at,
            user_email=users[m.user_id].email,
            user_name=users[m.user_id].full_name
        )
        for m in members
    ]

@router.delete("/{workspace_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    workspace_id: int,
    member_id: int,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    if member.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can remove members")
        
    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.id == member_id,
            WorkspaceMember.workspace_id == workspace_id
        )
    )
    member_to_remove = result.scalar_one_or_none()
    if not member_to_remove:
        raise HTTPException(status_code=404, detail="Member not found")
        
    workspace_result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    workspace = workspace_result.scalar_one()
    if member_to_remove.user_id == workspace.owner_id:
        raise HTTPException(status_code=400, detail="Cannot remove the workspace owner")
        
    await db.delete(member_to_remove)
    await db.commit()