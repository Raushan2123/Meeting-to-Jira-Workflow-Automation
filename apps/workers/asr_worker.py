from apps.shared.kafka_bus import get_consumer, get_producer
from apps.shared.redis_store import set_job_status
from apps.shared.asr.whisper_provider import transcribe
from apps.shared.redis_store import set_job_status, save_transcript

consumer = get_consumer("meeting.uploaded", "asr-group")
producer = get_producer()

print("🎙️ ASR worker started...")

for msg in consumer:
    data = msg.value
    job_id = data["job_id"]
    audio_path = data.get("audio_path", "/data/uploads/dummy.wav")

    try:
        set_job_status(job_id, "transcribing")

        result = transcribe(audio_path)

        save_transcript(
            meeting_id=data["meeting_id"],
            transcript=result
        )

        producer.send("meeting.transcribed", {
        "job_id": job_id,
        "meeting_id": data["meeting_id"],
        "transcript": result["text"],
        "language": result["language"]
    })
        producer.flush()

        set_job_status(job_id, "transcribed")

    except Exception as e:
        set_job_status(job_id, f"asr_failed: {str(e)}")
