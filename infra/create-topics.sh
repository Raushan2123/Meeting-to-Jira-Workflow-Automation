#!/usr/bin/env bash
set -euo pipefail

BOOTSTRAP="kafka:9092"

echo "⏳ Waiting for Kafka to be ready..."
until kafka-topics --bootstrap-server "$BOOTSTRAP" --list >/dev/null 2>&1; do
  sleep 2
done
echo "✅ Kafka is ready"

create_topic () {
  local topic="$1"
  local partitions="${2:-3}"
  local replication="${3:-1}"
  kafka-topics --bootstrap-server "$BOOTSTRAP" \
    --create --if-not-exists \
    --topic "$topic" \
    --partitions "$partitions" \
    --replication-factor "$replication" >/dev/null
  echo "✅ Topic ensured: $topic"
}

create_topic "meeting.uploaded"
create_topic "meeting.transcribed"
create_topic "meeting.tasks_extracted"
create_topic "meeting.jira_created"
create_topic "meeting.dlq" 1 1

echo "🎉 All topics created"
