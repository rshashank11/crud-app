import os
import gradio as gr
import requests

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

def search(q):
    if not q: return []
    try:
        response = requests.get(f"{API_URL}/books/search", params={"q": q})
        if response.status_code == 200:
            return [[b["title"], b.get("synopsis", "")] for b in response.json()]
        return []
    except Exception:
        return []

def semantic_search(q):
    if not q: return []
    try:
        response = requests.get(f"{API_URL}/books/semantic-search", params={"q": q})
        if response.status_code == 200:
            return [[b["title"], b.get("synopsis", "")] for b in response.json()]
        return []
    except Exception:
        return []

def rag_search(q):
    if not q: return "Please enter a question.", []
    try:
        response = requests.get(f"{API_URL}/books/rag-search", params={"q": q})
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "No answer generated.")
            sources = [[s] for s in data.get("sources", [])]
            return answer, sources
        return f"Error: {response.status_code}", []
    except Exception as e:
        return f"Connection Error: {e}", []

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# The Great Library: AI Search and RAG")

    with gr.Tab("Keyword Search"):
        gr.Markdown("### Traditional Database Search")
        with gr.Row():
            key_in = gr.Textbox(label="Search based on titles", scale=4)
            key_btn = gr.Button("Find Exact", variant="primary", scale=1)
        key_out = gr.Dataframe(headers=["Title", "Synopsis"], wrap=True)
        key_btn.click(fn=search, inputs=key_in, outputs=key_out)

    with gr.Tab("Semantic Search"):
        gr.Markdown("### AI Concept Search")
        with gr.Row():
            sem_in = gr.Textbox(label="Search by vibe or plot", scale=4)
            sem_btn = gr.Button("Find Vibe", variant="primary", scale=1)
        sem_out = gr.Dataframe(headers=["Title", "Synopsis"], wrap=True)
        sem_btn.click(fn=semantic_search, inputs=sem_in, outputs=sem_out)

    with gr.Tab("RAG Librarian"):
        gr.Markdown("### Ask the Librarian")
        with gr.Row():
            rag_in = gr.Textbox(label="Ask a question about the collection", scale=4)
            rag_btn = gr.Button("Ask AI", variant="primary", scale=1)
        rag_answer = gr.Textbox(label="AI Answer", interactive=False)
        rag_sources = gr.Dataframe(headers=["Books Consulted"], wrap=True)
        rag_btn.click(fn=rag_search, inputs=rag_in, outputs=[rag_answer, rag_sources])

if __name__ == "__main__":
    demo.launch()