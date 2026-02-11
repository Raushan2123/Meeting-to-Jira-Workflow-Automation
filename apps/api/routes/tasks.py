from fastapi import APIRouter, HTTPException
from apps.shared.redis_store import get_tasks

router = APIRouter()

@router.get("/{meeting_id}/tasks")
def get_meeting_tasks(meeting_id: str):
    tasks = get_tasks(meeting_id)

    if not tasks:
        raise HTTPException(status_code=404, detail="Tasks not found")

    return tasks
