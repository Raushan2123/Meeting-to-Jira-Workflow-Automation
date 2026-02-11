import time
from typing import Any, Dict

from apps.shared.kafka_bus import get_consumer
from apps.shared.jira.client import JiraClient
from apps.shared.jira.utils import (
    clean_str,
    normalize_priority,
    make_safe_title,
    is_iso_date,
)
from apps.shared.redis_store import (
    is_jira_created,
    mark_jira_created,
    set_job_status,
)

print("⏳ Waiting for Kafka...")

while True:
    try:
        consumer = get_consumer("meeting.tasks_extracted", "jira-group")
        print("✅ Connected to Kafka")
        break
    except Exception as e:
        print("❌ Kafka not ready, retrying...", repr(e))
        time.sleep(5)

jira = JiraClient()
print("🎫 Jira worker started...")

for msg in consumer:
    data: Dict[str, Any] = msg.value or {}

    meeting_id = clean_str(data.get("meeting_id"))
    job_id = clean_str(data.get("job_id"))
    meeting_summary = clean_str(data.get("summary")) or ""
    tasks = data.get("tasks") or []

    try:
        if not meeting_id:
            print("❌ Missing meeting_id:", data)
            continue

        if is_jira_created(meeting_id):
            print(f"⚠️ Jira already created for {meeting_id}")
            if job_id:
                set_job_status(job_id, "jira_skipped_already_created")
            continue

        if job_id:
            set_job_status(job_id, "creating_jira")

        created_keys = []

        for idx, task in enumerate(tasks, start=1):
            if not isinstance(task, dict):
                continue

            due = clean_str(task.get("due_date"))
            if not is_iso_date(due):
                due = None

            owner = clean_str(task.get("owner"))
            priority = normalize_priority(task.get("priority"))

            title = make_safe_title(
                raw_title=task.get("title"),
                meeting_summary=meeting_summary,
                due_date=due,
                index=idx,
            )

            description = (
                f"Meeting ID: {meeting_id}\n"
                f"Owner: {owner or 'Not specified'}\n"
                f"Due date: {due or 'Not specified'}\n"
                f"Meeting summary: {meeting_summary or 'N/A'}"
            )

            print("📝 Creating Jira issue:", title)

            issue = jira.create_issue(
                summary=title,
                description=description,
                priority=priority,
                due_date=due,
            )

            created_keys.append(issue["key"])
            print("✅ Created:", issue["key"])

        if created_keys:
            mark_jira_created(meeting_id, ",".join(created_keys))
            if job_id:
                set_job_status(job_id, f"jira_created: {created_keys}")
        else:
            if job_id:
                set_job_status(job_id, "jira_failed: no_valid_tasks")

    except Exception as e:
        print("❌ Jira failed:", repr(e))
        if job_id:
            set_job_status(job_id, f"jira_failed: {str(e)}")
