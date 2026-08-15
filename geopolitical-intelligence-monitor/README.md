# CyberLaunch Intelligence Monitor (CLIM)

CLIM is an open-source OSINT and geopolitical intelligence platform designed to transform public information into explainable, evidence-based assessments.

## Mission

Transform public information into explainable, evidence-based intelligence assessments.

## Core principles

- **Evidence first:** every assessment should be traceable to source material.
- **Explainability:** scores and classifications should have understandable reasons.
- **Human in the loop:** CLIM supports analysts; it does not replace them.
- **Modular architecture:** collection, intelligence, storage, and presentation stay loosely coupled.
- **Security by default:** secrets and runtime data are never committed.
- **Verify before trusting:** provenance matters, including for official sources and AI output.

## Initial watch areas

- Taiwan Strait
- Korean Peninsula
- Iran / Middle East
- Russia–Japan / Kuril Islands

## Pipeline

```text
Sources
  ↓
Collection
  ↓
Normalization
  ↓
Deduplication
  ↓
Watch Classification
  ↓
Significance Scoring
  ↓
Correlation
  ↓
Confidence
  ↓
Analyst Brief
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Run:

```bash
python3 -m app.main
```

Validate:

```bash
python3 -m ruff check app tests
python3 -m pytest
```

CLIM is currently in **Operation Genesis**, the clean v0.1 foundation phase.
