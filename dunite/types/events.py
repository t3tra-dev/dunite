"""
Type definitions for Minecraft events.

This module contains type definitions and enums for working with
Minecraft events and their data.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Any, Dict, Union

from .messages import EventProperties


class EventType(str, enum.Enum):
    """
    Available Minecraft event types.

    These events can be subscribed to using the WebSocket protocol.
    Some events may not be available in all versions of Minecraft.
    """

    ADDITIONAL_CONTENT_LOADED = "AdditionalContentLoaded"
    AGENT_COMMAND = "AgentCommand"
    AGENT_CREATED = "AgentCreated"
    API_INIT = "ApiInit"
    APP_PAUSED = "AppPaused"
    APP_RESUMED = "AppResumed"
    APP_SUSPENDED = "AppSuspended"
    AWARD_ACHIEVEMENT = "AwardAchievement"
    BLOCK_BROKEN = "BlockBroken"
    BLOCK_PLACED = "BlockPlaced"
    BOARD_TEXT_UPDATED = "BoardTextUpdated"
    BOSS_KILLED = "BossKilled"
    CAMERA_USED = "CameraUsed"
    CAULDRON_USED = "CauldronUsed"
    CONFIGURATION_CHANGED = "ConfigurationChanged"
    CONNECTION_FAILED = "ConnectionFailed"
    CRAFTING_SESSION_COMPLETED = "CraftingSessionCompleted"
    END_OF_DAY = "EndOfDay"
    ENTITY_SPAWNED = "EntitySpawned"
    FILE_TRANSMISSION_CANCELLED = "FileTransmissionCancelled"
    FILE_TRANSMISSION_COMPLETED = "FileTransmissionCompleted"
    FILE_TRANSMISSION_STARTED = "FileTransmissionStarted"
    FIRST_TIME_CLIENT_OPEN = "FirstTimeClientOpen"
    FOCUS_GAINED = "FocusGained"
    FOCUS_LOST = "FocusLost"
    GAME_SESSION_COMPLETE = "GameSessionComplete"
    GAME_SESSION_START = "GameSessionStart"
    HARDWARE_INFO = "HardwareInfo"
    HAS_NEW_CONTENT = "HasNewContent"
    ITEM_ACQUIRED = "ItemAcquired"
    ITEM_CRAFTED = "ItemCrafted"
    ITEM_DESTROYED = "ItemDestroyed"
    ITEM_DROPPED = "ItemDropped"
    ITEM_ENCHANTED = "ItemEnchanted"
    ITEM_SMELTED = "ItemSmelted"
    ITEM_USED = "ItemUsed"
    JOIN_CANCELED = "JoinCanceled"
    JUKEBOX_USED = "JukeboxUsed"
    LICENSE_CENSUS = "LicenseCensus"
    MASCOT_CREATED = "MascotCreated"
    MENU_SHOWN = "MenuShown"
    MOB_INTERACTED = "MobInteracted"
    MOB_KILLED = "MobKilled"
    MULTIPLAYER_CONNECTION_STATE_CHANGED = "MultiplayerConnectionStateChanged"
    MULTIPLAYER_ROUND_END = "MultiplayerRoundEnd"
    MULTIPLAYER_ROUND_START = "MultiplayerRoundStart"
    NPC_PROPERTIES_UPDATED = "NpcPropertiesUpdated"
    OPTIONS_UPDATED = "OptionsUpdated"
    PERFORMANCE_METRICS = "performanceMetrics"
    PACK_IMPORT_STAGE = "PackImportStage"
    PLAYER_BOUNCED = "PlayerBounced"
    PLAYER_DIED = "PlayerDied"
    PLAYER_JOIN = "PlayerJoin"
    PLAYER_LEAVE = "PlayerLeave"
    PLAYER_MESSAGE = "PlayerMessage"
    PLAYER_TELEPORTED = "PlayerTeleported"
    PLAYER_TRANSFORM = "PlayerTransform"
    PLAYER_TRAVELLED = "PlayerTravelled"
    PORTAL_BUILT = "PortalBuilt"
    PORTAL_USED = "PortalUsed"
    PORTFOLIO_EXPORTED = "PortfolioExported"
    POTION_BREWED = "PotionBrewed"
    PURCHASE_ATTEMPT = "PurchaseAttempt"
    PURCHASE_RESOLVED = "PurchaseResolved"
    REGIONAL_POPUP = "RegionalPopup"
    RESPONDED_TO_ACCEPT_CONTENT = "RespondedToAcceptContent"
    SCREEN_CHANGED = "ScreenChanged"
    SCREEN_HEARTBEAT = "ScreenHeartbeat"
    SIGN_IN_TO_EDU = "SignInToEdu"
    SIGN_IN_TO_XBOX_LIVE = "SignInToXboxLive"
    SIGN_OUT_OF_XBOX_LIVE = "SignOutOfXboxLive"
    SPECIAL_MOB_BUILT = "SpecialMobBuilt"
    START_CLIENT = "StartClient"
    START_WORLD = "StartWorld"
    TEXT_TO_SPEECH_TOGGLED = "TextToSpeechToggled"
    UGC_DOWNLOAD_COMPLETED = "UgcDownloadCompleted"
    UGC_DOWNLOAD_STARTED = "UgcDownloadStarted"
    UPLOAD_SKIN = "UploadSkin"
    VEHICLE_EXITED = "VehicleExited"
    WORLD_EXPORTED = "WorldExported"
    WORLD_FILES_LISTED = "WorldFilesListed"
    WORLD_GENERATED = "WorldGenerated"
    WORLD_LOADED = "WorldLoaded"
    WORLD_UNLOADED = "WorldUnloaded"


class PlayerGameMode(enum.IntEnum):
    """Player game mode values."""

    SURVIVAL = 0
    CREATIVE = 1
    ADVENTURE = 2
    SPECTATOR = 3
    DEFAULT = 5


class Biome(enum.IntEnum):
    """Biome type values."""

    OCEAN = 0
    PLAINS = 1
    DESERT = 2
    WINDSWEPT_HILLS = 3
    FOREST = 4
    TAIGA = 5
    SWAMPLAND = 6
    RIVER = 7
    HELL = 8
    THE_END = 9
    FROZEN_OCEAN = 10
    FROZEN_RIVER = 11
    ICE_PLAINS = 12
    ICE_MOUNTAINS = 13
    MUSHROOM_ISLAND = 14
    MUSHROOM_ISLAND_SHORE = 15
    BEACH = 16
    DESERT_HILLS = 17
    FOREST_HILLS = 18
    TAIGA_HILLS = 19
    EXTREME_HILLS_EDGE = 20
    JUNGLE = 21
    JUNGLE_HILLS = 22
    JUNGLE_EDGE = 23
    DEEP_OCEAN = 24
    STONE_BEACH = 25
    COLD_BEACH = 26
    BIRCH_FOREST = 27
    BIRCH_FOREST_HILLS = 28
    ROOFED_FOREST = 29
    COLD_TAIGA = 30
    COLD_TAIGA_HILLS = 31
    MEGA_TAIGA = 32
    MEGA_TAIGA_HILLS = 33
    WINDSWEPT_FOREST = 34
    SAVANNA = 35
    SAVANNA_PLATEAU = 36
    MESA = 37
    MESA_PLATEAU = 38
    MESA_PLATEAU_STONE = 39
    WARM_OCEAN = 40
    LUKEWARM_OCEAN = 41
    COLD_OCEAN = 42
    DEEP_WARM_OCEAN = 43
    DEEP_LUKEWARM_OCEAN = 44
    DEEP_COLD_OCEAN = 45
    DEEP_FROZEN_OCEAN = 46
    LEGACY_FROZEN_OCEAN = 47
    SUNFLOWER_PLAINS = 129
    DESERT_MUTATED = 130
    WINDSWEPT_GRAVELLY_HILLS = 131
    FLOWER_FOREST = 132
    TAIGA_MUTATED = 133
    SWAMPLAND_MUTATED = 134
    ICE_PLAINS_SPIKES = 140
    JUNGLE_MUTATED = 149
    JUNGLE_EDGE_MUTATED = 151
    BIRCH_FOREST_MUTATED = 155
    BIRCH_FOREST_HILLS_MUTATED = 156
    ROOFED_FOREST_MUTATED = 157
    COLD_TAIGA_MUTATED = 158
    REDWOOD_TAIGA_MUTATED = 160
    REDWOOD_TAIGA_HILLS_MUTATED = 161
    EXTREME_HILLS_PLUS_TREES_MUTATED = 162
    SAVANNA_MUTATED = 163
    SAVANNA_PLATEAU_MUTATED = 164
    MESA_BRYCE = 165
    MESA_PLATEAU_MUTATED = 166
    MESA_PLATEAU_STONE_MUTATED = 167
    BAMBOO_JUNGLE = 168
    BAMBOO_JUNGLE_HILLS = 169
    SOULSAND_VALLEY = 178
    CRIMSON_FOREST = 179
    WARPED_FOREST = 180
    BASALT_DELTAS = 181
    JAGGED_PEAKS = 182
    FROZEN_PEAKS = 183
    SNOWY_SLOPES = 184
    GROVE = 185
    MEADOW = 186
    LUSH_CAVES = 187
    DRIPSTONE_CAVES = 188
    STONY_PEAKS = 189


@dataclass
class EventData:
    """
    Base class for event data.

    :param event_type: Type of the event
    :param raw_data: Raw event data from Minecraft
    """

    event_type: EventType
    raw_data: Dict[str, Any]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> EventData:
        """
        Create an EventData instance from a dictionary.

        :param data: Dictionary containing event data
        :return: EventData instance
        :raises ValueError: If event type is invalid
        """
        body = data.get("body", {})
        event_name = body.get("eventName")

        try:
            event_type = EventType(event_name)
        except ValueError:
            raise ValueError(f"Unknown event type: {event_name}")

        # Create specific event data class based on event type
        if event_type == EventType.PLAYER_MESSAGE:
            return PlayerMessageData.from_dict(data)
        # Add more specific event types here as needed

        return EventData(event_type=event_type, raw_data=data)


@dataclass
class PlayerMessageData(EventData):
    """
    Data for PlayerMessage events.

    :param sender: Name of the player who sent the message
    :param message: Content of the message
    :param message_type: Type of message (e.g., "chat")
    :param properties: Additional message properties
    """

    sender: str
    message: str
    message_type: str
    properties: EventProperties

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> PlayerMessageData:
        """
        Create a PlayerMessageData instance from a dictionary.

        :param data: Dictionary containing event data
        :return: PlayerMessageData instance
        """
        body = data.get("body", {})
        properties = body.get("properties", {})

        return PlayerMessageData(
            event_type=EventType.PLAYER_MESSAGE,
            sender=properties.get("Sender", ""),
            message=properties.get("Message", ""),
            message_type=properties.get("MessageType", ""),
            properties=properties,
            raw_data=data,
        )


# Type alias for all possible event data types
Event = Union[EventData, PlayerMessageData]
