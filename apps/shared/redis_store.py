import redis
import json
from apps.shared.config import REDIS_URL

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def set_job_status(job_id: str, status: str):
    redis_client.hset(f"job:{job_id}", mapping={"status": status})

def get_job_status(job_id: str):
    return redis_client.hgetall(f"job:{job_id}")
    
def save_transcript(meeting_id: str, transcript: dict):
    redis_client.hset(
        f"meeting:{meeting_id}",
        mapping={
            "text": transcript["text"],
            "language": transcript.get("language"),
            "duration": transcript.get("duration")
        }
    )

def get_transcript(meeting_id: str):
    return redis_client.hgetall(f"meeting:{meeting_id}")

def save_tasks(meeting_id: str, data: dict):
    redis_client.set(f"meeting:{meeting_id}:tasks", json.dumps(data))

def set_tasks(meeting_id: str, data: dict):
    redis_client.set(f"meeting:{meeting_id}:tasks", json.dumps(data))

def get_tasks(meeting_id: str):
    raw = redis_client.get(f"meeting:{meeting_id}:tasks")
    return json.loads(raw) if raw else None

def mark_jira_created(meeting_id: str, issue_key: str):
    """
    Marks that Jira tickets have been created for this meeting.
    Prevents duplicate issue creation.
    """
    redis_client.set(f"meeting:{meeting_id}:jira_issue", issue_key)


def is_jira_created(meeting_id: str) -> bool:
    """
    Check if Jira ticket already exists for a meeting.
    """
    return redis_client.exists(f"meeting:{meeting_id}:jira_issue") == 1

