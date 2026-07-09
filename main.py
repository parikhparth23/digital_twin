from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr
import os
from pathlib import Path

load_dotenv(override=True)
openai = OpenAI()

BASE_DIR = Path(__file__).resolve().parent
FAVICON_PATH = BASE_DIR / "resources" / "favicon.png"

# Load resume
reader = PdfReader(BASE_DIR / "resources" / "resume.pdf")
resume = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        resume += text

# Load summary
with open(BASE_DIR / "resources" / "summary.txt", "r", encoding="utf-8") as f:
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

with gr.Blocks(title="AI Digital Twin of Parth Parikh") as demo:
    gr.HTML(
        """
        <div class="hero">
            <h1>Parth Parikh</h1>
            <p>Software Engineer — ask about my experience, projects, and technical background.</p>
        </div>
        """
    )

    chatbot = gr.Chatbot(
        elem_id="chatbot",
        height=650,
        show_label=False,
        avatar_images=(None, str(FAVICON_PATH) if FAVICON_PATH.exists() else None),
    )

    with gr.Row(elem_id="input-row"):
        message = gr.Textbox(
            placeholder="Message Parth...",
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

if not FAVICON_PATH.exists():
    print(f"[warning] favicon not found at {FAVICON_PATH} — tab will use default icon")

demo.launch(
    server_name="0.0.0.0",
    server_port=int(os.environ.get("PORT", 7860)),
    favicon_path=str(FAVICON_PATH) if FAVICON_PATH.exists() else None,
    theme=gr.themes.Soft(
        primary_hue="blue",
        neutral_hue="slate",
    ),
    css=css,
)