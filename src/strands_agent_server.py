import logging
import os
from contextlib import asynccontextmanager
from contextvars import ContextVar
from typing import Optional, List

import httpx
import uvicorn
from fastapi import FastAPI, Request
from mcp.client.streamable_http import streamable_http_client
from strands.tools.mcp import MCPClient
from strands.multiagent.a2a import A2AServer
from strands import Agent

# Import config
import config

logging.basicConfig(level=logging.INFO)

# Environment variables
runtime_url = os.environ.get("AGENTCORE_RUNTIME_URL", "http://127.0.0.1:9000/")
calculator_mcp_url = os.environ.get(
    "CALCULATOR_MCP_URL",
    "https://bedrock-agentcore.ap-southeast-1.amazonaws.com/runtimes/arn%3Aaws%3Abedrock-agentcore%3Aap-southeast-1%3A975050162743%3Aruntime%2Fcalculator_mcp-T3sYhKFsEy/invocations?qualifier=DEFAULT",
)

logging.info(f"Runtime URL: {runtime_url}")
logging.info(f"Calculator MCP URL: {calculator_mcp_url}")

host, port = "0.0.0.0", 9000

# Context variable để lưu token từ request hiện tại
current_auth_token: ContextVar[Optional[str]] = ContextVar(
    "current_auth_token", default=None
)


class LazyToolsAgent:
    """Agent wrapper that loads MCP tools lazily on first request"""

    def __init__(self, mcp_url: str, is_local: bool = False):
        self.mcp_url = mcp_url
        self.is_local = is_local
        self._mcp_client: Optional[MCPClient] = None
        self._http_client: Optional[httpx.AsyncClient] = None
        self._tools: List = []
        self._initialized = False

        self._agent = Agent(
            name="Calculator Agent",
            description="A calculator agent that can perform basic arithmetic operations using MCP tools.",
            tools=[],
        )

    def _create_http_client(self, token: Optional[str] = None) -> httpx.AsyncClient:
        headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
        }

        if token:
            headers["Authorization"] = f"Bearer {token}"

        return httpx.AsyncClient(timeout=120, headers=headers)

    def _create_mcp_client(self, token: Optional[str] = None) -> MCPClient:
        captured_token = token

        def transport_factory():
            http_client = self._create_http_client(captured_token)
            return streamable_http_client(url=self.mcp_url, http_client=http_client)

        return MCPClient(transport_factory)

    def set_initialized(self, status: bool):
        self._initialized = status

    def initialize(self, token: Optional[str] = None):
        """
        Initialize MCP connection.
        - Local mode: không cần token
        - Server mode: forward token từ request
        """
        if self._initialized and self.is_local:
            return

        try:
            if self._mcp_client:
                try:
                    self._mcp_client.stop()
                except Exception:
                    pass

            logging.debug(f"Auth Token: {token}")

            self._mcp_client = self._create_mcp_client(token)
            self._mcp_client.start()

            # Load tools
            self._tools = self._mcp_client.list_tools_sync()
            logging.info(f"Loaded {len(self._tools)} tools from MCP server")

            self._agent = Agent(
                name="Calculator Agent",
                description="A calculator agent that can perform basic arithmetic operations using MCP tools.",
                tools=self._tools,
            )

            self._initialized = True

        except Exception as e:
            logging.error(f"Failed to initialize MCP: {e}")
            raise

    @property
    def agent(self) -> Agent:
        return self._agent

    def cleanup(self):
        if self._mcp_client:
            self._mcp_client.stop()


is_local_mode = config.local == "1"

# Global lazy agent
lazy_agent = LazyToolsAgent(calculator_mcp_url, is_local=is_local_mode)

# Placeholder cho a2a_server - sẽ được khởi tạo trong lifespan
a2a_server: Optional[A2AServer] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global a2a_server

    logging.info("A2A Server starting...")
    logging.info(f"Mode: {'LOCAL' if is_local_mode else 'SERVER'}")

    if is_local_mode:
        lazy_agent.initialize()
        logging.info("Initialized MCP tools for local mode (no auth)")
    else:
        logging.info(
            "Server mode: MCP will be initialized with auth token from first request"
        )

    a2a_server = A2AServer(
        agent=lazy_agent.agent,
        http_url=runtime_url,
        serve_at_root=True,
    )

    app.mount("/", a2a_server.to_fastapi_app())
    logging.info(f"A2A Server mounted with {len(lazy_agent._tools)} tools")

    yield
    lazy_agent.cleanup()
    logging.info("Server stopped")


app = FastAPI(lifespan=lifespan)


@app.get("/ping")
def ping():
    return {"status": "healthy"}


@app.middleware("http")
async def inject_token_to_mcp(request: Request, call_next):
    """
    Middleware để forward Authorization header từ A2A request sang MCP server.
    Chỉ hoạt động trong server mode.
    """
    global a2a_server

    if is_local_mode:
        return await call_next(request)

    skip_paths = ["/.well-known/agent-card.json", "/ping"]
    if any(path in request.url.path for path in skip_paths):
        return await call_next(request)

    auth_header = request.headers.get("Authorization", "")

    logging.debug(f"Auth Header: {auth_header}")

    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        try:
            lazy_agent.set_initialized(False)
            a2a_server = lazy_agent.initialize(token)
            logging.debug(f"MCP initialized with token for request: {request.url.path}")
        except Exception as e:
            logging.error(f"Failed to initialize MCP with token: {e}")

    return await call_next(request)


if __name__ == "__main__":
    uvicorn.run(app, host=host, port=port)
