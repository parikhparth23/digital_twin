from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr
import os
from pathlib import Path


# Load environment
load_dotenv(override=True)

openai = OpenAI()


# Read resume
reader = PdfReader("resources/resume.pdf")

resume = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        resume += text


# Read summary
with open("resources/summary.txt", "r", encoding="utf-8") as f:
    summary = f.read()


system_prompt = f"""
# Your role

You are a digital twin running on a website.
You represent Parth Parikh.

You answer questions related to Parth's:
- career
- background
- skills
- experience
- projects
- technical expertise

Here are the details of the person you represent:

{summary}


Resume context:

{resume}


# Rules

- Be professional and engaging.
- Answer as if talking to a recruiter, client, or engineer visiting the website.
- Stay focused on career and professional topics.
- If asked, clearly explain that you are an AI digital twin.
- Never invent information.
- If you don't know something, say you don't know.
"""


def chat(message, history):
    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    messages.extend(history)

    messages.append(
        {
            "role": "user",
            "content": message
        }
    )

    response = openai.chat.completions.create(
        model="gpt-5.4-mini",
        messages=messages
    )

    return response.choices[0].message.content


# Load custom CSS
css_file = Path("style.css")

css = css_file.read_text() if css_file.exists() else ""


with gr.Blocks(
    title="Parth Parikh AI",
    theme=gr.themes.Base(
        primary_hue="blue",
        neutral_hue="slate"
    ),
    css=css
) as demo:


    # Header
    gr.Markdown(
        """
        <div class="header">

        <h1>🤖 Parth Parikh AI</h1>

        <p>
        Ask me about Parth's career, engineering experience,
        projects, and technical background.
        </p>

        </div>
        """
    )


    # Chat window
    gr.ChatInterface(
        fn=chat,
        chatbot=gr.Chatbot(
            height=650,
            show_label=False,
            avatar_images=(
                None,
                "resources/favicon.png"
            )
        ),
        textbox=gr.Textbox(
            placeholder="Message Parth AI...",
            container=False,
            scale=7
        ),
        examples=[
            "Tell me about Parth's backend engineering experience",
            "What distributed systems has Parth built?",
            "What technologies does Parth specialize in?",
            "Explain Parth's AI projects"
        ]
    )


demo.launch(
    server_name="0.0.0.0",
    server_port=int(os.environ.get("PORT", 7860)),
    favicon_path="resources/favicon.png",
)