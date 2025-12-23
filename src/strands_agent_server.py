import logging
import os
from contextlib import asynccontextmanager

# Import config
import config

import uvicorn
from fastapi import FastAPI
from mcp.client.streamable_http import streamable_http_client
from strands.tools.mcp import MCPClient
from strands.multiagent.a2a import A2AServer

# Import agents
from agents import create_calculator_strands_agent

logging.basicConfig(level=logging.INFO)

runtime_url = os.environ.get("AGENTCORE_RUNTIME_URL", "http://127.0.0.1:9000/")
calculator_mcp_url = os.environ.get("CALCULATOR_MCP_URL", "http://127.0.0.1:8000")

logging.info(f"Runtime URL: {runtime_url}")
logging.info(f"Calculator MCP URL: {calculator_mcp_url}")

mcp_client = MCPClient(lambda: streamable_http_client(url=f"{calculator_mcp_url}/mcp/"))

host, port = "0.0.0.0", 9000


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    mcp_client.start()
    tools = mcp_client.list_tools_sync()

    logging.info(f"Loaded {len(tools)} tools from MCP server")
    for tool in tools:
        logging.info(f"  - {tool}")

    agent = create_calculator_strands_agent(tools)

    a2a_server = A2AServer(
        agent=agent,
        http_url=runtime_url,
        serve_at_root=True,
    )
    app.mount("/", a2a_server.to_fastapi_app())

    yield  # App đang chạy

    # Shutdown
    mcp_client.stop()
    logging.info("MCP client stopped")


app = FastAPI(lifespan=lifespan)


@app.get("/ping")
def ping():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host=host, port=port)
