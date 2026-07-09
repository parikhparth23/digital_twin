import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr


load_dotenv(override=True)

client = OpenAI()


BASE_DIR = Path(__file__).resolve().parent
FAVICON_PATH = BASE_DIR / "resources" / "favicon.png"


def get_context():

    resume_path = BASE_DIR / "resources" / "resume.pdf"
    summary_path = BASE_DIR / "resources" / "summary.txt"

    resume = ""

    if resume_path.exists():
        reader = PdfReader(resume_path)

        for page in reader.pages:
            text = page.extract_text()

            if text:
                resume += text + "\n"


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
- Projects
- Technical skills
- System design experience

Profile:
{summary}

Resume:
{resume}

Rules:
- Do not invent information.
- Be concise and professional.
- Say you don't know if information is unavailable.
"""



def respond(message, history):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]


    for user, assistant in history:

        messages.append(
            {
                "role": "user",
                "content": user
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
        stream=True
    )


    output = ""

    for chunk in stream:

        if chunk.choices[0].delta.content:

            output += chunk.choices[0].delta.content

            yield output



css = """
body {
    background: #212121 !important;
}


.gradio-container {
    max-width: 1100px !important;
    margin: auto !important;
}


/* Main app */

#chatbox {
    height: calc(100vh - 180px);
}



/* Chat window */

.chatbot {

    border-radius: 12px !important;

}



/* Input */

textarea {

    font-size: 16px !important;

}



footer {
    display:none !important;
}
"""



with gr.Blocks(
    css=css,
    title="Ask Parth AI"
) as demo:


    gr.Markdown(
        """
        # Ask Parth AI

        AI digital twin trained on Parth's engineering background,
        projects, and experience.
        """
    )


    chatbot = gr.Chatbot(
        elem_id="chatbox",
        height=650,
        show_label=False
    )


    msg = gr.Textbox(
        placeholder="Ask about Parth's experience...",
        show_label=False,
        scale=7,
        container=False
    )


    clear = gr.Button(
        "Clear"
    )


    def chat(message, history):

        response = ""

        for token in respond(message, history):
            response = token

            yield "", history + [
                [
                    message,
                    response
                ]
            ]



    msg.submit(
        chat,
        inputs=[
            msg,
            chatbot
        ],
        outputs=[
            msg,
            chatbot
        ]
    )


    clear.click(
        lambda: [],
        outputs=chatbot
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