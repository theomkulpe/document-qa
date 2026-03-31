from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
import shutil, os
import tempfile

from ingestion import ingest
from vectorstore import add_chunks
from session import new_session, add_messages, get_history
from rag import stream_answer

app = FastAPI()

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(None),
    url: str = Form(None)
):
    session_id = new_session()
    
    if file:
        suffix = os.path.splitext(file.filename)[1]  # preserves .pdf extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_path = tmp.name
        chunks = ingest(temp_path, "pdf")
        os.remove(temp_path)
    elif url:
        chunks = ingest(url, "url")
    else:
        return {"error": "Provide a file or URL"}
    
    add_chunks(session_id, chunks)
    return {"session_id": session_id}

@app.post("/chat")
async def chat(session_id: str = Form(...), question: str = Form(...)):
    add_messages(session_id, "user", question)

    def generate():
        full_response = ""
        for token in stream_answer(session_id, question):
            full_response += token
            yield token
        add_messages(session_id, "assistant", full_response)

    return StreamingResponse(generate(), media_type = "text/plain")

@app.get("/history/{session_id}")
async def history(session_id: str):
    return {"history": get_history(session_id)}