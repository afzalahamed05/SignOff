import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.deps import get_workspace_member
from app.core.stripe import get_or_create_customer, create_stripe_invoice
from app.models import User, WorkspaceMember, Project, Milestone, Invoice, Client, UserRole, InvoiceStatus
from app.schemas.milestone import MilestoneCreate, MilestoneUpdate, MilestoneResponse
from app.schemas.invoice import InvoiceResponse

router = APIRouter(prefix="/workspaces/{workspace_id}/projects/{project_id}/milestones", tags=["milestones"])

async def verify_project_in_workspace(workspace_id: int, project_id: int, db: AsyncSession):
    result = await db.execute(select(Project).where(Project.id == project_id, Project.workspace_id == workspace_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found in this workspace")
    return project

@router.post("/", response_model=MilestoneResponse, status_code=status.HTTP_201_CREATED)
async def create_milestone(workspace_id: int, project_id: int, milestone_in: MilestoneCreate, current_user: User = Depends(get_current_user), member: WorkspaceMember = Depends(get_workspace_member), db: AsyncSession = Depends(get_db)):
    if member.role not in [UserRole.ADMIN, UserRole.PM]: raise HTTPException(status_code=403, detail="Only Admins and PMs can create milestones")
    await verify_project_in_workspace(workspace_id, project_id, db)
    milestone = Milestone(project_id=project_id, name=milestone_in.name, description=milestone_in.description, due_date=milestone_in.due_date, amount=milestone_in.amount)
    db.add(milestone)
    await db.commit()
    await db.refresh(milestone)
    return milestone

@router.get("/", response_model=list[MilestoneResponse])
async def list_milestones(workspace_id: int, project_id: int, current_user: User = Depends(get_current_user), member: WorkspaceMember = Depends(get_workspace_member), db: AsyncSession = Depends(get_db)):
    await verify_project_in_workspace(workspace_id, project_id, db)
    result = await db.execute(select(Milestone).options(selectinload(Milestone.invoice)).where(Milestone.project_id == project_id).order_by(Milestone.created_at))
    return result.scalars().all()

@router.get("/{milestone_id}", response_model=MilestoneResponse)
async def get_milestone(workspace_id: int, project_id: int, milestone_id: int, current_user: User = Depends(get_current_user), member: WorkspaceMember = Depends(get_workspace_member), db: AsyncSession = Depends(get_db)):
    await verify_project_in_workspace(workspace_id, project_id, db)
    result = await db.execute(select(Milestone).options(selectinload(Milestone.invoice)).where(Milestone.id == milestone_id, Milestone.project_id == project_id))
    milestone = result.scalar_one_or_none()
    if not milestone: raise HTTPException(status_code=404, detail="Milestone not found")
    return milestone

@router.patch("/{milestone_id}", response_model=MilestoneResponse)
async def update_milestone(workspace_id: int, project_id: int, milestone_id: int, milestone_in: MilestoneUpdate, current_user: User = Depends(get_current_user), member: WorkspaceMember = Depends(get_workspace_member), db: AsyncSession = Depends(get_db)):
    if member.role not in [UserRole.ADMIN, UserRole.PM]: raise HTTPException(status_code=403, detail="Only Admins and PMs can update milestones")
    await verify_project_in_workspace(workspace_id, project_id, db)
    result = await db.execute(select(Milestone).where(Milestone.id == milestone_id, Milestone.project_id == project_id))
    milestone = result.scalar_one_or_none()
    if not milestone: raise HTTPException(status_code=404, detail="Milestone not found")
    for key, value in milestone_in.model_dump(exclude_unset=True).items(): setattr(milestone, key, value)
    await db.commit()
    await db.refresh(milestone)
    return milestone

@router.delete("/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_milestone(workspace_id: int, project_id: int, milestone_id: int, current_user: User = Depends(get_current_user), member: WorkspaceMember = Depends(get_workspace_member), db: AsyncSession = Depends(get_db)):
    if member.role not in [UserRole.ADMIN, UserRole.PM]: raise HTTPException(status_code=403, detail="Only Admins and PMs can delete milestones")
    await verify_project_in_workspace(workspace_id, project_id, db)
    result = await db.execute(select(Milestone).where(Milestone.id == milestone_id, Milestone.project_id == project_id))
    milestone = result.scalar_one_or_none()
    if not milestone: raise HTTPException(status_code=404, detail="Milestone not found")
    await db.delete(milestone)
    await db.commit()

@router.post("/{milestone_id}/generate-invoice", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def generate_invoice(workspace_id: int, project_id: int, milestone_id: int, current_user: User = Depends(get_current_user), member: WorkspaceMember = Depends(get_workspace_member), db: AsyncSession = Depends(get_db)):
    if member.role not in [UserRole.ADMIN, UserRole.PM]: raise HTTPException(status_code=403, detail="Only Admins and PMs can generate invoices")
    await verify_project_in_workspace(workspace_id, project_id, db)
    
    result = await db.execute(select(Milestone).where(Milestone.id == milestone_id, Milestone.project_id == project_id))
    milestone = result.scalar_one_or_none()
    if not milestone: raise HTTPException(status_code=404, detail="Milestone not found")
        
    existing_invoice = await db.execute(select(Invoice).where(Invoice.milestone_id == milestone_id))
    if existing_invoice.scalar_one_or_none(): raise HTTPException(status_code=400, detail="Invoice already generated for this milestone")
    
    # Fetch Project and Client
    proj_result = await db.execute(select(Project).where(Project.id == milestone.project_id))
    project = proj_result.scalar_one()
    if not project.client_id: raise HTTPException(status_code=400, detail="Project must have a client to generate an invoice")
    
    client_result = await db.execute(select(Client).where(Client.id == project.client_id))
    client = client_result.scalar_one()
    
    # Run synchronous Stripe calls in a thread to avoid blocking the async event loop
    customer_id = await asyncio.to_thread(get_or_create_customer, client.email, client.name)
    stripe_invoice = await asyncio.to_thread(create_stripe_invoice, customer_id, milestone.amount, f"{project.name} - {milestone.name}")
    
    # Save Stripe customer ID to client for future use
    client.stripe_customer_id = customer_id
    
    invoice = Invoice(
        milestone_id=milestone.id,
        stripe_invoice_id=stripe_invoice["id"],
        hosted_invoice_url=stripe_invoice["hosted_invoice_url"],
        amount=milestone.amount,
        status=InvoiceStatus.SENT
    )
    db.add(invoice)
    await db.commit()
    await db.refresh(invoice)
    return invoice