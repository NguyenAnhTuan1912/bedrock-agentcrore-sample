import asyncio
import logging
import os
import sys
from uuid import uuid4


import httpx
from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
from a2a.types import Message, Part, Role, TextPart

ROOT_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, "..")))
sys.path.insert(0, os.path.join(ROOT_DIR, "src"))

import config as script_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 300  # set request timeout to 5 minutes


def create_message(*, role: Role = Role.user, text: str) -> Message:
    return Message(
        kind="message",
        role=role,
        parts=[Part(TextPart(kind="text", text=text))],
        message_id=uuid4().hex,
    )


async def send_sync_message(message: str):
    # Get runtime URL from environment variable
    aws_region = script_config.aws_region
    agent_arn = script_config.agent_arn
    bearer_token = script_config.bearer_token
    agentcore_runtime_url = script_config.agentcore_runtime_url

    # Generate a unique session ID
    session_id = str(uuid4())
    print(f"Generated session ID: {session_id}")

    # Add authentication headers for Amazon Bedrock AgentCore
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": session_id,
    }

    async with httpx.AsyncClient(
        timeout=DEFAULT_TIMEOUT, headers=headers
    ) as httpx_client:
        # Get agent card from the runtime URL
        resolver = A2ACardResolver(
            httpx_client=httpx_client, base_url=agentcore_runtime_url
        )
        agent_card = await resolver.get_agent_card()

        # Agent card contains the correct URL (same as runtime_url in this case)
        # No manual override needed - this is the path-based mounting pattern

        # Create client using factory
        config = ClientConfig(
            httpx_client=httpx_client,
            streaming=False,  # Use non-streaming mode for sync response
        )
        factory = ClientFactory(config)
        client = factory.create(agent_card)

        # Create and send message
        msg = create_message(text=message)

        # With streaming=False, this will yield exactly one result
        async for event in client.send_message(msg):
            if isinstance(event, Message):
                logger.info(event.model_dump_json(exclude_none=True, indent=2))
                return event
            elif isinstance(event, tuple) and len(event) == 2:
                # (Task, UpdateEvent) tuple
                task, update_event = event
                logger.info(
                    f"Task: {task.model_dump_json(exclude_none=True, indent=2)}"
                )
                if update_event:
                    logger.info(
                        f"Update: {update_event.model_dump_json(exclude_none=True, indent=2)}"
                    )
                return task
            else:
                # Fallback for other response types
                logger.info(f"Response: {str(event)}")
                return event


# Usage - Uses AGENTCORE_RUNTIME_URL environment variable
asyncio.run(send_sync_message("what is 101 * 11"))
