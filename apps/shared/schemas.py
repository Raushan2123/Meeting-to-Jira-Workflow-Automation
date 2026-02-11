from pydantic import BaseModel, model_validator, field_validator
from typing import List, Optional

class JobResponse(BaseModel):
    job_id: str
    meeting_id: str

class Task(BaseModel):
    title: str
    owner: Optional[str]
    due_date: Optional[str]
    priority: Optional[str]

class TaskSchema(BaseModel):
    title: Optional[str] = None
    owner: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None

    @field_validator("title", mode="before")
    @classmethod
    def coerce_title(cls, v):
        # null -> ""
        if v is None:
            return ""
        return str(v)

    @model_validator(mode="after")
    def fill_missing_title(self):
        # Ensure title is NEVER empty at schema boundary
        t = (self.title or "").strip()
        if not t:
            # minimal safe placeholder (will be improved using summary in TaskExtractionSchema)
            self.title = "Action item"
        else:
            self.title = t
        return self


class TaskExtractionSchema(BaseModel):
    summary: str
    tasks: List[TaskSchema]

    @field_validator("summary", mode="before")
    @classmethod
    def coerce_summary(cls, v):
        if v is None:
            return ""
        return str(v).strip()

    @model_validator(mode="after")
    def improve_task_titles(self):
        base = (self.summary or "").strip() or "Action item"

        for task in self.tasks:
            # If schema fallback produced generic title, upgrade it deterministically
            if task.title == "Action item":
                if task.due_date:
                    task.title = f"{base} (due {task.due_date})"
                else:
                    task.title = base

            # Keep Jira-safe length
            task.title = " ".join(task.title.split())[:250]

        return self