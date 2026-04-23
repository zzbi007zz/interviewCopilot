from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any, Callable
from urllib.parse import urlparse

from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed
from websockets.server import ServerConnection

from config import PROTOCOL_VERSION


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class WebSocketHub:
    _LOCAL_HOSTS = {"127.0.0.1", "::1", "localhost", "::ffff:127.0.0.1"}
    _ALLOWED_ORIGIN_SCHEMES = {"http", "https"}
    _SEND_TIMEOUT_SECONDS = 1.0

    def __init__(
        self,
        host: str,
        port: int,
        session_id: str,
        state_provider: Callable[[], str] | None = None,
    ) -> None:
        self._host = host
        self._port = port
        self._session_id = session_id
        self._state_provider = state_provider or (lambda: "listening")
        self._clients: set[ServerConnection] = set()
        self._server = None

    async def start(self) -> None:
        self._server = await serve(self._handle_client, self._host, self._port)

    async def stop(self) -> None:
        for client in list(self._clients):
            await client.close()
        self._clients.clear()

        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()

    async def _send_with_timeout(self, client: ServerConnection, message: str) -> bool:
        try:
            await asyncio.wait_for(client.send(message), timeout=self._SEND_TIMEOUT_SECONDS)
            return True
        except (ConnectionClosed, asyncio.TimeoutError):
            return False

    async def broadcast(
        self,
        event_type: str,
        payload: dict[str, Any],
        metadata: dict[str, str | int | float | bool | None] | None = None,
    ) -> None:
        if not self._clients:
            return

        event: dict[str, Any] = {
            "protocolVersion": PROTOCOL_VERSION,
            "type": event_type,
            "timestamp": _timestamp(),
            "sessionId": self._session_id,
            "payload": payload,
        }

        if metadata:
            event["metadata"] = metadata

        message = json.dumps(event)

        clients = list(self._clients)
        results = await asyncio.gather(
            *(self._send_with_timeout(client, message) for client in clients),
            return_exceptions=False,
        )

        stale = [client for client, sent in zip(clients, results, strict=False) if not sent]

        for client in stale:
            self._clients.discard(client)
            try:
                await client.close()
            except ConnectionClosed:
                pass

    def _is_local_peer(self, websocket: ServerConnection) -> bool:
        remote = websocket.remote_address
        if remote is None:
            return False

        host = remote[0] if isinstance(remote, tuple) and remote else str(remote)
        return host in self._LOCAL_HOSTS

    def _extract_origin(self, websocket: ServerConnection) -> str | None:
        request = getattr(websocket, "request", None)
        headers = getattr(request, "headers", None) if request is not None else None
        if headers is None:
            return None

        return headers.get("Origin") or headers.get("origin")

    def _is_allowed_origin(self, origin: str) -> bool:
        try:
            parsed = urlparse(origin.strip())
        except ValueError:
            return False

        if parsed.scheme.lower() not in self._ALLOWED_ORIGIN_SCHEMES:
            return False

        if parsed.hostname is None:
            return False

        return parsed.hostname.lower() in self._LOCAL_HOSTS

    async def _handle_client(self, websocket: ServerConnection) -> None:
        if not self._is_local_peer(websocket):
            await websocket.close(code=1008, reason="Local connections only")
            return

        origin = self._extract_origin(websocket)
        if origin and not self._is_allowed_origin(origin):
            await websocket.close(code=1008, reason="Origin not allowed")
            return

        self._clients.add(websocket)
        await self.broadcast(
            "status.update",
            {"state": self._state_provider(), "message": "Client connected"},
        )

        try:
            async for _ in websocket:
                pass
        finally:
            self._clients.discard(websocket)

    async def wait_forever(self) -> None:
        await asyncio.Future()
