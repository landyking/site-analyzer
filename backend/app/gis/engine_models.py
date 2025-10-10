import logging
from typing import Protocol

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class EngineRestrictedFactor(BaseModel):
    kind: str
    buffer_distance: int


class EngineSuitabilityFactor(BaseModel):
    kind: str
    weight: float
    ranges: list[tuple[float, float, int]] | None = None


class EngineConfigs(BaseModel):
    restricted_factors: list[EngineRestrictedFactor]
    suitability_factors: list[EngineSuitabilityFactor]


class TaskMonitor(Protocol):
    """Contract for monitoring and controlling long-running GIS engine tasks."""

    def is_cancelled(self) -> bool:  # pragma: no cover - interface
        """Return True if task processing should stop early."""
        ...

    def update_progress(
        self, percent: int, phase: str | None = None, description: str | None = None
    ) -> None:  # pragma: no cover - interface
        """Report progress percentage (0-100) with optional phase and description."""
        ...

    def record_error(
        self,
        error_msg: str,
        phase: str | None = None,
        percent: int | None = None,
        description: str | None = None,
    ) -> None:  # pragma: no cover - interface
        """Record an error event with optional phase, percent and description."""
        ...

    def record_file(self, file_type: str, file_path: str) -> None:  # pragma: no cover - interface
        """Record a generated file with type and path."""
        ...


class EmptyTaskMonitor:
    def is_cancelled(self) -> bool:
        return False

    def update_progress(
        self, percent: int, phase: str | None = None, description: str | None = None
    ) -> None:
        logger.info(f"Progress update: {percent}% - Phase: {phase} - Description: {description}")

    def record_error(
        self,
        error_msg: str,
        phase: str | None = None,
        percent: int | None = None,
        description: str | None = None,
    ) -> None:
        logger.error(
            f"Error occurred: {error_msg} - Phase: {phase} - Percent: {percent} - Description: {description}"
        )

    def record_file(self, file_type: str, file_path: str) -> None:
        logger.info(f"File recorded: {file_type} - Path: {file_path}")
