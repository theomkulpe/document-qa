import gradio as gr
import requests

BACKEND_URL = "http://localhost:8000"

def upload_document(file, url):
    if file:
        with open(file.name, "rb") as f:
            response = requests.post(f"{BACKEND_URL}/upload", files = {"file": f})
    elif url:
        response = requests.post(f"{BACKEND_URL}/upload", data = {"url": url})
    else:
        return None, "Provide a file or URL"
    
    session_id = response.json()["session_id"]
    return session_id, "Document uploaded successfully!"

def chat(question, session_id, history):
    if not session_id:
        return history, "Please upload a document first."
    
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": ""})
    
    with requests.post(
        f"{BACKEND_URL}/chat",
        data={"session_id": session_id, "question": question},
        stream=True
    ) as response:
        for token in response.iter_content(chunk_size=None, decode_unicode=True):
            history[-1]["content"] += token
            yield history, ""

with gr.Blocks() as demo:
    session_id = gr.State(None)

    gr.Markdown('# Document Q&A')

    with gr.Row():
        file_input = gr.File(label = "Upload PDF")
        url_input = gr.Textbox(label = "Or paste a URL")

    upload_btn = gr.Button("Upload")
    upload_status = gr.Textbox(label = "Status", interactive = False)

    chatbot = gr.Chatbot()
    question_input = gr.Textbox(label = "Ask a question")

    upload_btn.click(upload_document, inputs=[file_input, url_input], outputs=[session_id, upload_status])
    question_input.submit(chat, inputs=[question_input, session_id, chatbot], outputs=[chatbot, question_input])

demo.launch()
