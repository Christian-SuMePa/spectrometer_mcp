from __future__ import annotations

import pytest

import spectrometer_mcp.server as server_module
from spectrometer_mcp.server import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    ServerConfig,
    _fastmcp_init_kwargs,
    apply_server_config,
    create_mcp_server,
    get_server_config_from_env,
    register_tools,
    run_server,
)


class DummySettings:
    pass


class DummyServer:
    def __init__(self) -> None:
        self.settings = DummySettings()
        self.run_calls: list[dict[str, object]] = []
        self.registered: list[str] = []

    def tool(self):
        def decorator(func):
            self.registered.append(func.__name__)
            return func
        return decorator

    def run(self, **kwargs: object) -> None:
        self.run_calls.append(kwargs)


@pytest.fixture(autouse=True)
def clear_server_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ["MCP_TRANSPORT", "MCP_HOST", "MCP_PORT", "MCP_MOUNT_PATH"]:
        monkeypatch.delenv(key, raising=False)


def test_server_config_defaults_to_streamable_http() -> None:
    config = get_server_config_from_env()

    assert config == ServerConfig(
        transport="streamable-http",
        host=DEFAULT_HOST,
        port=DEFAULT_PORT,
        mount_path="/mcp",
    )
    assert config.connector_path == "/mcp/"


def test_server_config_uses_sse_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MCP_TRANSPORT", "sse")

    config = get_server_config_from_env()

    assert config == ServerConfig(
        transport="sse",
        host=DEFAULT_HOST,
        port=DEFAULT_PORT,
        mount_path="/sse",
    )
    assert config.connector_path == "/sse/"


def test_server_config_normalizes_mount_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MCP_MOUNT_PATH", "custom")

    config = get_server_config_from_env()

    assert config.mount_path == "/custom"
    assert config.connector_path == "/custom/"


def test_server_config_rejects_invalid_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MCP_TRANSPORT", "stdio")

    with pytest.raises(ValueError, match="MCP_TRANSPORT"):
        get_server_config_from_env()


def test_server_config_rejects_invalid_port(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MCP_PORT", "not-a-number")

    with pytest.raises(ValueError, match="MCP_PORT"):
        get_server_config_from_env()


def test_fastmcp_init_kwargs_for_streamable_http() -> None:
    config = ServerConfig(transport="streamable-http", host="127.0.0.1", port=9000, mount_path="/mcp")

    assert _fastmcp_init_kwargs(config) == {
        "host": "127.0.0.1",
        "port": 9000,
        "mount_path": "/mcp",
        "streamable_http_path": "/mcp",
    }


def test_fastmcp_init_kwargs_for_sse() -> None:
    config = ServerConfig(transport="sse", host="127.0.0.1", port=9000, mount_path="/sse")

    assert _fastmcp_init_kwargs(config) == {
        "host": "127.0.0.1",
        "port": 9000,
        "mount_path": "/sse",
        "sse_path": "/sse",
    }


def test_register_tools_registers_all_tools() -> None:
    server = DummyServer()

    register_tools(server)

    assert server.registered == [
        "acquire_1d_spectrum",
        "get_parameter",
        "read_csv_file",
    ]


def test_apply_server_config_sets_streamable_http_settings() -> None:
    server = DummyServer()
    config = ServerConfig(transport="streamable-http", host="127.0.0.1", port=9000, mount_path="/mcp")

    apply_server_config(server, config)

    assert server.settings.host == "127.0.0.1"
    assert server.settings.port == 9000
    assert server.settings.mount_path == "/mcp"
    assert server.settings.streamable_http_path == "/mcp"


def test_apply_server_config_sets_sse_settings() -> None:
    server = DummyServer()
    config = ServerConfig(transport="sse", host="127.0.0.1", port=9000, mount_path="/sse")

    apply_server_config(server, config)

    assert server.settings.host == "127.0.0.1"
    assert server.settings.port == 9000
    assert server.settings.mount_path == "/sse"
    assert server.settings.sse_path == "/sse"


def test_create_mcp_server_uses_config_in_constructor(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeFastMCP(DummyServer):
        def __init__(self, name: str, **kwargs: object) -> None:
            super().__init__()
            captured["name"] = name
            captured.update(kwargs)

    monkeypatch.setattr(server_module, "FastMCP", FakeFastMCP)

    create_mcp_server(ServerConfig())

    assert captured["name"] == "spectrometer_mcp"
    assert captured["host"] == DEFAULT_HOST
    assert captured["port"] == DEFAULT_PORT
    assert captured["streamable_http_path"] == "/mcp"


def test_run_server_uses_transport_only_for_streamable_http() -> None:
    server = DummyServer()

    run_server(server)

    assert server.run_calls == [{"transport": "streamable-http"}]


def test_run_server_passes_mount_path_for_sse(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MCP_TRANSPORT", "sse")
    server = DummyServer()

    run_server(server)

    assert server.run_calls == [{"transport": "sse", "mount_path": "/sse"}]
