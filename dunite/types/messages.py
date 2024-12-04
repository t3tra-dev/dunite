"""
Type definitions for Minecraft WebSocket protocol messages.

This module contains type definitions for the messages exchanged between
Minecraft and the WebSocket server.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional, TypedDict, Union


class MessagePurpose(str, Enum):
    """Message purpose enum for header."""

    COMMAND_REQUEST = "commandRequest"
    COMMAND_RESPONSE = "commandResponse"
    EVENT = "event"
    ERROR = "error"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"


class MessageType(str, Enum):
    """Message type enum for header."""

    COMMAND_REQUEST = "commandRequest"


class Header(TypedDict):
    """Message header structure."""

    messagePurpose: str
    version: int
    requestId: str
    messageType: Optional[str]


class CommandOrigin(TypedDict):
    """Command origin structure."""

    type: str


class CommandRequestBody(TypedDict):
    """Command request body structure."""

    version: int
    commandLine: str
    origin: CommandOrigin


class CommandResponseBody(TypedDict):
    """Command response body structure."""

    statusCode: int
    statusMessage: str


class EventProperties(TypedDict, total=False):
    """Event properties structure with optional fields."""

    AccountType: int
    ActiveSessionID: str
    AppSessionID: str
    Biome: int
    Build: str
    BuildNum: str
    BuildPlat: int
    Cheevos: bool
    ClientId: str
    CurrentNumDevices: int
    DeviceSessionId: str
    Difficulty: str
    Dim: int
    GlobalMultiplayerCorrelationId: str
    Message: str
    MessageType: str
    Mode: int
    NetworkType: int
    Plat: str
    PlayerGameMode: int
    Sender: str
    Seq: int
    WorldFeature: int
    WorldSessionId: str
    editionType: str
    isTrial: int
    locale: str
    vrMode: bool


class EventBody(TypedDict):
    """Event body structure."""

    eventName: str
    measurements: Optional[Any]
    properties: EventProperties


class ErrorBody(TypedDict):
    """Error body structure."""

    statusMessage: str
    statusCode: int


class SubscriptionBody(TypedDict):
    """Subscription body structure."""

    eventName: str


# Complete message structures
class CommandRequestMessage(TypedDict):
    """Complete command request message structure."""

    header: Header
    body: CommandRequestBody


class CommandResponseMessage(TypedDict):
    """Complete command response message structure."""

    header: Header
    body: CommandResponseBody


class EventMessage(TypedDict):
    """Complete event message structure."""

    header: Header
    body: EventBody


class ErrorMessage(TypedDict):
    """Complete error message structure."""

    header: Header
    body: ErrorBody


class SubscriptionMessage(TypedDict):
    """Complete subscription message structure."""

    header: Header
    body: SubscriptionBody


# Union type for all possible messages
Message = Union[
    CommandRequestMessage,
    CommandResponseMessage,
    EventMessage,
    ErrorMessage,
    SubscriptionMessage,
]
