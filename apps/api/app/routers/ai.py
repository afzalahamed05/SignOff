import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.deps import get_workspace_member
from app.models import User, WorkspaceMember, Project, Milestone, Deliverable, AITask, AITaskStatus
from app.workers.ai_worker import synthesize_ai_feedback

router = APIRouter(prefix="/workspaces/{workspace_id}/projects/{project_id}/milestones/{milestone_id}/deliverables/{deliverable_id}/ai", tags=["ai"])

@router.post("/synthesize", status_code=status.HTTP_202_ACCEPTED)
async def synthesize_feedback(
    workspace_id: int,
    project_id: int,
    milestone_id: int,
    deliverable_id: int,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    # Verify deliverable exists in workspace
    result = await db.execute(
        select(Deliverable)
        .join(Milestone).join(Project)
        .where(
            Deliverable.id == deliverable_id,
            Milestone.id == milestone_id,
            Project.id == project_id,
            Project.workspace_id == workspace_id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Deliverable not found")
        
    # Create AI Task record
    ai_task = AITask(
        deliverable_id=deliverable_id,
        status=AITaskStatus.PENDING
    )
    db.add(ai_task)
    await db.commit()
    await db.refresh(ai_task)
    
    # Trigger Celery background task
    synthesize_ai_feedback.delay(ai_task.id)
    
    return {"task_id": ai_task.id, "status": ai_task.status}

@router.get("/tasks/{task_id}")
async def get_ai_task(
    workspace_id: int,
    project_id: int,
    milestone_id: int,
    deliverable_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(AITask).where(AITask.id == task_id, AITask.deliverable_id == deliverable_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "id": task.id,
        "status": task.status,
        "result": json.loads(task.result_json) if task.result_json else None,
        "error": task.error_message,
        "created_at": task.created_at
    }