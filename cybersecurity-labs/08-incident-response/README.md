# Lab 08: Incident-Response Documentation

## Objective

Turn sanitized events into a factual incident timeline, evidence register,
and after-action plan.

## Safety boundary

Use the included synthetic timeline or sanitized data from your own lab.
Documentation does not authorize containment changes on production systems.
Any action that changes a real system requires the appropriate owner approval.

## Setup

Copy the templates:

```bash
cp ../templates/incident-report.md ./REPORT.md
cp ../templates/evidence-log.csv ./evidence-log.csv
```

Do not commit these working files until they are sanitized.

## Scenario

A user reports an unexpected sign-in prompt shortly after a failed Windows
sign-in event. An analyst preserves a small event export. The events may be
related, but the available evidence does not prove a common cause.

Use `../samples/incident-timeline.csv` as the evidence source.

## Procedure

1. Assign an incident ID and state the confirmed scope.
2. Copy each event into the report timeline in UTC.
3. Label facts, reports, analyst actions, and hypotheses distinctly.
4. Add the source timeline to the evidence register and calculate its hash:

   ```bash
   shasum -a 256 ../samples/incident-timeline.csv
   ```

   On Linux, `sha256sum` provides the equivalent digest.
5. Propose preservation and containment actions, but identify which actions
   would require authorization.
6. Define recovery validation and two follow-up improvements.

## Deliverable

A completed, sanitized incident report that:

- Separates observed evidence from assumptions
- Uses UTC consistently
- Records evidence provenance
- Names action owners and approval needs
- Includes lessons learned and measurable follow-up work

## Cleanup

Retain only the sanitized portfolio report. Remove duplicate working evidence
when it is no longer required.

