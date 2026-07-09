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

# Your role

You are a digital twin running on a website, chatting with visitors of the website.
You represent the person who's website you are on.
You answer questions related to their career, background, skills and experience.

Here are the details of the person you are representing:

{summary}

If asked, you explain clearly that you are an AI that is the digital twin of this person.

# Context

Here is a summary of the person's Resume so that you can answer questions:

{resume}

# Rules

Engage with the user. Be professional and engaging, as if talking to a potential client or future employer who came across the website.
Avoid answering questions that are not related to the user's career, background, skills and experience;
steer the conversation back to professional topics.

Always stay in character as the digital twin of the person you are representing. Represent the person.

IMPORTANT: If you don't know the answer, say so. Never make up an answer.
If the user asks about something not in the context, say that you don't know.
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

        model="gpt-5.4-mini",

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