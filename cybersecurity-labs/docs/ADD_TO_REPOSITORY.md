# Add This Section to CyberLaunch

The intended destination is:

```text
CyberLaunch/
└── cybersecurity-labs/
```

## Before copying

From the CyberLaunch repository, inspect current work:

```bash
cd ~/CyberLaunch
git status
```

Do not overwrite an existing `cybersecurity-labs` folder without reviewing
and preserving its contents. Copy this complete folder into the repository
using Finder or your editor.

## Review

From `~/CyberLaunch`:

```bash
git status
git diff -- cybersecurity-labs
```

Run the local checks:

```bash
python3 -m compileall -q cybersecurity-labs/tools
python3 cybersecurity-labs/tools/auth_log_summary.py cybersecurity-labs/samples/linux-auth.log
python3 cybersecurity-labs/tools/eml_summary.py cybersecurity-labs/samples/safe-phishing-sample.eml
```

Review the staged files before publishing:

```bash
git add cybersecurity-labs
git diff --cached --stat
git diff --cached
```

Confirm that the staged content contains no credentials, personal
information, private raw logs, or real target details.

## Commit and push

```bash
git commit -m "Add defensive cybersecurity lab portfolio"
git push
```

If `git status` showed unrelated changes, stage only
`cybersecurity-labs` as shown above. Do not use `git add .` unless every
change in the repository has been reviewed and belongs in the same commit.

