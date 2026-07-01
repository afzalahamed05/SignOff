import asyncio
import json
from sqlalchemy import select
import ollama

from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.core.websocket import manager
from app.core.config import settings
from app.models import AITask, AITaskStatus, Deliverable, Comment, User, Milestone, Project

# Initialize Ollama client pointing to local server
ollama_client = ollama.Client(host=settings.OLLAMA_BASE_URL)

@celery_app.task(bind=True, name="synthesize_ai_feedback")
def synthesize_ai_feedback(self, task_id: int):
    # Celery tasks are synchronous. We run our async logic in a new event loop.
    asyncio.run(_run_synthesis(task_id))

async def _run_synthesis(task_id: int):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(AITask).where(AITask.id == task_id))
        task = result.scalar_one_or_none()
        if not task:
            return
            
        task.status = AITaskStatus.PROCESSING
        await db.commit()
        
        try:
            # 1. Fetch Deliverable
            del_result = await db.execute(select(Deliverable).where(Deliverable.id == task.deliverable_id))
            deliverable = del_result.scalar_one()
            
            # 2. Fetch Milestone
            mile_result = await db.execute(select(Milestone).where(Milestone.id == deliverable.milestone_id))
            milestone = mile_result.scalar_one()
            
            # 3. Fetch Project
            proj_result = await db.execute(select(Project).where(Project.id == milestone.project_id))
            project = proj_result.scalar_one()
            
            # 4. Fetch Comments and Users
            com_result = await db.execute(
                select(Comment)
                .where(Comment.deliverable_id == deliverable.id)
                .order_by(Comment.created_at)
            )
            comments = com_result.scalars().all()
            
            user_ids = list(set(c.user_id for c in comments))
            users = {}
            if user_ids:
                users_result = await db.execute(select(User).where(User.id.in_(user_ids)))
                users = {u.id: u.full_name for u in users_result.scalars().all()}
                
            # 5. Format Comments (Threaded context for the AI)
            # We build a map to safely nest replies without triggering async lazy-loading errors
            comment_map = {c.id: {"comment": c, "replies": []} for c in comments}
            top_level_comments = []
            for c in comments:
                if c.parent_id and c.parent_id in comment_map:
                    comment_map[c.parent_id]["replies"].append(c)
                else:
                    top_level_comments.append(c)
                    
            formatted_comments = []
            for c in top_level_comments:
                user_name = users.get(c.user_id, "Unknown")
                formatted_comments.append(f"[{user_name}]: {c.content}")
                for reply in comment_map[c.id]["replies"]:
                    reply_user = users.get(reply.user_id, "Unknown")
                    formatted_comments.append(f"  -> [{reply_user}] (reply): {reply.content}")
                    
            comments_text = "\n".join(formatted_comments) if formatted_comments else "No text comments provided."
            
            # 6. Construct Rich Text Prompt
            prompt = f"""You are an expert creative director. Your task is to synthesize messy client feedback into a clean, prioritized action list for the design team.

Project Context:
- Project: {project.name}
- Description: {project.description or 'N/A'}

Milestone Context:
- Milestone: {milestone.name}
- Description: {milestone.description or 'N/A'}

Deliverable Context:
- File: {deliverable.file_name} ({deliverable.file_type})
- Status: {deliverable.status}

Client Feedback & Discussions:
{comments_text}

Instructions:
1. Analyze the textual feedback, threaded discussions, and project context.
2. Group duplicate or highly similar comments.
3. Resolve any contradictions based on the discussion threads.
4. Extract clear, actionable items for the design team.
5. Prioritize the items (High, Medium, Low).
6. Output ONLY a valid JSON object with a single key "action_items" containing an array of objects.

JSON Format:
{{
  "action_items": [
    {{
      "priority": "High",
      "category": "Design/Content/Technical",
      "action": "Clear instruction here.",
      "resolved_contradictions": null
    }}
  ]
}}
"""
            
            messages = [
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
            
            # 7. Call Ollama (Strictly Text-Only)
            # format="json" forces the qwen2.5 model to output valid JSON
            ai_response = await asyncio.to_thread(
                ollama_client.chat,
                model=settings.OLLAMA_MODEL,
                messages=messages,
                format="json" 
            )
            ai_result = ai_response["message"]["content"]
            
            # 8. Save result to database
            task.result_json = ai_result
            task.status = AITaskStatus.COMPLETED
            await db.commit()
            
            # 9. Broadcast completion via WebSocket
            await manager.broadcast(deliverable.id, {
                "type": "ai_synthesis_completed",
                "payload": {
                    "task_id": task.id,
                    "deliverable_id": deliverable.id,
                    "result": json.loads(ai_result)
                }
            })
            
        except Exception as e:
            task.status = AITaskStatus.FAILED
            task.error_message = str(e)
            await db.commit()
            raise