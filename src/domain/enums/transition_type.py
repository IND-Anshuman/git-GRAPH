"""Enum defining how a logic signature transitioned between two versions."""

from enum import Enum


class TransitionType(str, Enum):
    """Describes the type of transition a logic signature underwent between commits."""

    UNCHANGED = "UNCHANGED"
    """The logic implementation remained identical."""

    EVOLVED = "EVOLVED"
    """The logic was modified but retains its core behavior."""

    REPLACED = "REPLACED"
    """The logic was replaced by a substantially different implementation."""

    MERGED = "MERGED"
    """Multiple logic versions were merged into one."""

    SPLIT = "SPLIT"
    """A single logic version was split into multiple implementations."""

    CREATED = "CREATED"
    """First appearance of this logic in the codebase."""

    DELETED = "DELETED"
    """The logic is no longer present in the codebase."""
