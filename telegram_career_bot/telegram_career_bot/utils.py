"""Small shared helpers used by graph nodes and agents."""

from typing import List

from langchain_core.messages import BaseMessage, HumanMessage


def get_last_human_message(messages: List[BaseMessage]) -> str:
    """Return the text of the most recent HumanMessage in a message list."""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            return msg.content
    return ""
