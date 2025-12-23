import logging

from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse

logging.basicConfig(level=logging.INFO)

mcp = FastMCP(host="0.0.0.0", stateless_http=True)


@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    logging.info("Call add_numbers function")
    return a + b


@mcp.tool()
def multiply_numbers(a: int, b: int) -> int:
    """Multiply two numbers together"""
    logging.info("Call multiply_numbers function")
    return a * b


@mcp.tool()
def subtract_numbers(a: int, b: int) -> str:
    """Subtract two numbers"""
    logging.info("Call subtract_numbers function")
    return a - b


@mcp.tool()
def divide_numbers(a: int, b: int) -> str:
    """Divide two numbers"""
    logging.info("Call divide_numbers function")
    return a / b


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
