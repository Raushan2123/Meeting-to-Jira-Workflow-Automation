import os
from apps.shared.config import UPLOAD_DIR

os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_upload(file_id: str, content: bytes) -> str:
    path = os.path.join(UPLOAD_DIR, f"{file_id}.bin")
    with open(path, "wb") as f:
        f.write(content)
    return path
