from strands import Agent

from typing import Any


def create_calculator_strands_agent(tools: list[Any]):
    """Create a calculator strands agent.

    Args:
        tools (list[Any]): list of tools.

    Returns:
        Agent: strands agent.
    """
    agent = Agent(
        name="Calculator Agent",
        description="A calculator agent that can perform basic arithmetic operations.",
        tools=[tools],
        callback_handler=None,
    )

    return agent
