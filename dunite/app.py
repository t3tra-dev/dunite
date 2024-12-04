"""
Server implementation for Dunite.

This module provides the Server class that manages WebSocket connections
and event handling for Minecraft clients.
"""

from __future__ import annotations

import asyncio
import logging
import signal
from typing import Any, Callable, Dict, Optional, Set

from .client import Client
from .context import Context
from .types.events import EventType
from .ws.server import WebSocketHandler, serve


class Server:
    """
    WebSocket server for Minecraft.

    Manages WebSocket connections and routes events to appropriate handlers.

    :param name: Server name
    :param logger: Optional logger instance
    """

    def __init__(self, name: str, logger: Optional[logging.Logger] = None) -> None:
        if logger is None:
            logger = logging.getLogger(name)
        self.logger = logger
        self.name = name

        self._event_handlers: Dict[EventType, Set[EventHandler]] = {}
        self._clients: Set[Client] = set()
        self._running = False
        self._tasks: Set[asyncio.Task] = set()
        self._ws_server = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def on(
        self, event_type: str | EventType, *, auto_subscribe: bool = True
    ) -> Callable[[EventHandler], EventHandler]:
        """
        Decorator for registering event handlers.

        :param event_type: Event type to handle
        :param auto_subscribe: Whether to automatically subscribe to the event
        :return: Decorator function
        :raises ValueError: If event type is invalid

        Example::

            @app.on("PlayerMessage")
            async def handle_message(ctx: Context):
                await ctx.reply("Hello!")
        """
        if isinstance(event_type, str):
            try:
                event_type = EventType(event_type)
            except ValueError:
                raise ValueError(f"Unknown event type: {event_type}")

        def decorator(handler: EventHandler) -> EventHandler:
            handlers = self._event_handlers.setdefault(event_type, set())
            handlers.add(handler)
            handler._auto_subscribe = auto_subscribe  # type: ignore
            return handler

        return decorator

    async def _handle_client(self, handler: WebSocketHandler) -> None:
        """
        Handle a client connection.

        :param handler: WebSocket connection handler
        """
        client = Client(handler, self.logger)
        self._clients.add(client)
        self.logger.info(f"Client connected: {client.id}")

        try:
            # Subscribe to events that have handlers with auto_subscribe
            for event_type, handlers in self._event_handlers.items():
                if any(getattr(h, "_auto_subscribe", True) for h in handlers):
                    await client.subscribe(event_type)

            while not client.closed:
                try:
                    message = await client.receive_message()
                    task = asyncio.create_task(self._handle_message(client, message))
                    self._tasks.add(task)
                    task.add_done_callback(self._tasks.discard)
                except Exception as e:
                    self.logger.error(f"Error handling message: {e}")

        except Exception as e:
            self.logger.error(f"Client error: {e}")
        finally:
            await self._cleanup_client(client)

    async def _handle_message(self, client: Client, message: Dict[str, Any]) -> None:
        """
        Handle a received message.

        :param client: Client that sent the message
        :param message: Message to handle
        """
        try:
            # Handle command responses
            await client.handle_message(message)

            # Handle events
            header = message.get("header", {})
            if header.get("messagePurpose") == "event":
                body = message.get("body", {})
                event_name = body.get("eventName")
                if event_name:
                    try:
                        event_type = EventType(event_name)
                    except ValueError:
                        self.logger.warning(f"Unknown event type: {event_name}")
                        return

                    handlers = self._event_handlers.get(event_type, set())
                    if handlers:
                        context = Context.from_event(client, message)
                        for handler in handlers:
                            try:
                                task = asyncio.create_task(handler(context))
                                self._tasks.add(task)
                                task.add_done_callback(self._tasks.discard)
                            except Exception:
                                self.logger.exception(
                                    f"Error in event handler for {event_type}"
                                )

        except Exception as e:
            self.logger.error(f"Error processing message: {e}")

    async def _cleanup_client(self, client: Client) -> None:
        """
        Clean up a client connection.

        :param client: Client to clean up
        """
        try:
            await client.close()
        except Exception:
            self.logger.exception("Error closing client")
        finally:
            self._clients.discard(client)
            self.logger.info(f"Client disconnected: {client.id}")

    async def _shutdown(self) -> None:
        """Shut down the server."""
        self._running = False

        # Close all clients
        for client in list(self._clients):
            await self._cleanup_client(client)

        # Cancel all tasks
        for task in self._tasks:
            task.cancel()

        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

    def run(
        self,
        host: str = "localhost",
        port: int = 8765,
        **kwargs: Any
    ) -> None:
        """
        Run the server.

        :param host: Host to bind to
        :param port: Port to bind to
        :param kwargs: Additional arguments for the WebSocket server
        """
        async def server_main() -> None:
            self._running = True
            self._loop = asyncio.get_running_loop()

            def signal_handler():
                if not self._running:
                    return
                self._running = False
                asyncio.create_task(self._shutdown())

            # Set up signal handlers
            for sig in (signal.SIGINT, signal.SIGTERM):
                self._loop.add_signal_handler(sig, signal_handler)

            async def handle_client(websocket: WebSocketHandler) -> None:
                await self._handle_client(websocket)

            try:
                server = await serve(
                    handle_client,
                    host,
                    port,
                    logger=self.logger,
                    **kwargs
                )
                self._ws_server = server
                self.logger.info(f"Server running on ws://{host}:{port}")

                # Wait until shutdown is triggered
                while self._running:
                    await asyncio.sleep(0.1)

            except Exception as e:
                self.logger.error(f"Server error: {e}")
            finally:
                if self._ws_server:
                    self._ws_server.close()
                    await self._ws_server.wait_closed()
                await self._shutdown()

        try:
            asyncio.run(server_main())
        except KeyboardInterrupt:
            self.logger.info("Server stopped")


# Type alias for event handlers
EventHandler = Callable[[Context], Any]
