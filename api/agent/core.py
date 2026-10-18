import json
import asyncio
import datetime
import logging
import functools
from openai import OpenAI
from .models import IncomingMessage, AgentResponse
from .prompts import SYSTEM_PROMPT
from .tools import TOOLS
from .memory_store import save_memory, search_memory
from .reminder import create_reminder

logger = logging.getLogger(__name__)

# Synchronous OpenAI client — all calls are offloaded to a thread via run_in_executor
client = OpenAI()


def _call_llm(messages: list) -> object:
    """
    First LLM call (with tools). Runs synchronously — must be called via run_in_executor.
    """
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS
    )


def _call_llm_parse(messages: list) -> object:
    """
    Final structured LLM call. Runs synchronously — must be called via run_in_executor.
    """
    return client.chat.completions.parse(
        model="gpt-4o-mini",
        messages=messages,
        response_format=AgentResponse
    )


def _run_tool(name: str, args: dict) -> str:
    """
    Dispatches a tool call synchronously — must be called via run_in_executor
    since save_memory / search_memory both do blocking network I/O (OpenAI + Qdrant).
    """
    if name == "save_memory":
        return save_memory(
            memory_type=args.get("memory_type"),
            content=args.get("content"),
            metadata=args.get("metadata")
        )
    elif name == "search_memory":
        return search_memory(
            query=args.get("query"),
            memory_type=args.get("memory_type")
        )
    elif name == "create_reminder":
        return create_reminder(
            message=args.get("message"),
            due_at=args.get("due_at")
        )
    else:
        return f"Unknown tool: {name}"


async def process_message(message: IncomingMessage) -> str:
    """
    Main entry point for handling incoming messages from the FastAPI app.
    All blocking SDK calls (OpenAI + Qdrant) are offloaded to a thread pool
    via run_in_executor so the asyncio event loop is never blocked.
    """
    loop = asyncio.get_event_loop()
    current_time = datetime.datetime.now().astimezone().isoformat(timespec='seconds')

    # Format incoming message context into a user prompt
    if message.type == "text":
        user_content = message.caption or ""
    else:
        parts = [f"Type: {message.type}"]
        if message.path:
            parts.append(f"File Path: {message.path}")
        if message.caption:
            parts.append(f"Caption: {message.caption}")
        user_content = "\n".join(parts)
        print("\n\nuser content", user_content)

    user_content_with_time = f"Current Time: {current_time}\nUser Message: {user_content}"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content_with_time}
    ]

    try:
        # --- First LLM call (non-blocking) ---
        response = await loop.run_in_executor(
            None, functools.partial(_call_llm, messages)
        )

        assistant_msg = response.choices[0].message
        messages.append(assistant_msg)
        print("\n\nassistant msg", assistant_msg)

        if not assistant_msg.tool_calls:
            return {
                "type": "text",
                "message": assistant_msg.content or "",
                "path": None
            }

        # --- Tool calls (each offloaded to executor since they're blocking) ---
        for tool_call in assistant_msg.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            result = await loop.run_in_executor(
                None, functools.partial(_run_tool, name, args)
            )

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

        # --- Final structured LLM call (non-blocking) ---
        final_response = await loop.run_in_executor(
            None, functools.partial(_call_llm_parse, messages)
        )
        parsed_response = final_response.choices[0].message.parsed
        print("final response", parsed_response)
        return parsed_response or ""

    except Exception as e:
        logger.exception("Error processing message")
        return "Something went wrong while processing your request."
