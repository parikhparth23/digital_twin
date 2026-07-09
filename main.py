import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr

# Load environment variables
load_dotenv(override=True)
client = OpenAI()

BASE_DIR = Path(__file__).resolve().parent
FAVICON_PATH = BASE_DIR / "resources" / "favicon.png"

# Load data
def get_context():
    resume_path = BASE_DIR / "resources" / "resume.pdf"
    summary_path = BASE_DIR / "resources" / "summary.txt"
    
    resume = ""
    if resume_path.exists():
        reader = PdfReader(resume_path)
        resume = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    
    summary = summary_path.read_text(encoding="utf-8") if summary_path.exists() else ""
    return resume, summary

resume, summary = get_context()

SYSTEM_PROMPT = f"""
You are a digital twin of Parth Parikh. Answer questions about: Career, Engineering experience, Skills, Projects, Technical background.
Profile: {summary}
Resume: {resume}
Rules: Be professional, don't invent info, admit if you don't know, and identify as an AI digital twin if asked.
"""

def respond(message, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for human, assistant in history:
        messages.append({"role": "user", "content": human})
        messages.append({"role": "assistant", "content": assistant})
    messages.append({"role": "user", "content": message})

    stream = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        stream=True,
    )
    
    partial = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            partial += chunk.choices[0].delta.content
            yield partial

# Load CSS
css = Path("style.css").read_text() if Path("style.css").exists() else ""

# Create Interface
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
        avatar_images=(None, str(FAVICON_PATH) if FAVICON_PATH.exists() else None)
    )
)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0", 
        server_port=int(os.environ.get("PORT", 7860)),
        favicon_path=str(FAVICON_PATH) if FAVICON_PATH.exists() else None
    )