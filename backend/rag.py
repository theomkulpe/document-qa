from groq import Groq
from backend.vectorstore import retrieve

client = Groq()

def build_prompt(context_chunks: list[str], question: str) -> str:
    context = "\n\n".join(context_chunks)
    return f"""Answer the question using only the context below.
If the answer isn't in the context, say "I don't know."

Context:
{context}

Question: {question}"""

def stream_answer(session_id: str, question: str):
    chunks = retrieve(session_id, question)
    '''print("=== RETRIEVED CHUNKS ===")
    for i, c in enumerate(chunks):
        print(f"[{i}] {c[:200]}\n")'''
        
    prompt = build_prompt(chunks, question)

    stream = client.chat.completions.create(
        model = "llama-3.3-70b-versatile",
        messages = [{"role": "user", "content": prompt}],
        stream = True
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
