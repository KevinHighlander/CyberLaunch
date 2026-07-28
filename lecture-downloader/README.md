# Lecture Downloader

A safe, platform-neutral Python utility for collecting course files you are
already authorized to download. It supports user-supplied direct HTTPS URLs,
static HTML exports, and JSON manifests, with a complete offline sample.

This project does **not** log in, automate a browser, scrape a named learning
platform, bypass authentication or DRM, defeat access controls, or ignore site
terms. If a platform requires authentication, use its official export/download
feature or an authorized API to produce a manifest or static HTML export.

## Highlights

- HTTPS-only remote downloads with an explicit host allowlist
- Local manifest and HTML-export support
- Extension and maximum-size enforcement
- SHA-256 duplicate detection and collision-safe filenames
- Persistent history so completed URLs are not downloaded twice
- Dry-run and baseline modes
- No credentials, cookies, or tokens in configuration
- Automated tests requiring no network access

## Project layout

```text
lecture-downloader/
├── lecture_downloader.py
├── lecture-downloader.py
├── config.example.json
├── requirements.txt
├── samples/
│   ├── config.sample.json
│   ├── manifest.json
│   └── fixtures/
└── tests/
```

## Setup and sample

Requires Python 3.10 or newer.

```bash
cd ~/CyberLaunch/lecture-downloader
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 lecture-downloader.py --sample
```

The sample copies one local fixture to `samples/output/Sample Course/` and
reports the identical second fixture as a duplicate. Both output and sample
state are ignored by Git. Remove those generated folders/files to replay it.

## Configure an authorized source

```bash
cp config.example.json config.json
```

Edit the private, Git-ignored `config.json`. Supported source types:

- `manifest`: local JSON export containing `{"files": [...]}`. Entries can be
  URL strings or `{"url": "...", "filename": "..."}` objects.
- `html`: local static HTML export. Supported file links are discovered.
- `html_url`: public/authorized HTTPS HTML page with no login automation.
- `url`: an authorized direct HTTPS file URL.

Relative local paths are resolved from the config file's directory. Every
remote hostname—including a redirect destination—must appear in
`allowed_hosts`. HTTP, embedded URL credentials, and unlisted hosts are rejected.

Do not place passwords, session cookies, API tokens, or signed private URLs in a
committed file. For authenticated systems, prefer an official export or API
client and keep that separate from this downloader.

## Run

```bash
# Preview without writing downloads or state
python3 lecture-downloader.py --dry-run

# Mark currently listed files as seen
python3 lecture-downloader.py --baseline

# Download new files
python3 lecture-downloader.py

# Use another config
python3 lecture-downloader.py --config /path/to/private-config.json
```

Failures return a nonzero exit status. A failed URL is not marked complete, so
the next run can retry it.

## Test

```bash
python3 -m unittest discover -s tests -v
```

All tests are offline and use temporary directories.

## Example output

```text
DOWNLOADED [Sample Course] .../samples/output/Sample Course/Week 01 Notes.txt
DUPLICATE [Sample Course] fixtures/week-01-copy.txt
```

## Git guidance

The project `.gitignore` excludes virtual environments, private config,
downloads, state, logs, and sample output. Before committing:

```bash
cd ~/CyberLaunch
git status --short
git diff -- lecture-downloader
git check-ignore -v lecture-downloader/config.json
git add lecture-downloader
git commit -m "Build safe Lecture Downloader"
```

Use the path-scoped `git add` shown above so unrelated repository work—such as
`hurricane-tracker` changes—is not included.
