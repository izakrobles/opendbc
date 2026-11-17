"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from enum import IntFlag


class VolkswagenSafetyFlagsSP:
  BRAKE_STOP_RESUME = 1


class VolkswagenFlagsSP(IntFlag):
  BRAKE_STOP_RESUME = 1  # re-engage when the brake is released at a full stop it was held to (MQB, openpilot long)
