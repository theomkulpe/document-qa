from collections import defaultdict
import uuid

conversation_store = defaultdict(list)

def new_session() -> str:
    return str(uuid.uuid4())

def add_messages(session_id: str, role: str, content: str):
    conversation_store[session_id].append({"role": role, "content": content})

def get_history(session_id: str) -> list[dict]:
    return conversation_store[session_id]