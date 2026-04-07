import os
import gradio as gr
import requests

API_URL = os.getenv("API_URL", "http://localhost:8000")

def search_books_keyword(q):
    res = requests.get(f"{API_URL}/books/search", params={"q": q})
    return [[b["title"], b.get("synopsis", "")] for b in res.json()]

def search_books_semantic(q):
    res = requests.get(f"{API_URL}/books/semantic-search", params={"q": q})
    return [[b["title"], b.get("synopsis", "")] for b in res.json()]

def search_books_rag(q):
    res = requests.get(f"{API_URL}/books/rag-search", params={"q": q})
    data = res.json()
    return data["answer"], [[s] for s in data["sources"]]

def fetch_books():
    res = requests.get(f"{API_URL}/books")
    return [[b["id"], b["title"], b.get("author", {}).get("name", "N/A")] for b in res.json()]

def add_book(title, author_id, synopsis):
    payload = {"title": title, "author_id": author_id, "synopsis": synopsis}
    requests.post(f"{API_URL}/books", json=payload)
    return fetch_books()

def delete_book(book_id):
    requests.delete(f"{API_URL}/books/{book_id}")
    return fetch_books()

def fetch_authors():
    res = requests.get(f"{API_URL}/authors")
    return [[a["id"], a["name"], a["bio"]] for a in res.json()]

def add_author(name, bio):
    payload = {"name": name, "bio": bio}
    requests.post(f"{API_URL}/authors", json=payload)
    return fetch_authors()

def delete_author(author_id):
    requests.delete(f"{API_URL}/authors/{author_id}")
    return fetch_authors()

def fetch_reviews():
    res = requests.get(f"{API_URL}/reviews")
    return [[r["id"], r["comment"], r["rating"]] for r in res.json()]

def delete_review(review_id):
    requests.delete(f"{API_URL}/reviews/{review_id}")
    return fetch_reviews()

with gr.Blocks() as demo:
    gr.Markdown("# Library Management System")
    
    with gr.Tab("Search & AI"):
        with gr.Row():
            q_in = gr.Textbox(label="Query")
            s_btn = gr.Button("Keyword Search")
            v_btn = gr.Button("Vector Search")
            r_btn = gr.Button("Ask Librarian (RAG)")
        out_df = gr.Dataframe(headers=["Title", "Synopsis"])
        ans_box = gr.Textbox(label="Librarian Answer")
        
        s_btn.click(search_books_keyword, inputs=q_in, outputs=out_df)
        v_btn.click(search_books_semantic, inputs=q_in, outputs=out_df)
        r_btn.click(search_books_rag, inputs=q_in, outputs=[ans_box, out_df])

    with gr.Tab("Manage Books"):
        with gr.Row():
            t_in = gr.Textbox(label="Title")
            a_id_in = gr.Textbox(label="Author ID")
            syn_in = gr.Textbox(label="Synopsis")
            add_b_btn = gr.Button("Add Book")
        b_df = gr.Dataframe(headers=["ID", "Title", "Author"])
        del_b_id = gr.Textbox(label="Book ID to Delete")
        del_b_btn = gr.Button("Delete Book")
        
        add_b_btn.click(add_book, inputs=[t_in, a_id_in, syn_in], outputs=b_df)
        del_b_btn.click(delete_book, inputs=del_b_id, outputs=b_df)
        demo.load(fetch_books, outputs=b_df)

    with gr.Tab("Manage Authors"):
        with gr.Row():
            n_in = gr.Textbox(label="Name")
            b_in = gr.Textbox(label="Bio")
            add_a_btn = gr.Button("Add Author")
        a_df = gr.Dataframe(headers=["ID", "Name", "Bio"])
        del_a_id = gr.Textbox(label="Author ID to Delete")
        del_a_btn = gr.Button("Delete Author")
        
        add_a_btn.click(add_author, inputs=[n_in, b_in], outputs=a_df)
        del_a_btn.click(delete_author, inputs=del_a_id, outputs=a_df)
        demo.load(fetch_authors, outputs=a_df)

    with gr.Tab("Manage Reviews"):
        r_df = gr.Dataframe(headers=["ID", "Comment", "Rating"])
        del_r_id = gr.Textbox(label="Review ID to Delete")
        del_r_btn = gr.Button("Delete Review")
        
        del_r_btn.click(delete_review, inputs=del_r_id, outputs=r_df)
        demo.load(fetch_reviews, outputs=r_df)