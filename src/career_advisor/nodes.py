"""Graph node definitions for Career Transition Advisor."""

from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langchain_core.messages import SystemMessage

from .config import config
from .prompts import CAREER_ADVISOR_SYSTEM_PROMPT


def create_llm() -> ChatOpenAI:
    """
    Create and configure the LLM instance.

    Returns:
        ChatOpenAI: Configured LLM client pointing to RunPod vLLM endpoint
    """
    return ChatOpenAI(
        api_key=config.RUNPOD_API_KEY,
        base_url=config.RUNPOD_ENDPOINT_URL,
        model=config.MODEL_NAME,
        max_completion_tokens=config.MAX_COMPLETION_TOKENS,
        temperature=config.TEMPERATURE,
    )


def create_call_model_node(llm_with_tools):
    """
    Factory function to create the call_model node.

    Args:
        llm_with_tools: LLM instance with tools bound

    Returns:
        Async function that processes messages with context awareness
    """
    async def call_model(state: MessagesState):
        """
        Career Advisor agent node that processes messages with context awareness.

        - Maintains conversation history for personalized career guidance
        - Uses async invocation for better performance with web research tools
        - Automatically includes system prompt for consistent career advisor behavior
        """
        messages = state["messages"]

        # Add system prompt if this is the first message in the conversation
        if not messages or messages[0].type != "system":
            messages = [SystemMessage(content=CAREER_ADVISOR_SYSTEM_PROMPT)] + messages

        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    return call_model
