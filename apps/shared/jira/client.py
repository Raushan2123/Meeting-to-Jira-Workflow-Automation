import base64
import os
import requests
from typing import Optional

from apps.shared.jira.utils import clean_str, is_iso_date, adf_text


class JiraClient:
    def __init__(self):
        self.base_url = (os.getenv("JIRA_BASE_URL") or "").rstrip("/")
        self.email = os.getenv("JIRA_EMAIL")
        self.api_token = os.getenv("JIRA_API_TOKEN")
        self.project_key = os.getenv("JIRA_PROJECT_KEY")

        if not all([self.base_url, self.email, self.api_token, self.project_key]):
            raise RuntimeError("Jira configuration missing in environment variables")

        token = base64.b64encode(
            f"{self.email}:{self.api_token}".encode()
        ).decode()

        self.headers = {
            "Authorization": f"Basic {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def create_issue(
        self,
        summary: str,
        description: str,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
        issue_type: str = "Task",
    ):
        summary = clean_str(summary) or "Action item"

        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": summary[:255],
                "description": adf_text(description),
                "issuetype": {"name": issue_type},
            }
        }

        if due_date and is_iso_date(due_date):
            payload["fields"]["duedate"] = due_date

        if priority:
            payload["fields"]["priority"] = {"name": priority}

        url = f"{self.base_url}/rest/api/3/issue"
        resp = requests.post(url, headers=self.headers, json=payload, timeout=30)

        if resp.status_code != 201:
            raise RuntimeError(
                f"Jira issue creation failed: {resp.status_code} {resp.text}"
            )

        return resp.json()
