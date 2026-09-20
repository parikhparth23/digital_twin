from openai import OpenAI
from google import genai
import os

from context import SYSTEM
from tools import tools, handle_tool_calls

# client = OpenAI()

# MODEL_NAME = "gpt-5.4-mini"
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
# client = genai.Client(
#     api_key=os.getenv("GEMINI_API_KEY")
# )

MODEL_NAME = "gemini-3.1-flash-lite"

def ask_digital_twin(question: str):

    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": question},
    ]

    while True:

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=tools,
        )

        assistant = response.choices[0].message
        # If the model has finished, return the answer.
        if not assistant.tool_calls:
            content = assistant.content
            if content is None:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                )
                content = response.choices[0].message.content
            return content or "I don't have enough information to answer that."

        # Add assistant tool request.
        messages.append(assistant)

        # Execute tool(s).
        tool_results = handle_tool_calls(assistant.tool_calls)

        # Add tool outputs.
        messages.extend(tool_results)
