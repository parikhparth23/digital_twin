import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr


# Environment
load_dotenv(override=True)

client = OpenAI()


BASE_DIR = Path(__file__).resolve().parent

FAVICON_PATH = BASE_DIR / "resources" / "favicon.png"


# Load resume and summary
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
        summary = summary_path.read_text(
            encoding="utf-8"
        )


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
- Do not make up information.
- If you do not know something, say so.
- If asked who you are, explain you are an AI digital twin representing Parth Parikh.
"""



# Chat function
def respond(message, history):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]


    # New Gradio message format
    for item in history:

        if item["role"] == "user":

            messages.append(
                {
                    "role": "user",
                    "content": item["content"]
                }
            )


        elif item["role"] == "assistant":

            messages.append(
                {
                    "role": "assistant",
                    "content": item["content"]
                }
            )



    messages.append(
        {
            "role": "user",
            "content": message
        }
    )



    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        stream=True
    )



    output = ""

    for chunk in response:

        if chunk.choices[0].delta.content:

            output += chunk.choices[0].delta.content

            yield output





# CSS
css_path = BASE_DIR / "style.css"

css = ""

if css_path.exists():
    css = css_path.read_text()



# App
demo = gr.ChatInterface(

    fn=respond,

    title="Ask Parth AI",

    description=(
        "Ask about my experience, projects, "
        "and technical background."
    ),

    css=css,


    examples=[
        "Tell me about Parth's backend engineering experience",
        "What distributed systems has Parth built?",
        "Explain Parth's AI projects",
    ],


    chatbot=gr.Chatbot(

        height=600,

        show_label=False,

        type="messages",

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
        ),

        favicon_path=(
            str(FAVICON_PATH)
            if FAVICON_PATH.exists()
            else None
        )
    )