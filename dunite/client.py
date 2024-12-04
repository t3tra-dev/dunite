"""
Client implementation for Minecraft WebSocket communication.

This module provides the Client class that handles the WebSocket connection
with Minecraft and manages command execution and event subscriptions.
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any, Dict, Optional, Set

from .exceptions import ClientError, CommandError, ProtocolError, SubscriptionError
from .types.commands import Command, CommandResponse
from .types.events import EventType
from .types.messages import (
    CommandRequestMessage,
    CommandResponseMessage,
    ErrorMessage,
    EventMessage,
    Message,
    MessagePurpose,
    MessageType,
)
from .ws.frames import CloseCode
from .ws.server import WebSocketHandler


class Client:
    """
    Client for Minecraft WebSocket communication.

    Handles command execution, event subscription, and message routing.

    :param handler: WebSocket connection handler
    :param logger: Optional logger instance
    """

    def __init__(
        self,
        handler: WebSocketHandler,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.handler = handler
        if logger is None:
            logger = logging.getLogger("dunite.client")
        self.logger = logger

        self.id = str(uuid.uuid4())
        self._subscribed_events: Set[EventType] = set()
        self._pending_requests: Dict[str, asyncio.Future[Message]] = {}
        self._response_lock = asyncio.Lock()
        self._closed = False

    @property
    def closed(self) -> bool:
        """Whether the client connection is closed."""
        return self._closed or self.handler.closed

    async def send_message(self, message: Dict[str, Any]) -> None:
        """
        Send a message to the client.

        :param message: Message to send
        :raises ClientError: If connection is closed or send fails
        """
        if self.closed:
            raise ClientError("Connection is closed", self.id)

        try:
            await self.handler.send(json.dumps(message))
        except Exception as e:
            raise ClientError(f"Failed to send message: {e}", self.id) from e

    async def receive_message(self) -> Message:
        """
        Receive a message from the client.

        :return: Received message
        :raises ClientError: If connection is closed or receive fails
        :raises ProtocolError: If message format is invalid
        """
        if self.closed:
            raise ClientError("Connection is closed", self.id)

        try:
            data = await self.handler.recv()
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            message = json.loads(data)
            return self._validate_message(message)
        except json.JSONDecodeError as e:
            raise ProtocolError("Invalid JSON message", None) from e
        except Exception as e:
            raise ClientError(f"Failed to receive message: {e}", self.id) from e

    def _validate_message(self, message: Dict[str, Any]) -> Message:
        """
        Validate and type a received message.

        :param message: Raw message dictionary
        :return: Typed message
        :raises ProtocolError: If message format is invalid
        """
        if not isinstance(message, dict):
            raise ProtocolError("Message must be a dictionary", message)

        header = message.get("header")
        if not isinstance(header, dict):
            raise ProtocolError("Message must have a header", message)

        purpose = header.get("messagePurpose")
        if not purpose:
            raise ProtocolError("Message must have a purpose", message)

        # Type the message based on its purpose
        try:
            if purpose == MessagePurpose.COMMAND_RESPONSE:
                return CommandResponseMessage(**message)  # type: ignore
            elif purpose == MessagePurpose.EVENT:
                return EventMessage(**message)  # type: ignore
            elif purpose == MessagePurpose.ERROR:
                return ErrorMessage(**message)  # type: ignore
            else:
                raise ProtocolError(f"Unknown message purpose: {purpose}", message)
        except Exception as e:
            raise ProtocolError(f"Invalid message structure: {e}", message) from e

    async def run_command(self, command: Command) -> CommandResponse:
        """
        Run a Minecraft command.

        :param command: Command to run
        :return: Command response
        :raises CommandError: If command execution fails
        :raises ClientError: If connection is closed
        """
        request_id = str(uuid.uuid4())
        message: CommandRequestMessage = {
            "header": {
                "version": 1,
                "requestId": request_id,
                "messagePurpose": MessagePurpose.COMMAND_REQUEST,
                "messageType": MessageType.COMMAND_REQUEST,
            },
            "body": {
                "version": 1,
                "commandLine": str(command),
                "origin": {"type": "player"},
            },
        }

        future: asyncio.Future[Message] = asyncio.Future()
        self._pending_requests[request_id] = future

        try:
            await self.send_message(message)
            response = await asyncio.wait_for(future, timeout=10.0)

            if "error" in response["header"]["messagePurpose"]:
                error_msg = response["body"]["statusMessage"]
                raise CommandError(error_msg, -1, str(command))

            return CommandResponse.from_dict(response)
        except asyncio.TimeoutError:
            raise CommandError("Command timed out", -1, str(command))
        finally:
            self._pending_requests.pop(request_id, None)

    async def subscribe(self, event_type: EventType) -> None:
        """
        Subscribe to an event type.

        :param event_type: Event type to subscribe to
        :raises SubscriptionError: If subscription fails
        """
        if event_type in self._subscribed_events:
            return

        message = {
            "header": {
                "version": 1,
                "requestId": str(uuid.uuid4()),
                "messagePurpose": MessagePurpose.SUBSCRIBE,
                "messageType": MessageType.COMMAND_REQUEST,
            },
            "body": {"eventName": event_type.value},
        }

        try:
            await self.send_message(message)
            self._subscribed_events.add(event_type)
        except Exception as e:
            raise SubscriptionError(f"Failed to subscribe: {e}", event_type.value)

    async def unsubscribe(self, event_type: EventType) -> None:
        """
        Unsubscribe from an event type.

        :param event_type: Event type to unsubscribe from
        :raises SubscriptionError: If unsubscription fails
        """
        if event_type not in self._subscribed_events:
            return

        message = {
            "header": {
                "version": 1,
                "requestId": str(uuid.uuid4()),
                "messagePurpose": MessagePurpose.UNSUBSCRIBE,
                "messageType": MessageType.COMMAND_REQUEST,
            },
            "body": {"eventName": event_type.value},
        }

        try:
            await self.send_message(message)
            self._subscribed_events.remove(event_type)
        except Exception as e:
            raise SubscriptionError(f"Failed to unsubscribe: {e}", event_type.value)

    async def handle_message(self, message: Message) -> None:
        """
        Handle an incoming message.

        :param message: Message to handle
        """
        header = message["header"]
        request_id = header.get("requestId")

        if request_id in self._pending_requests:
            future = self._pending_requests[request_id]
            if not future.done():
                future.set_result(message)

    async def close(self) -> None:
        """Close the client connection."""
        if self._closed:
            return

        self._closed = True
        try:
            await self.handler.close(CloseCode.NORMAL)
        except Exception:
            self.logger.exception("Error closing client connection")

        # Cancel any pending requests
        for future in self._pending_requests.values():
            if not future.done():
                future.cancel()
        self._pending_requests.clear()
