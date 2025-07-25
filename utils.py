"""
Utility functions and tools for the LLM Alter Ego chatbot.
"""
import os
import requests
import json


def push(text):
    """Send push notification via Pushover."""
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        }
    )


def record_user_details(email, name="Name not provided", notes="not provided"):
    """Record user contact details and interest."""
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}


def record_unknown_question(question):
    """Record questions that couldn't be answered."""
    push(f"Recording unknown question: {question}")
    return {"recorded": "ok"}


def handle_tool_calls(tool_calls):
    """
    Handle tool calls from the LLM.
    Takes a list of tool calls and executes them.
    """
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"Tool called: {tool_name}", flush=True)
        
        # Get the function from the global namespace
        tool_func = globals().get(tool_name)
        result = tool_func(**arguments) if tool_func else {"error": "Tool not found"}
        
        results.append({
            "role": "tool",
            "content": json.dumps(result),
            "tool_call_id": tool_call.id
        })
    return results


# Tool definitions for OpenAI function calling
RECORD_USER_DETAILS_TOOL = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            },
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

RECORD_UNKNOWN_QUESTION_TOOL = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

# Default tools list
DEFAULT_TOOLS = [
    {"type": "function", "function": RECORD_USER_DETAILS_TOOL},
    {"type": "function", "function": RECORD_UNKNOWN_QUESTION_TOOL}
] 