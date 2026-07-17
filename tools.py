import json
from dotenv import load_dotenv
import os
import requests
from rich.console import Console
from rag.retrieval import retrieve_resume

# Load environment variables before reading them
load_dotenv(override=True)
telegram_token = os.getenv("TELEGRAM_TOKEN")


def show(text):
    try:
        Console().print(text)
    except Exception:
        print(text)

checklist = []
completed = []

def get_checklist_report() -> str:
    result = ""
    for index, item in enumerate(checklist):
        if completed[index]:
            result += f"Checklist #{index + 1}: [green][strike]{item}[/strike][/green]\n"
        else:
            result += f"Checklist #{index + 1}: {item}\n"
    show(result)
    return result

def create_checklist(descriptions: list[str]) -> str:
    checklist.extend(descriptions)
    completed.extend([False] * len(descriptions))
    return get_checklist_report()

def mark_complete(index: int, completion_notes: str) -> str:
    if 1 <= index <= len(checklist):
        completed[index - 1] = True
    else:
        return "No checklist at this index."
    Console().print(completion_notes)
    return get_checklist_report()

def send_telegram_message(chat_id: str, message: str):
    if not telegram_token:
        return {"ok": False, "error": "Missing TELEGRAM_TOKEN"}

    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"ok": False, "error": str(e)}


def record_user_conversation(info: str, notes: str = ""):
    send_telegram_message(chat_id="6679381468", message=f"Recording conversation: {info} with notes: {notes}")
    return {"status": "OK"}


def record_unknown_question(question: str):
    send_telegram_message(chat_id="6679381468", message=f"Recording {question} asked that I couldn't answer")
    return {"status": "OK"}


def search_resume(query: str):
    return retrieve_resume(query)


create_checklist_json = {
    "name": "create_checklist",
    "description": "Add new checklist from a list of descriptions and return the full list",
    "parameters": {
        "type": "object",
        "properties": {
            "descriptions": {
                'type': 'array',
                'items': {'type': 'string'},
                'title': 'Descriptions of checklist items'
                }
            },
        "required": ["descriptions"],
        "additionalProperties": False
    }
}

mark_complete_json = {
    "name": "mark_complete",
    "description": "Mark complete the checklist item at the given position (starting from 1) and return the full list",
    "parameters": {
        'properties': {
            'index': {
                'description': 'The 1-based index of the checklist item to mark as complete',
                'title': 'Index',
                'type': 'integer'
                },
            'completion_notes': {
                'description': 'Notes about how you completed the checklist item in rich console markup',
                'title': 'Completion Notes',
                'type': 'string'
                }
            },
        'required': ['index', 'completion_notes'],
        'type': 'object',
        'additionalProperties': False
    }
}

record_user_conversation_json = {
    "name": "record_user_conversation",
    "description": "MANDATORY: Call this tool for every single professional question asked about Parth Parikh. This logs the question and answer for analysis.",
    "parameters": {
        "type": "object",
        "properties": {
            "info": {"type": "string", "description": "The user's question."},
            "notes": {"type": "string", "description": "The answer you provided."},
        },
        "required": ["info", "notes"],
        "additionalProperties": False,
    },
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "MANDATORY: Call this tool for every single non professional question asked. This logs the question and answer for analysis.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "The question that couldn't be answered"},
        },
        "required": ["question"],
        "additionalProperties": False,
    },
}

search_resume_json = {
    "name": "search_resume",
    "description": "Search Parth's resume and professional documents for    relevant "
        "information. Use this whenever you need information about "
        "experience, projects, skills, education, work history, "
        "technologies, achievements, certifications, or any professional details.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "A natural language search query describing the information "
                    "to retrieve from the resume."
                    "Semantic search query. Example: 'backend experience at Reddit', 'AI projects', 'work authorization', 'programming languages', 'education'."
            },
        },
        "required": ["query"],
        "additionalProperties": False,
    },
}


tools = [
    {"type": "function", "function": record_user_conversation_json},
    {"type": "function", "function": record_unknown_question_json},
    {"type": "function", "function": search_resume_json},
    {"type": "function", "function": create_checklist_json},
    {"type": "function", "function": mark_complete_json}
]


tool_map = {
    "record_user_conversation": record_user_conversation,
    "record_unknown_question": record_unknown_question,
    "search_resume": search_resume,
    "create_checklist": create_checklist,
    "mark_complete": mark_complete,
}

def handle_tool_calls(tool_call_list):
    results = []
    for tool_call in tool_call_list:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"Tool called: {tool_name}", flush=True)
        tool = tool_map.get(tool_name)
        result = tool(**arguments) if tool else {"status": "Unknown tool: " + tool_name}
        results.append({"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id})
    return results