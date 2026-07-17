from openai import OpenAI

from context import SYSTEM
from tools import tools, handle_tool_calls

client = OpenAI()

MODEL_NAME = "gpt-5.4-mini"


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
            
            return assistant.content

        # Add assistant tool request.
        messages.append(assistant)

        # Execute tool(s).
        tool_results = handle_tool_calls(assistant.tool_calls)

        # Add tool outputs.
        messages.extend(tool_results)
