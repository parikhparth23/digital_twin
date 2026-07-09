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
                resume += text


    summary = ""

    summary_file = BASE_DIR / "resources" / "summary.txt"

    if summary_file.exists():
        summary = summary_file.read_text()


    return resume, summary



resume, summary = load_context()



SYSTEM = f"""
You are Parth Parikh's AI digital twin.

Profile:
{summary}

Resume:
{resume}

Rules:
- Do not hallucinate.
- Answer professionally.
"""



@cl.on_message
async def main(message: cl.Message):

    response = cl.Message(content="")

    await response.send()


    stream = client.chat.completions.create(

        model="gpt-4o",

        messages=[
            {
                "role":"system",
                "content":SYSTEM
            },
            {
                "role":"user",
                "content":message.content
            }
        ],

        stream=True
    )


    for chunk in stream:

        token = chunk.choices[0].delta.content

        if token:
            await response.stream_token(token)


    await response.update()