from apps.shared.kafka_bus import get_consumer, get_producer
from apps.shared.redis_store import set_job_status
from apps.shared.llm.router import extract_tasks
from apps.shared.redis_store import set_tasks
import time


print("⏳ Waiting for Kafka...")

while True:
    try:
        consumer = get_consumer("meeting.transcribed", "extract-group")
        producer = get_producer()
        print("✅ Connected to Kafka")
        break
    except Exception as e:
        print("❌ Kafka not ready, retrying...", e)
        time.sleep(5)

print("🧠 LLM extraction worker started...")

for msg in consumer:
    data = msg.value
    job_id = data["job_id"]
    meeting_id = data["meeting_id"]
    transcript = data.get("transcript")
    print("📨 Received transcript:", transcript[:100])

    try:
        set_job_status(job_id, "extracting_tasks")

        result = extract_tasks(transcript)
        set_tasks(meeting_id, result)

        producer.send("meeting.tasks_extracted", {
            "job_id": job_id,
            "meeting_id": meeting_id,
            "summary": result["summary"],
            "tasks": result["tasks"]
        })
        print("hi")
        producer.flush()

        set_job_status(job_id, "tasks_extracted")

    except Exception as e:
        set_job_status(job_id, f"llm_failed: {str(e)}")
