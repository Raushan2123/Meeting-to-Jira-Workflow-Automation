from fastapi import APIRouter, HTTPException
from apps.shared.redis_store import get_transcript

router = APIRouter()

@router.get("/{meeting_id}")
def get_meeting(meeting_id: str):
    transcript = get_transcript(meeting_id)

    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")

    return transcript
