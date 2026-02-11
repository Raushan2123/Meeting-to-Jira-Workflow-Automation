import uuid
from fastapi import APIRouter, UploadFile, File
from apps.shared.redis_store import set_job_status
from apps.shared.kafka_bus import get_producer
from apps.shared.storage import save_upload


router = APIRouter()

@router.post("/upload")
async def upload_meeting(file: UploadFile = File(...)):
    meeting_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())

    set_job_status(job_id, "uploaded")

    producer = get_producer()
    producer.send("meeting.uploaded", {
        "job_id": job_id,
        "meeting_id": meeting_id
    })
    producer.flush()

    content = await file.read()
    audio_path = save_upload(meeting_id, content)

    producer.send("meeting.uploaded", {
        "job_id": job_id,
        "meeting_id": meeting_id,
        "audio_path": audio_path
    })

    return {"meeting_id": meeting_id, "job_id": job_id}
