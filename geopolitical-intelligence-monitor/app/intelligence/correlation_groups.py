"""Multi-report event grouping for CLIM."""

from __future__ import annotations

from dataclasses import dataclass

from app.intelligence.correlation import correlate
from app.models.normalized_event import NormalizedEvent


@dataclass(frozen=True, slots=True)
class CorrelationGroup:
    """A set of reports believed to describe the same event."""

    group_id: str
    events: tuple[NormalizedEvent, ...]

    @property
    def source_count(self) -> int:
        """Return the number of unique reporting sources."""
        return len(
            {
                event.source_name
                for event in self.events
            }
        )

    @property
    def event_count(self) -> int:
        """Return the number of reports in the group."""
        return len(self.events)

    @property
    def source_names(self) -> tuple[str, ...]:
        """Return unique source names in deterministic order."""
        return tuple(
            sorted(
                {
                    event.source_name
                    for event in self.events
                }
            )
        )

    @property
    def is_corroborated(self) -> bool:
        """Return whether multiple independent sources support the group."""
        return self.source_count >= 2


def _belongs_to_group(
    event: NormalizedEvent,
    group_events: list[NormalizedEvent],
    threshold: float,
) -> bool:
    """
    Return whether an event sufficiently matches a correlation group.

    An event joins the group when it matches at least one existing report.
    """
    return any(
        correlate(
            event,
            existing,
        ).score >= threshold
        for existing in group_events
    )


def group_events(
    events: list[NormalizedEvent],
    *,
    threshold: float = 0.40,
) -> tuple[CorrelationGroup, ...]:
    """Cluster normalized reports into likely real-world events."""
    if not events:
        return ()

    raw_groups: list[list[NormalizedEvent]] = []

    for event in events:
        matching_group: list[NormalizedEvent] | None = None

        for group in raw_groups:
            if _belongs_to_group(
                event,
                group,
                threshold,
            ):
                matching_group = group
                break

        if matching_group is None:
            raw_groups.append([event])

        else:
            matching_group.append(event)

    groups: list[CorrelationGroup] = []

    for index, group in enumerate(
        raw_groups,
        start=1,
    ):
        groups.append(
            CorrelationGroup(
                group_id=f"event-group-{index}",
                events=tuple(group),
            )
        )

    return tuple(groups)