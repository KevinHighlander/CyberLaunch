# Changelog

All notable changes to the CyberLaunch Intelligence Monitor (CLIM) project are documented in this file.

The project follows a milestone-based development model where each version represents a completed engineering objective.

---

# v0.4 — Operation Fusion

**Status:** Complete

## Added

- Pairwise report correlation engine
- Correlation scoring
- Shared-term detection
- Correlation thresholds
- Correlation groups
- Unique source counting
- Corroboration detection
- Correlation integration tests

## Improved

- Intelligence pipeline now supports grouping multiple reports describing the same real-world event.
- Foundation established for intelligence fusion.

## Test Status

**75 Passing Tests**

---

# v0.3 — Operation Atlas

**Status:** Complete

## Added

- Typed source registry
- `IntelligenceSource`
- `NormalizedEvent`
- `AnalyzedEvent`
- Source metadata model
- Pipeline integration tests

## Changed

- RSS collectors now return normalized events.
- Analyzer now produces analyzed events.
- SQLite persistence now stores analyzed events instead of raw collector output.

## Improved

- Complete separation between collection, analysis, and persistence.
- Cleaner architecture with stronger typing.

## Test Status

**67 Passing Tests**

---

# v0.2 — Operation Watchtower

**Status:** Complete

## Added

- Intelligence ontology
- Entity recognition
- Indicator detection
- Theater resolution
- Impact scoring
- Escalation assessment
- Explainable reasoning
- Confidence engine
- Structured enums
- Operational watchlists

## Improved

- Transitioned CLIM from a news collector into an explainable intelligence engine.

## Test Status

**54 Passing Tests**

---

# v0.1 — Operation Genesis

**Status:** Complete

## Added

- Project foundation
- Python virtual environment
- Ruff
- Pytest
- SQLite repository
- RSS collectors
- Event deduplication
- Terminal intelligence brief
- Initial Git workflow

## Test Status

Initial automated test suite established.

---

# Upcoming

Planned future milestones include:

- Correlation confidence integration
- Source diversity scoring
- Contradiction detection
- Government and defense collectors
- Knowledge graph
- Historical event relationships
- Interactive dashboard
- AI-assisted intelligence briefs
- REST API
- Mobile intelligence client