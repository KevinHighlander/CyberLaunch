# Lecture Downloader

A safe Python utility for downloading newly posted lecture and discussion files
from course pages you are authorized to access or from direct file links.

It does **not** bypass logins, access controls, CAPTCHAs, paywalls, or other site
protections. Use it only where your school and course platform permit automated
downloads.

## Features

- Finds PDF, PowerPoint, Keynote, and Word links on permitted course pages
- Uses a private browser profile for signed-in Campuswire Files pages
- Accepts direct file URLs
- Saves files in a separate folder for each course
- Records previously seen URLs
- Detects duplicate file contents with SHA-256 hashes
- Offers baseline and dry-run modes
- Keeps configuration, download history, and logs out of Git
- Can read permitted session headers or cookies from environment variables
- Blocks off-site links discovered on pages unless their hosts are explicitly allowed
- Enforces configurable timeouts and file-size limits

## Project files

```text
lecture-downloader/
├── lecture-downloader.py
├── config.example.json
├── requirements.txt
└── README.md
```

Your private `config.json`, downloads, logs, and history are ignored by Git.

## Setup

Requires Python 3.10 or newer.

```bash
cd ~/CyberLaunch/lecture-downloader
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m playwright install chromium
cp config.example.json config.json
```

Edit `config.json` and replace the example URLs with course pages or direct
links you are allowed to download.

For Campuswire, use each class's Files-page URL, not an individual PDF:

```text
https://campuswire.com/c/COURSE-ID/modules/files
```

## Configuration

Each course has:

- `name`: display name used by `--course`
- `folder`: download subfolder
- `sources`: authorized HTML pages and/or direct file URLs
- `allowed_hosts`: optional hosts for legitimate file/CDN links discovered on
  the course page
- `tab_names`: optional Modules tabs to open, such as `["All Files"]`
- `auth`: optional environment-variable mappings

The default download location is:

```text
~/Downloads/CyberLaunch Lectures/<course folder>/
```

Private history and logs are stored under:

```text
~/.local/share/lecture-downloader/
```

The saved Campuswire browser session is stored privately under:

```text
~/.local/share/lecture-downloader/browser-profile/
```

It remains on your Mac and is not part of the Git repository.

### Authentication, when permitted

Do not put passwords, tokens, or cookie values in `config.json`. If your course
platform explicitly permits a user-provided session token, map an environment
variable to the required header or cookie:

```json
"auth": {
  "headers_from_env": {
    "Authorization": "COURSE_AUTHORIZATION"
  },
  "cookies_from_env": {
    "session": "COURSE_SESSION_COOKIE"
  }
}
```

Then set the value only in your current Terminal session:

```bash
export COURSE_AUTHORIZATION='Bearer value-provided-by-your-platform'
export COURSE_SESSION_COOKIE='value-provided-by-your-platform'
```

Never commit these values, paste them into an issue, or share them.

### Campuswire sign-in

After adding all Campuswire Files-page URLs to `config.json`, run:

```bash
python3 lecture-downloader.py --login
```

A private Chromium window opens. Sign in to Campuswire normally, wait until the
Files page appears, return to Terminal, and press Return. The program saves the
resulting browser session locally. It does not read or store your password in
the project.

Campuswire tabs with the standard `tab` role are scanned automatically. If a
course keeps files behind a custom Modules tab, add its visible name:

```json
"tab_names": ["All Files"]
```

Campuswire may store instructor-provided external documents in its official
Amazon S3 bucket. Add that exact host only for a course that uses it:

```json
"allowed_hosts": [
  "files.campuswire.com",
  "campuspro-data.s3.us-east-1.amazonaws.com"
]
```

## First run

To mark everything currently posted as already seen without downloading it:

```bash
python3 lecture-downloader.py --baseline
```

To preview new links without downloading:

```bash
python3 lecture-downloader.py --dry-run --visible
```

To download new files:

```bash
python3 lecture-downloader.py
```

To process one configured course:

```bash
python3 lecture-downloader.py --course "ENGL 200"
```

For detailed logging in Terminal:

```bash
python3 lecture-downloader.py --verbose
```

The `--visible` option shows the Campuswire browser during a scan and is useful
for troubleshooting. Normal scans reuse the same session in the background.

If Campuswire reports zero supported links even though files are visible, run:

```bash
python3 lecture-downloader.py --dry-run --visible --diagnose
```

This saves a private HTML snapshot and screenshot under:

```text
~/.local/share/lecture-downloader/debug/
```

These diagnostics can contain course names and filenames. Keep them private;
do not upload them to GitHub or share them publicly.

## Duplicate detection

The program first skips URLs already recorded in its private state. When a new
URL returns a file whose SHA-256 hash matches an earlier download, the temporary
file is deleted and recorded as a duplicate. Different files with the same name
receive numbered filenames rather than overwriting existing work.

If a download fails, its URL is not marked complete, so a later run can retry it.

## Limitations

- A Campuswire interface change may require updating the link discovery logic.
- Some learning-management systems prohibit scraping or require an official API.
- Signed download URLs may expire.
- A successful request does not imply that automation is permitted; follow your
  institution's rules.

For unsupported authenticated pages, use the platform's official download
feature or add authorized direct links to `sources`.

## GitHub workflow

Review changes first:

```bash
cd ~/CyberLaunch
git status
git diff -- lecture-downloader
```

Commit only this project:

```bash
git add lecture-downloader
git commit -m "Build safe Lecture Downloader"
git push
```

Before committing, confirm that `config.json`, secrets, downloaded class
materials, state files, and logs are not listed by `git status`.
