from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr
import os
from pathlib import Path

load_dotenv(override=True)
openai = OpenAI()

# Load resume
reader = PdfReader("resources/resume.pdf")
resume = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        resume += text

# Load summary
with open("resources/summary.txt", "r", encoding="utf-8") as f:
    summary = f.read()

system_prompt = f"""
You are a digital twin of Parth Parikh.
You answer questions about:
- Career
- Engineering experience
- Skills
- Projects
- Technical background
You represent Parth professionally when talking to recruiters,
clients, and engineers.
Profile information:
{summary}
Resume:
{resume}
Rules:
- Stay focused on professional topics.
- Do not invent information.
- If you don't know something, say so.
- If asked, explain you are an AI digital twin.
"""


def chat_stream(message, history):
    """Yields partial assistant text as it streams in from the model."""
    messages = [{"role": "system", "content": system_prompt}]
    for user_msg, assistant_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": assistant_msg})
    messages.append({"role": "user", "content": message})

    stream = openai.chat.completions.create(
        model="gpt-5.4-mini",
        messages=messages,
        stream=True,
    )

    partial = ""
    for chunk in stream:
        delta = chunk.choices[0].delta.content or ""
        if delta:
            partial += delta
            yield partial


css_path = Path("style.css")
css = css_path.read_text() if css_path.exists() else ""

with gr.Blocks(
    title="Parth Parikh AI",
    theme=gr.themes.Soft(
        primary_hue="blue",
        neutral_hue="slate",
    ),
    css=css,
) as demo:
    gr.HTML(
        """
        <div class="hero">
            <div class="hero-avatar">PP</div>
            <h1>Parth Parikh</h1>
            <p>AI Digital Twin — ask about my career, engineering experience, projects, and technical background.</p>
        </div>
        """
    )

    chatbot = gr.Chatbot(
        elem_id="chatbot",
        height=650,
        show_label=False,
        avatar_images=(None, "resources/favicon.png"),
        bubble_full_width=False,
    )

    with gr.Row(elem_id="input-row"):
        message = gr.Textbox(
            placeholder="Message Parth AI...",
            show_label=False,
            container=False,
            scale=8,
        )
        send = gr.Button("Send", variant="primary", scale=1)

    gr.Examples(
        examples=[
            "Tell me about Parth's backend engineering experience",
            "What distributed systems has Parth built?",
            "Explain Parth's AI projects",
            "What technologies does Parth specialize in?",
        ],
        inputs=message,
    )

    def user_turn(msg, history):
        # Immediately show the user's message, clear the box, add an empty bot slot
        history = history + [(msg, "")]
        return "", history

    def bot_turn(history):
        user_msg = history[-1][0]
        prior_history = history[:-1]
        for partial in chat_stream(user_msg, prior_history):
            history[-1] = (user_msg, partial)
            yield history

    send.click(
        user_turn, inputs=[message, chatbot], outputs=[message, chatbot]
    ).then(
        bot_turn, inputs=chatbot, outputs=chatbot
    )

    message.submit(
        user_turn, inputs=[message, chatbot], outputs=[message, chatbot]
    ).then(
        bot_turn, inputs=chatbot, outputs=chatbot
    )

demo.launch(
    server_name="0.0.0.0",
    server_port=int(os.environ.get("PORT", 7860)),
    favicon_path="resources/favicon.png",
)