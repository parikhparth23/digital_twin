import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr

load_dotenv(override=True)
openai = OpenAI()

BASE_DIR = Path(__file__).resolve().parent
FAVICON_PATH = BASE_DIR / "resources" / "favicon.png"

# --- Content Loading ---
def get_context():
    reader = PdfReader(BASE_DIR / "resources" / "resume.pdf")
    resume = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    with open(BASE_DIR / "resources" / "summary.txt", "r", encoding="utf-8") as f:
        summary = f.read()
    return resume, summary

resume, summary = get_context()

SYSTEM_PROMPT = f"""
You are a digital twin of Parth Parikh. 
You answer questions about: Career, Engineering experience, Skills, Projects, Technical background.
Represent Parth professionally.
Profile: {summary}
Resume: {resume}
Rules: Stay professional. Do not invent info. If you don't know, say so. Explain you are an AI if asked.
"""

def respond(message, history):
    # Convert Gradio history format to OpenAI format
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for human, assistant in history:
        messages.append({"role": "user", "content": human})
        messages.append({"role": "assistant", "content": assistant})
    messages.append({"role": "user", "content": message})

    # Stream the response
    stream = openai.chat.completions.create(
        model="gpt-4o", # Ensure your environment has access to this model
        messages=messages,
        stream=True,
    )
    
    partial = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            partial += chunk.choices[0].delta.content
            yield partial

# --- UI Setup ---
css = Path("style.css").read_text() if Path("style.css").exists() else ""

demo = gr.ChatInterface(
    fn=respond,
    title="Ask Parth AI",
    description="Ask about my experience, projects, and technical background.",
    theme=gr.themes.Base(primary_hue="gray", neutral_hue="gray"),
    css=css,
    examples=[
        "Tell me about Parth's backend engineering experience",
        "What distributed systems has Parth built?",
        "Explain Parth's AI projects",
    ],
    chatbot=gr.Chatbot(
        height=600, 
        show_label=False, 
        bubble_full_width=False,
        avatar_images=(None, str(FAVICON_PATH) if FAVICON_PATH.exists() else None)
    )
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))