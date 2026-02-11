from fastapi import APIRouter
from apps.shared.redis_store import get_job_status

router = APIRouter()

@router.get("/{job_id}")
def job_status(job_id: str):
    return get_job_status(job_id)
