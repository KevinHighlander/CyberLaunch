# Lab 02: Windows Log Analysis

## Objective

Export a small set of Windows security events from a lab VM and distinguish
successful sign-ins, failed sign-ins, and process creation.

## Safety boundary

Use your own Windows VM and synthetic activity. Event logs can contain
usernames, hostnames, IP addresses, and command lines; sanitize all exports
before committing them.

## Setup

1. Start a Windows lab VM.
2. Open **Event Viewer → Windows Logs → Security**.
3. Generate one normal sign-in and one intentionally mistyped password on
   your own test account.
4. If process creation auditing is not enabled, treat event 4688 as an
   optional observation rather than changing policy for this lab.

## Procedure

In Event Viewer, use **Filter Current Log** and enter:

```text
4624,4625,4688
```

Relevant event IDs:

- `4624`: successful account sign-in
- `4625`: failed account sign-in
- `4688`: new process created, when auditing is enabled

Select a few events and record the UTC time, event ID, account placeholder,
source placeholder, and interpretation. Export only the events needed for the
exercise.

Optional PowerShell read-only query in the lab VM:

```powershell
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4624,4625,4688; StartTime=(Get-Date).AddHours(-1)} -MaxEvents 30 |
  Select-Object TimeCreated, Id, ProviderName, LevelDisplayName, Message
```

This may require an elevated Event Viewer or PowerShell window to read the
Security log. It does not change the log.

## Expected observations

Use `../samples/windows-events.csv` to practice before handling a real export.
A single failed sign-in is not automatically malicious; assess frequency,
source, account, timing, and surrounding events.

## Deliverable

Document:

- Three events and what each means
- Which fields would help build a timeline
- One benign explanation and one security-relevant explanation for event 4625
- A recommendation such as alerting on repeated failures

## Cleanup

Store original exports outside the repository. Commit only a sanitized report.

