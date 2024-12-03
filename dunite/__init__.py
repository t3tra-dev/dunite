"""
dunite
~~~~~~~~~~~~~~~~~~~

WebSocket server for Minecraft Bedrock

:copyright: (c) 2024-present t3tra
:license: MIT, see LICENSE for more details.

"""


__title__ = 'dunite'
__author__ = 't3tra'
__license__ = 'MIT'
__copyright__ = 'Copyright 2024 t3tra'
__version__ = '0.1.0'

__path__ = __import__('pkgutil').extend_path(__path__, __name__)

import logging
from typing import NamedTuple, Literal


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: Literal["alpha", "beta", "candidate", "final"]
    serial: int


version_info: VersionInfo = VersionInfo(major=0, minor=0, micro=1, releaselevel='final', serial=0)

logging.getLogger(__name__).addHandler(logging.NullHandler())

del logging, NamedTuple, Literal, VersionInfo