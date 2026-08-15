"""Entity classifications."""

from __future__ import annotations

from enum import Enum


class EntityType(Enum):
    STATE = "state"

    MILITARY = "military"

    GOVERNMENT = "government"

    INTERNATIONAL_ORGANIZATION = "international-organization"

    COMPANY = "company"

    PERSON = "person"

    LOCATION = "location"

    INFRASTRUCTURE = "infrastructure"

    OTHER = "other"