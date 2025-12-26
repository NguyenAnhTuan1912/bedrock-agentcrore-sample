import asyncio
import os
import sys
import traceback
import httpx

ROOT_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, "..")))
sys.path.insert(0, os.path.join(ROOT_DIR, "src"))

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

import config


async def main():
    try:
        aws_region = config.aws_region
        agent_arn = config.mcp_agent_arn
        bearer_token = config.bearer_token
        if not agent_arn or not bearer_token:
            print("Error: AGENT_ARN or BEARER_TOKEN environment variable is not set")
            sys.exit(1)

        encoded_arn = agent_arn.replace(":", "%3A").replace("/", "%2F")
        mcp_url = f"https://bedrock-agentcore.{aws_region}.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"
        headers = {
            "Authorization": f"Bearer {bearer_token}",
        }
        print(f"Invoking: {mcp_url}\n")

        # Tạo httpx client với headers
        async with httpx.AsyncClient(headers=headers, timeout=120) as http_client:
            async with streamable_http_client(mcp_url, http_client=http_client) as (
                read_stream,
                write_stream,
                _,
            ):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    tool_result = await session.list_tools()
                    print(tool_result)
    except ExceptionGroup as eg:
        print(f"Caught {len(eg.exceptions)} exception(s):")
        for i, exc in enumerate(eg.exceptions, 1):
            print(f"\n--- Exception {i} ---")
            traceback.print_exception(type(exc), exc, exc.__traceback__)
    except Exception as e:
        if hasattr(e, "exceptions"):
            for i, exc in enumerate(e.exceptions, 1):
                print(f"\n--- Sub-exception {i} ---")
                traceback.print_exception(type(exc), exc, exc.__traceback__)
        else:
            traceback.print_exc()


asyncio.run(main())
