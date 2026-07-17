import chainlit as cl
from dotenv import load_dotenv

from context import USER, STARTERS
from inference import ask_digital_twin

load_dotenv()


@cl.set_starters
async def set_starters():
    return STARTERS


@cl.on_chat_start
async def start():
    await cl.Message(content=USER).send()


@cl.on_message
async def main(message: cl.Message):

    answer = ask_digital_twin(message.content)

    await cl.Message(
        content=answer
    ).send()