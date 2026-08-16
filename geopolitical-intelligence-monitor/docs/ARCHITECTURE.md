# CLIM Architecture

CLIM uses a modular pipeline.

```text
Source Registry
     ↓
Collectors
     ↓
IntelligenceEvent
     ↓
Watch Classifier
     ↓
Significance Engine
     ↓
SQLite Storage
     ↓
Brief / Dashboard
```

## Boundaries

### Models
Defines normalized domain objects used by all modules.

### Collectors
Fetch and normalize public-source data. Collectors do not write directly to the database.

### Intelligence
Classifies and scores normalized events. Rules should remain explainable.

### Storage
Persists events and handles deduplication.

### Watchlists
Defines monitored theaters and matching terms.

### Application
Coordinates the pipeline without embedding collector, scoring, or database logic.

## Design rule

Dependencies flow inward toward the shared event model. No collector should need to know how the dashboard works, and no dashboard should need to know how RSS parsing works.
