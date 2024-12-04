"""
Type definitions for Minecraft commands.

This module contains type definitions and classes for working with
Minecraft commands and their responses.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from ..exceptions import CommandError


@dataclass
class CommandResponse:
    """
    Represents a response from a Minecraft command.

    :param code: Status code of the response (0 for success)
    :param status_message: Status message from the command
    :param raw_response: Raw response data from Minecraft

    :raises CommandError: If the command failed (status code != 0)
    """

    code: int
    status_message: str
    raw_response: Dict[str, Any]

    def __post_init__(self) -> None:
        """Validate the response and raise error if needed."""
        if self.code != 0:
            raise CommandError(
                message=self.status_message,
                code=self.code,
                command=self.raw_response.get("body", {}).get("commandLine", "unknown"),
            )

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> CommandResponse:
        """
        Create a CommandResponse from a dictionary.

        :param data: Dictionary containing response data
        :return: CommandResponse instance
        """
        body = data.get("body", {})
        return CommandResponse(
            code=body.get("statusCode", -1),
            status_message=body.get("statusMessage", "Unknown error"),
            raw_response=data,
        )


@dataclass
class Command:
    """
    Represents a Minecraft command to be executed.

    :param name: Name of the command
    :param args: Optional command arguments
    :param input_data: Optional input data for the command
    """

    name: str
    args: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None

    def __str__(self) -> str:
        """Convert command to string format."""
        if self.args:
            return f"{self.name} {self.args}"
        return self.name

    @staticmethod
    def parse(command_line: str) -> Command:
        """
        Parse a command line into a Command object.

        :param command_line: Command line string
        :return: Command instance
        """
        parts = command_line.strip().split(maxsplit=1)
        name = parts[0]
        args = parts[1] if len(parts) > 1 else None
        return Command(name=name, args=args)
