"""
WebSocket server implementation.
"""

from __future__ import annotations

import asyncio
import logging
import ssl
from typing import Any, Awaitable, Callable, Optional

from .exceptions import WebSocketError
from .frames import CloseCode, Frame, Opcode, parse_frame
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
        self._message_queue: asyncio.Queue[str] = asyncio.Queue()

    @property
    def closed(self) -> bool:
        return self._closed

    async def handle_connection(self) -> None:
        try:
            await self._handle_handshake()

            # Start reader and writer tasks
            reader_task = asyncio.create_task(self._reader_loop())
            writer_task = asyncio.create_task(self._writer_loop())

            # Wait for either task to complete
            done, pending = await asyncio.wait(
                [reader_task, writer_task], return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel remaining tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        except Exception as e:
            self.logger.error(f"Connection error: {e}")
        finally:
            await self.close()

    async def _reader_loop(self) -> None:
        """Read incoming frames from the socket."""
        try:
            while not self.closed:
                data = await self.reader.read(65536)
                if not data:
                    break
                frame, _ = parse_frame(data)

                if frame.opcode == Opcode.TEXT:
                    message = frame.payload.decode("utf-8")
                    await self._message_queue.put(message)
                elif frame.opcode == Opcode.CLOSE:
                    break
        except Exception as e:
            self.logger.error(f"Reader error: {e}")
        finally:
            await self.close()

    async def _writer_loop(self) -> None:
        """Write outgoing frames to the socket."""
        try:
            while not self.closed:
                outgoing = self.protocol.get_outgoing_data()
                if outgoing:
                    self.writer.write(outgoing)
                    await self.writer.drain()
                await asyncio.sleep(0.01)
        except Exception as e:
            self.logger.error(f"Writer error: {e}")
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

    async def send(self, data: str) -> None:
        if self.closed:
            raise WebSocketError("Connection is closed")

        frame = Frame(fin=True, opcode=Opcode.TEXT, payload=data.encode("utf-8"))
        self.writer.write(frame.serialize(mask=False))
        await self.writer.drain()

    async def recv(self, timeout: Optional[float] = None) -> str:
        if self.closed:
            raise WebSocketError("Connection is closed")

        try:
            if timeout is not None:
                message = await asyncio.wait_for(
                    self._message_queue.get(), timeout=timeout
                )
            else:
                message = await self._message_queue.get()
            return message
        except asyncio.TimeoutError:
            raise WebSocketError("Receive timeout")
        except Exception as e:
            raise WebSocketError(f"Error receiving message: {e}")

    async def close(self, code: int = CloseCode.NORMAL) -> None:
        if self._closed:
            return

        self._closed = True
        try:
            frame = Frame(
                fin=True, opcode=Opcode.CLOSE, payload=bytes([code >> 8, code & 0xFF])
            )
            self.writer.write(frame.serialize(mask=False))
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
        connection_task = asyncio.create_task(ws_handler.handle_connection())
        handler_task = asyncio.create_task(handler(ws_handler))

        try:
            await asyncio.gather(connection_task, handler_task)
        except Exception:
            if logger:
                logger.exception("Error in connection handler")
        finally:
            await ws_handler.close()

    return await asyncio.start_server(
        handle_connection, host, port, ssl=ssl_context, **kwargs
    )
