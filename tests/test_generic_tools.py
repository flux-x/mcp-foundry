import uuid
from unittest.mock import AsyncMock, patch

import pytest

from mcp_foundry.mcp_runtime.server_factory import build_mcp_app
from mcp_foundry.models.mcp_server import McpServer


@pytest.mark.asyncio
async def test_build_mcp_app_generic_tools():
    server = McpServer(
        id=uuid.uuid4(),
        name="Test Tools Server",
        tools_config=[
            {
                "name": "send_email",
                "description": "Sends an email",
                "webhook_url": "http://127.0.0.1:8001/send-email",
                "parameters": {
                    "properties": {
                        "to": {"type": "string", "description": "Email address"},
                        "subject": {"type": "string"},
                    },
                    "required": ["to", "subject"],
                },
            }
        ],
    )

    app = build_mcp_app(server, None)

    tools = await app.list_tools()
    assert len(tools) == 1
    assert tools[0].name == "send_email"
    assert tools[0].description == "Sends an email"


@pytest.mark.asyncio
async def test_invoke_generic_tool():
    server = McpServer(
        id=uuid.uuid4(),
        name="Test Tools Server",
        tools_config=[
            {
                "name": "send_email",
                "description": "Sends an email",
                "webhook_url": "http://127.0.0.1:8001/send-email",
                "parameters": {
                    "properties": {
                        "to": {"type": "string"},
                        "subject": {"type": "string"},
                    },
                    "required": ["to", "subject"],
                },
            }
        ],
    )

    app = build_mcp_app(server, None)

    tool_callable = None
    for tool_name, wrapper in app._tool_manager._tools.items():
        if tool_name == "send_email":
            tool_callable = wrapper.fn
            break

    assert tool_callable is not None, "Tool was not registered correctly"

    mock_response = AsyncMock()
    mock_response.text = '{"status": "success"}'
    mock_response.raise_for_status = AsyncMock()

    with patch("httpx.AsyncClient.post", return_value=mock_response) as mock_post:
        result = await tool_callable(to="test@example.com", subject="Hello")

        assert mock_post.called
        assert mock_post.call_args[0][0] == "http://127.0.0.1:8001/send-email"
        assert mock_post.call_args[1]["json"] == {"to": "test@example.com", "subject": "Hello"}
        assert result == '{"status": "success"}'
