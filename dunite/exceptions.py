"""
Exceptions for the Dunite library.

This module contains all custom exceptions that may be raised by the Dunite library.
Inherits from the base WebSocket exceptions where appropriate.
"""

from __future__ import annotations

from typing import Optional

from .ws.exceptions import WebSocketError, ConnectionError


class DuniteException(Exception):
    """Base exception for all Dunite-related errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class CommandError(DuniteException):
    """
    Raised when a command execution fails.

    :param message: Error message
    :param code: Error status code from Minecraft
    :param command: The command that failed
    """

    def __init__(self, message: str, code: int, command: str) -> None:
        super().__init__(message)
        self.code = code
        self.command = command

    def __str__(self) -> str:
        return f"{super().__str__()} (code={self.code}, command={self.command!r})"


class EventError(DuniteException):
    """
    Raised when there is an error processing an event.

    :param message: Error message
    :param event_name: Name of the event that caused the error
    """

    def __init__(self, message: str, event_name: str) -> None:
        super().__init__(message)
        self.event_name = event_name

    def __str__(self) -> str:
        return f"{super().__str__()} (event={self.event_name!r})"


class SubscriptionError(DuniteException):
    """
    Raised when there is an error subscribing to or unsubscribing from events.

    :param message: Error message
    :param event_name: Name of the event that caused the error
    """

    def __init__(self, message: str, event_name: str) -> None:
        super().__init__(message)
        self.event_name = event_name

    def __str__(self) -> str:
        return f"{super().__str__()} (event={self.event_name!r})"


class ProtocolError(WebSocketError):
    """
    Raised when there is an error in the Minecraft protocol.

    :param message: Error message
    :param raw_message: Raw message that caused the error
    """

    def __init__(self, message: str, raw_message: Optional[dict] = None) -> None:
        super().__init__(message)
        self.raw_message = raw_message

    def __str__(self) -> str:
        if self.raw_message:
            return f"{super().__str__()} (message={self.raw_message!r})"
        return super().__str__()


class ClientError(ConnectionError):
    """
    Raised when there is an error with the Minecraft client connection.

    :param message: Error message
    :param client_id: ID of the client that caused the error
    """

    def __init__(self, message: str, client_id: Optional[str] = None) -> None:
        super().__init__(message)
        self.client_id = client_id

    def __str__(self) -> str:
        if self.client_id:
            return f"{super().__str__()} (client={self.client_id!r})"
        return super().__str__()
