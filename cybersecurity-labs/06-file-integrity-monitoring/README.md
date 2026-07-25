# Lab 06: File Integrity Monitoring

## Objective

Create a cryptographic baseline for harmless training files and identify an
authorized addition, modification, and deletion.

## Safety boundary

Monitor only the temporary lab directory you create. Do not point the helper
at system directories, private documents, or another user's files. The tool
reads file content to calculate SHA-256 hashes and stores no content itself.

## Setup

From the repository root:

```bash
mkdir -p /tmp/cyberlaunch-fim-lab
cp 06-file-integrity-monitoring/training-files/* /tmp/cyberlaunch-fim-lab/
python3 tools/file_integrity.py baseline /tmp/cyberlaunch-fim-lab /tmp/cyberlaunch-fim-baseline.json
```

The baseline is stored outside the monitored folder so it does not monitor
itself.

## Procedure

Make controlled, authorized changes:

```bash
printf "authorized lab change\n" >> /tmp/cyberlaunch-fim-lab/policy.txt
cp /tmp/cyberlaunch-fim-lab/policy.txt /tmp/cyberlaunch-fim-lab/policy-copy.txt
mv /tmp/cyberlaunch-fim-lab/inventory.txt /tmp/cyberlaunch-fim-lab/inventory.removed
```

Compare with the baseline:

```bash
python3 tools/file_integrity.py check /tmp/cyberlaunch-fim-lab /tmp/cyberlaunch-fim-baseline.json
```

The renamed file appears as a deletion and an addition because file integrity
monitoring observes state, not user intent.

## Deliverable

Explain:

- Why a hash change indicates changed bytes but not who changed them
- Why the baseline must be protected
- Which expected changes could create false positives
- How integrity alerts should be combined with logs and change records

## Cleanup

These commands target only the explicitly named temporary lab artifacts:

```bash
rm -r /tmp/cyberlaunch-fim-lab
rm /tmp/cyberlaunch-fim-baseline.json
```

