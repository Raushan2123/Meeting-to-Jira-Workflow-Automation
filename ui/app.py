import streamlit as st
import requests
import time

API_BASE = "http://localhost:8000"  # change if needed

st.set_page_config(page_title="Meeting → Jira Automation", layout="wide")

st.title("🎙️ Meeting to Jira Automation")

uploaded_file = st.file_uploader("Upload meeting audio", type=["wav", "mp3", "m4a"])

if uploaded_file:
    if st.button("🚀 Process Meeting"):
        files = {"file": uploaded_file.getvalue()}
        response = requests.post(f"{API_BASE}/meetings/upload", files=files)

        if response.status_code == 200:
            data = response.json()
            job_id = data["job_id"]
            meeting_id = data["meeting_id"]

            st.success(f"Job Created: {job_id}")

            status_placeholder = st.empty()

            while True:
                job_resp = requests.get(f"{API_BASE}/jobs/{job_id}")
                status = job_resp.json()["status"]

                status_placeholder.info(f"Current Status: {status}")

                if "jira_created" in status or "failed" in status:
                    break

                time.sleep(2)

            st.success("Processing Complete")

            # Fetch tasks
            task_resp = requests.get(f"{API_BASE}/meetings/{meeting_id}/tasks")
            if task_resp.status_code == 200:
                tasks_data = task_resp.json()

                st.subheader("📝 Extracted Summary")
                st.write(tasks_data.get("summary"))

                st.subheader("📌 Tasks")
                for t in tasks_data.get("tasks", []):
                    st.markdown(f"""
                    **Title:** {t.get("title")}  
                    Owner: {t.get("owner")}  
                    Due: {t.get("due_date")}  
                    Priority: {t.get("priority")}
                    """)
