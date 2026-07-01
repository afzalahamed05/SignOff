from fastapi import APIRouter, Depends, HTTPException, status, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.deps import get_workspace_member
from app.core.websocket import manager
from app.models import User, WorkspaceMember, Project, Milestone, Deliverable, Comment, UserRole
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse

router = APIRouter(tags=["comments"])

async def verify_deliverable_in_workspace(workspace_id: int, project_id: int, milestone_id: int, deliverable_id: int, db: AsyncSession):
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
    deliverable = result.scalar_one_or_none()
    if not deliverable:
        raise HTTPException(status_code=404, detail="Deliverable not found in this workspace/project/milestone")
    return deliverable

@router.post("/workspaces/{workspace_id}/projects/{project_id}/milestones/{milestone_id}/deliverables/{deliverable_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    workspace_id: int,
    project_id: int,
    milestone_id: int,
    deliverable_id: int,
    comment_in: CommentCreate,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    await verify_deliverable_in_workspace(workspace_id, project_id, milestone_id, deliverable_id, db)
    
    if comment_in.parent_id:
        parent_result = await db.execute(
            select(Comment).where(Comment.id == comment_in.parent_id, Comment.deliverable_id == deliverable_id)
        )
        if not parent_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Parent comment not found in this deliverable")

    comment = Comment(
        deliverable_id=deliverable_id,
        user_id=current_user.id,
        content=comment_in.content,
        x_coord=comment_in.x_coord,
        y_coord=comment_in.y_coord,
        parent_id=comment_in.parent_id
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    
    response_data = CommentResponse(
        id=comment.id,
        deliverable_id=comment.deliverable_id,
        user_id=comment.user_id,
        content=comment.content,
        x_coord=comment.x_coord,
        y_coord=comment.y_coord,
        parent_id=comment.parent_id,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        user_name=current_user.full_name,
        user_avatar=current_user.avatar_url,
        replies=[]
    )
    
    # Broadcast the new comment via Redis/WebSocket
    await manager.broadcast(deliverable_id, {
        "type": "new_comment",
        "payload": response_data.model_dump(mode="json")
    })
    
    return response_data

@router.get("/workspaces/{workspace_id}/projects/{project_id}/milestones/{milestone_id}/deliverables/{deliverable_id}/comments", response_model=list[CommentResponse])
async def list_comments(
    workspace_id: int,
    project_id: int,
    milestone_id: int,
    deliverable_id: int,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    await verify_deliverable_in_workspace(workspace_id, project_id, milestone_id, deliverable_id, db)
    
    result = await db.execute(select(Comment).where(Comment.deliverable_id == deliverable_id).order_by(Comment.created_at))
    all_comments = result.scalars().all()
    
    if not all_comments:
        return []
        
    user_ids = list(set(c.user_id for c in all_comments))
    users_result = await db.execute(select(User).where(User.id.in_(user_ids)))
    users = {u.id: u for u in users_result.scalars().all()}
    
    comment_map = {}
    for c in all_comments:
        comment_map[c.id] = CommentResponse(
            id=c.id,
            deliverable_id=c.deliverable_id,
            user_id=c.user_id,
            content=c.content,
            x_coord=c.x_coord,
            y_coord=c.y_coord,
            parent_id=c.parent_id,
            created_at=c.created_at,
            updated_at=c.updated_at,
            user_name=users[c.user_id].full_name,
            user_avatar=users[c.user_id].avatar_url,
            replies=[]
        )
        
    top_level = []
    for c in all_comments:
        if c.parent_id is None:
            top_level.append(comment_map[c.id])
        else:
            if c.parent_id in comment_map:
                comment_map[c.parent_id].replies.append(comment_map[c.id])
                
    return top_level

@router.patch("/workspaces/{workspace_id}/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    workspace_id: int,
    comment_id: int,
    comment_in: CommentUpdate,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own comments")
        
    comment.content = comment_in.content
    await db.commit()
    await db.refresh(comment)
    
    return CommentResponse(
        id=comment.id,
        deliverable_id=comment.deliverable_id,
        user_id=comment.user_id,
        content=comment.content,
        x_coord=comment.x_coord,
        y_coord=comment.y_coord,
        parent_id=comment.parent_id,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        user_name=current_user.full_name,
        user_avatar=current_user.avatar_url,
        replies=[]
    )

@router.delete("/workspaces/{workspace_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    workspace_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own comments")
        
    await db.delete(comment)
    await db.commit()