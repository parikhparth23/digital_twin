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


# Load resume + summary
def get_context():
    resume_path = BASE_DIR / "resources" / "resume.pdf"
    summary_path = BASE_DIR / "resources" / "summary.txt"

    resume = ""

    if resume_path.exists():
        reader = PdfReader(resume_path)
        pages = []

        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)

        resume = "\n".join(pages)

    summary = ""

    if summary_path.exists():
        summary = summary_path.read_text(encoding="utf-8")

    return resume, summary


resume, summary = get_context()


SYSTEM_PROMPT = f"""
You are a digital twin of Parth Parikh.

Answer questions about:
- Career
- Engineering experience
- Skills
- Projects
- Technical background

Profile:
{summary}

Resume:
{resume}

Rules:
- Be professional.
- Do not invent information.
- If information is unavailable, say you don't know.
- If asked who you are, explain you are an AI digital twin representing Parth Parikh.
"""


def respond(message, history):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    for human, assistant in history:
        messages.append(
            {
                "role": "user",
                "content": human
            }
        )

        messages.append(
            {
                "role": "assistant",
                "content": assistant
            }
        )

    messages.append(
        {
            "role": "user",
            "content": message
        }
    )


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
css_path = BASE_DIR / "style.css"

css = ""

if css_path.exists():
    css = css_path.read_text()



# UI
with gr.Blocks(
    theme=gr.themes.Base(
        primary_hue="gray",
        neutral_hue="gray"
    ),
    css=css,
    title="Ask Parth AI"
) as demo:


    # favicon
    if FAVICON_PATH.exists():
        gr.HTML(
            f"""
            <link rel="icon" type="image/png" href="/file={FAVICON_PATH}">
            """
        )


    gr.ChatInterface(
        fn=respond,

        title="Ask Parth AI",

        description=(
            "Ask about my experience, projects, "
            "and technical background."
        ),

        examples=[
            "Tell me about Parth's backend engineering experience",
            "What distributed systems has Parth built?",
            "Explain Parth's AI projects",
        ],

        chatbot=gr.Chatbot(
            height=600,
            show_label=False,
            avatar_images=(
                None,
                str(FAVICON_PATH)
                if FAVICON_PATH.exists()
                else None
            )
        )
    )



if __name__ == "__main__":

    demo.launch(
        server_name="0.0.0.0",
        server_port=int(
            os.environ.get(
                "PORT",
                7860
            )
        )
    )