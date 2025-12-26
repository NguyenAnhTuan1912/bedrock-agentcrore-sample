import os

from dotenv import load_dotenv

load_dotenv()

aws_cli_profile = os.environ.get("AWS_PROFILE", "default")
aws_region = os.environ.get("AWS_REGION", "ap-southeast-1")
mcp_agent_arn = os.environ.get("MCP_AGENT_ARN", "")
agent_arn = os.environ.get("AGENT_ARN", "")
bearer_token = os.environ.get("BEARER_TOKEN", "")
agentcore_runtime_url = os.environ.get("AGENTCORE_RUNTIME_URL", "")
local = os.environ.get("LOCAL", "0")
