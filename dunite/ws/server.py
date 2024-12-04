"""
WebSocket server implementation.
"""

from __future__ import annotations

import asyncio
import logging
import ssl
from typing import Any, Awaitable, Callable, Optional

from .exceptions import WebSocketError
from .frames import CloseCode
from .http import Headers, build_response, parse_request, validate_handshake
from .protocol import State, WebSocketProtocol
from .utils import compute_accept_key


class WebSocketHandler:
    def __init__(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.reader = reader
        self.writer = writer
        if logger is None:
            logger = logging.getLogger("dunite.ws")
        self.logger = logger
        self.protocol = WebSocketProtocol(logger=logger)
        self._closed = False

    @property
    def closed(self) -> bool:
        return self._closed

    async def handle_connection(self) -> None:
        try:
            await self._handle_handshake()
            while not self.closed:
                data = await self.reader.read(65536)
                if not data:
                    break
                self.protocol.receive_data(data)
                outgoing = self.protocol.get_outgoing_data()
                if outgoing:
                    self.writer.write(outgoing)
                    await self.writer.drain()
        except Exception as e:
            self.logger.error(f"Connection error: {e}")
        finally:
            await self.close()

    async def _handle_handshake(self) -> None:
        # Read HTTP request
        data = await self.reader.read(65536)
        if not data:
            raise WebSocketError("Client disconnected during handshake")

        request, _ = parse_request(data)
        validate_handshake(request.headers, client_mode=False)

        key = request.headers["Sec-WebSocket-Key"]
        accept = compute_accept_key(key)

        # Build response
        headers = Headers(
            [
                ("Upgrade", "websocket"),
                ("Connection", "Upgrade"),
                ("Sec-WebSocket-Accept", accept),
            ]
        )
        response = build_response(101, headers)
        self.writer.write(response)
        await self.writer.drain()

        self.protocol.state.transition(State.OPEN)

    def send(self, data: str) -> None:
        if self.closed:
            raise WebSocketError("Connection is closed")
        message = data.encode("utf-8")
        self.protocol.send_message(message)
        outgoing = self.protocol.get_outgoing_data()
        if outgoing:
            self.writer.write(outgoing)

    def recv(self, timeout: Optional[float] = None) -> str:
        if self.closed:
            raise WebSocketError("Connection is closed")
        try:
            message = self.protocol.receive_message(timeout=timeout)
            if isinstance(message, bytes):
                return message.decode("utf-8")
            return message
        except Exception as e:
            raise WebSocketError(f"Error receiving message: {e}")

    async def close(self, code: int = CloseCode.NORMAL) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self.protocol.close(code)
            outgoing = self.protocol.get_outgoing_data()
            if outgoing:
                self.writer.write(outgoing)
                await self.writer.drain()
            self.writer.close()
            await self.writer.wait_closed()
        except Exception:
            self.logger.exception("Error during close")


async def serve(
    handler: Callable[[WebSocketHandler], Awaitable[None]],
    host: str = "localhost",
    port: int = 8765,
    ssl_context: Optional[ssl.SSLContext] = None,
    logger: Optional[logging.Logger] = None,
    **kwargs: Any,
) -> asyncio.Server:
    """
    Start a WebSocket server.

    :param handler: Connection handler
    :param host: Host to bind to
    :param port: Port to bind to
    :param ssl_context: Optional SSL context
    :param logger: Optional logger instance
    :param kwargs: Additional server arguments
    :return: Server instance
    """

    async def handle_connection(
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        ws_handler = WebSocketHandler(reader, writer, logger)
        try:
            await handler(ws_handler)
        except Exception:
            if logger:
                logger.exception("Error in connection handler")
        finally:
            await ws_handler.close()

    return await asyncio.start_server(
        handle_connection, host, port, ssl=ssl_context, **kwargs
    )
