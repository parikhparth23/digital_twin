import os
from pathlib import Path

import chainlit as cl
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader


load_dotenv()

client = OpenAI()

BASE_DIR = Path(__file__).parent


def load_context():

    resume = ""

    pdf = BASE_DIR / "resources" / "resume.pdf"

    if pdf.exists():

        reader = PdfReader(pdf)

        for page in reader.pages:

            text = page.extract_text()

            if text:
                resume += text + "\n"


    summary = ""

    summary_file = BASE_DIR / "resources" / "summary.txt"

    if summary_file.exists():

        summary = summary_file.read_text(
            encoding="utf-8"
        )


    return resume, summary



resume, summary = load_context()



SYSTEM = f"""
You are Parth Parikh's AI digital twin.

Answer questions about:
- Career
- Backend engineering
- Distributed systems
- Cloud architecture
- AI projects
- Technical background

Profile:
{summary}

Resume:
{resume}

Rules:
- Do not hallucinate.
- Do not invent experience.
- If information is unavailable, say so.
- Reply in the same language as the user.
"""



@cl.set_starters
async def set_starters():

    return [

        cl.Starter(
            label="Backend Engineering Experience",
            message="Tell me about Parth's backend engineering experience"
        ),

        cl.Starter(
            label="Distributed Systems",
            message="What distributed systems has Parth built?"
        ),

        cl.Starter(
            label="AI Projects",
            message="Explain Parth's AI projects"
        ),

    ]



@cl.on_chat_start
async def start():

    await cl.Message(
        content="""
# 👋 Ask Parth AI

Ask about my experience, projects, and technical background.

You can ask about:

- Tell me about yourself
- What technologies does Parth work with?
- What distributed systems has Parth built?
- Explain Parth's AI experience
"""
    ).send()



@cl.on_message
async def main(message: cl.Message):

    response = cl.Message(
        content=""
    )

    await response.send()


    stream = client.chat.completions.create(

        model="gpt-4o",

        messages=[
            {
                "role": "system",
                "content": SYSTEM
            },
            {
                "role": "user",
                "content": message.content
            }
        ],

        stream=True
    )


    for chunk in stream:

        token = chunk.choices[0].delta.content

        if token:

            await response.stream_token(token)


    await response.update()