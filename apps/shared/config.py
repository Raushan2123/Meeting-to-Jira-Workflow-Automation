import os

APP_ENV = os.getenv("APP_ENV", "dev")

# Kafka (MANDATORY, no silent fallback)
KAFKA_BOOTSTRAP_SERVERS = os.environ["KAFKA_BOOTSTRAP_SERVERS"]

# Redis
REDIS_URL = os.environ["REDIS_URL"]

# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# Storage
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/data/uploads")

# Jira
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")
