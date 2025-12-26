import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def main():
    """Khi gọi xong hàm này thì kết quả trả về sẽ là thông tin của
    các tools đang có trong MCP.
    """
    mcp_url = "http://localhost:8000/mcp"

    async with streamable_http_client(mcp_url) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tool_result = await session.list_tools()
            print(tool_result)


asyncio.run(main())
