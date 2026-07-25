# Lab 03: Linux Authentication Log Analysis

## Objective

Review synthetic and local Linux authentication records, summarize successful
and failed SSH activity, and identify privileged command use.

## Safety boundary

Read logs only on your own Linux VM. Do not collect logs from shared or
third-party systems. Logs may expose account names and addresses.

## Setup

Python 3.10 or newer is sufficient for the synthetic sample:

```bash
python3 ../tools/auth_log_summary.py ../samples/linux-auth.log
```

On a Debian/Ubuntu lab VM, authentication records are commonly in
`/var/log/auth.log`. On Fedora/RHEL systems, they may be in
`/var/log/secure` or the system journal. Access depends on local permissions.

## Procedure

1. Run the helper against the provided synthetic sample.
2. Review each source line and verify the counts.
3. On your own VM, optionally copy a small, relevant time-bounded excerpt to a
   secure working location.
4. Replace usernames and addresses before using the helper or report.
5. Record accepted SSH, failed SSH, invalid-user, and sudo events.

Read-only journal query for a local lab VM:

```bash
journalctl --since "1 hour ago" -u ssh --no-pager
```

The service may be named `sshd` on some distributions.

## Expected observations

The synthetic sample contains one accepted SSH login, two failed logins for an
invalid user, and one sudo event. Repeated failures can justify investigation,
but context is required before assigning severity.

## Deliverable

Include the sanitized summary, a short event timeline, and two defensive
recommendations such as key-based authentication, rate limiting, or
centralized logging.

## Cleanup

Remove temporary raw excerpts after the report is complete, following your
evidence-retention needs.

