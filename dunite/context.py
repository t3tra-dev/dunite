"""
Context class for event handlers.

This module provides the Context class that is passed to event handlers,
containing all relevant information about the event and client state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict

from .types.events import Event, EventData, EventType
from .types.commands import Command, CommandResponse

if TYPE_CHECKING:
    from .client import Client


@dataclass
class Context:
    """
    Context for event handlers.

    Provides access to the client connection, event data, and utility methods
    for interacting with the Minecraft client.

    :param client: Client instance representing the Minecraft connection
    :param event: Event data
    :param raw_data: Raw event data from Minecraft
    """

    client: Client
    event: Event
    raw_data: Dict[str, Any]

    @property
    def event_type(self) -> EventType:
        """Get the event type."""
        return self.event.event_type

    @property
    def properties(self) -> Dict[str, Any]:
        """Get event properties."""
        return self.raw_data.get("body", {}).get("properties", {})

    async def reply(self, message: str) -> CommandResponse:
        """
        Reply to the current event with a message.

        This is a convenience method for sending a message in response to an event.
        For PlayerMessage events, it will send a message back to the player.

        :param message: Message to send
        :return: Command response
        :raises CommandError: If the command fails
        """
        return await self.run_command(f"say {message}")

    async def run_command(self, command: str | Command) -> CommandResponse:
        """
        Run a Minecraft command.

        :param command: Command to run (string or Command object)
        :return: Command response
        :raises CommandError: If the command fails
        """
        if isinstance(command, str):
            command = Command.parse(command)
        return await self.client.run_command(command)

    async def subscribe(self, event_type: EventType) -> None:
        """
        Subscribe to an event type.

        :param event_type: Event type to subscribe to
        :raises SubscriptionError: If subscription fails
        """
        await self.client.subscribe(event_type)

    async def unsubscribe(self, event_type: EventType) -> None:
        """
        Unsubscribe from an event type.

        :param event_type: Event type to unsubscribe from
        :raises SubscriptionError: If unsubscription fails
        """
        await self.client.unsubscribe(event_type)

    @staticmethod
    def from_event(client: Client, event_data: Dict[str, Any]) -> Context:
        """
        Create a Context instance from event data.

        :param client: Client instance
        :param event_data: Raw event data from Minecraft
        :return: Context instance
        :raises ValueError: If event data is invalid
        """
        event = EventData.from_dict(event_data)
        return Context(client=client, event=event, raw_data=event_data)

    def __repr__(self) -> str:
        """Return string representation of the context."""
        return (
            f"Context(event_type={self.event_type.value}, client_id={self.client.id})"
        )
