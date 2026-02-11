from fastapi import FastAPI
from apps.api.routes import meetings, jobs
from apps.api.routes import meetings_read
from apps.api.routes import tasks

app = FastAPI(title="Meeting-to-Jira API")

app.include_router(meetings.router, prefix="/meetings")
app.include_router(jobs.router, prefix="/jobs")
app.include_router(meetings_read.router, prefix="/meetings")
app.include_router(tasks.router, prefix="/meetings")

@app.get("/health")
def health():
    return {"status": "ok"}
