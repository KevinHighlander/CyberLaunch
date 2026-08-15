# CLIM Development Log

## Operation Genesis

### Clean v0.1 rebuild
The original prototype proved that RSS ingestion, SQLite storage, deduplication, watch classification, and rule-based significance scoring were viable.

The clean v0.1 rebuild reorganizes those lessons into a maintainable architecture with:
- a typed `IntelligenceEvent` model,
- a source registry,
- modular collectors,
- isolated intelligence rules,
- SQLite persistence,
- automated tests,
- Ruff linting and pytest validation.

The prototype is intentionally preserved outside this clean implementation until the migration is validated.
