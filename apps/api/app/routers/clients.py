from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.deps import get_workspace_member
from app.models import User, WorkspaceMember, Client, UserRole
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse

router = APIRouter(prefix="/workspaces/{workspace_id}/clients", tags=["clients"])

@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    workspace_id: int,
    client_in: ClientCreate,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    if member.role not in [UserRole.ADMIN, UserRole.PM]:
        raise HTTPException(status_code=403, detail="Only Admins and PMs can create clients")
        
    client = Client(
        workspace_id=workspace_id,
        name=client_in.name,
        email=client_in.email,
        company=client_in.company
    )
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client

@router.get("/", response_model=list[ClientResponse])
async def list_clients(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    # All workspace members can list clients
    result = await db.execute(
        select(Client).where(Client.workspace_id == workspace_id)
    )
    return result.scalars().all()

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    workspace_id: int,
    client_id: int,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Client).where(Client.id == client_id, Client.workspace_id == workspace_id)
    )
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    workspace_id: int,
    client_id: int,
    client_in: ClientUpdate,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    if member.role not in [UserRole.ADMIN, UserRole.PM]:
        raise HTTPException(status_code=403, detail="Only Admins and PMs can update clients")
        
    result = await db.execute(
        select(Client).where(Client.id == client_id, Client.workspace_id == workspace_id)
    )
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
        
    update_data = client_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(client, key, value)
        
    await db.commit()
    await db.refresh(client)
    return client

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    workspace_id: int,
    client_id: int,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    if member.role not in [UserRole.ADMIN, UserRole.PM]:
        raise HTTPException(status_code=403, detail="Only Admins and PMs can delete clients")
        
    result = await db.execute(
        select(Client).where(Client.id == client_id, Client.workspace_id == workspace_id)
    )
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
        
    await db.delete(client)
    await db.commit()