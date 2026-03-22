from __future__ import annotations

import os

import pytest

from spectrometer_mcp.server import DEFAULT_HOST, DEFAULT_PORT, ServerConfig, get_server_config_from_env


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
