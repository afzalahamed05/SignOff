from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.deps import get_workspace_member
from app.models import User, WorkspaceMember, Project, Client, UserRole
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse

router = APIRouter(prefix="/workspaces/{workspace_id}/projects", tags=["projects"])

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    workspace_id: int,
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    if member.role not in [UserRole.ADMIN, UserRole.PM]:
        raise HTTPException(status_code=403, detail="Only Admins and PMs can create projects")
        
    # Verify client belongs to workspace if provided
    if project_in.client_id:
        client_result = await db.execute(
            select(Client).where(Client.id == project_in.client_id, Client.workspace_id == workspace_id)
        )
        if not client_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Client not found in this workspace")
            
    project = Project(
        workspace_id=workspace_id,
        client_id=project_in.client_id,
        name=project_in.name,
        description=project_in.description,
        status=project_in.status
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project

@router.get("/", response_model=list[ProjectResponse])
async def list_projects(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    # All workspace members can list projects
    result = await db.execute(
        select(Project).where(Project.workspace_id == workspace_id)
    )
    return result.scalars().all()

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    workspace_id: int,
    project_id: int,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.workspace_id == workspace_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    workspace_id: int,
    project_id: int,
    project_in: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    if member.role not in [UserRole.ADMIN, UserRole.PM]:
        raise HTTPException(status_code=403, detail="Only Admins and PMs can update projects")
        
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.workspace_id == workspace_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    update_data = project_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
        
    await db.commit()
    await db.refresh(project)
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    workspace_id: int,
    project_id: int,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    if member.role not in [UserRole.ADMIN, UserRole.PM]:
        raise HTTPException(status_code=403, detail="Only Admins and PMs can delete projects")
        
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.workspace_id == workspace_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    await db.delete(project)
    await db.commit()