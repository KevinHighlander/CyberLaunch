# iPad Notes Converter

A local Python organizer for notes exported from an iPad. It watches an inbox
folder, converts supported exports to PDF, files the PDFs into subject folders,
and records every action in a log.

This project does **not** read the private Apple Notes database. Apple Notes
should export or share a note into the watched folder first. The recommended
workflow is an Apple Shortcut that creates a PDF and saves it to an iCloud Drive
folder.

## What it does

- Watches a designated folder for new exports
- Accepts PDF, PNG, JPG/JPEG, TIFF, plain text, and Markdown files
- Copies PDFs without recompressing them
- Converts images and text documents to PDF
- Routes exports into user-defined subject folders
- Uses a filename prefix, such as `Math -`, or configurable keyword rules
- Moves unrecognized or unsupported files to an `_Unsorted` folder
- Avoids overwriting existing PDFs
- Logs processing activity and errors
- Provides a one-time scan mode for testing or automation

## Project layout

```text
ipad-notes-converter/
├── config.example.json
├── docs/
│   └── apple-shortcuts.md
├── MAIN.py
├── requirements.txt
├── tests/
│   └── test_converter.py
└── README.md
```

Runtime folders are created outside this project wherever you choose in the
configuration file.

## Requirements

- Python 3.10 or newer
- macOS for the intended Apple Notes/iCloud workflow
- Pillow for image-to-PDF conversion
- ReportLab for text-to-PDF conversion
- watchdog for continuous folder monitoring

## Installation

From the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
cp config.example.json config.json
```

Open `config.json` and replace the example paths with absolute paths on your
Mac. A typical iCloud Drive inbox path is:

```text
/Users/YOUR_NAME/Library/Mobile Documents/com~apple~CloudDocs/Note Exports
```

The destination can also be in iCloud Drive:

```text
/Users/YOUR_NAME/Library/Mobile Documents/com~apple~CloudDocs/Organized Notes
```

macOS may ask Terminal, Python, or your editor for permission to access iCloud
Drive. Approve access only for the application you are using.

## Configuration

The included `config.example.json` contains:

- `inbox`: folder watched for new exports
- `destination`: root folder containing organized subjects
- `default_subject`: folder used when no rule matches
- `poll_interval_seconds`: fallback/rescan interval
- `settle_seconds`: wait time to ensure iCloud finished writing a file
- `keep_originals`: whether to retain processed source files
- `log_file`: activity log location
- `subjects`: routing rules and keywords

Subject matching works in this order:

1. A filename prefix before ` - `, such as `Math - Chapter 4.pdf`
2. Configured subject keywords found in the filename
3. The configured default subject

For example:

```text
Math - Homework 07.pdf
```

is filed under:

```text
Organized Notes/Math Assignments/Homework 07.pdf
```

## Usage

Validate the configuration without changing files:

```bash
python3 MAIN.py --config config.json --check
```

Process everything currently in the inbox, then exit:

```bash
python3 MAIN.py --config config.json --once
```

Watch continuously:

```bash
python3 MAIN.py --config config.json
```

Preview routing and conversion without writing or moving files:

```bash
python3 MAIN.py --config config.json --once --dry-run
```

Process one specific export:

```bash
python3 MAIN.py --config config.json --file "/path/to/Math - Homework 07.pdf"
```

Stop continuous watch mode with `Control+C`.

## Supported files

| Input | Result |
|---|---|
| `.pdf` | Copied as-is |
| `.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff` | Converted to PDF |
| `.txt`, `.md` | Rendered as a basic text PDF |
| Other formats | Moved to `_Unsorted/Unsupported` |

Apple Notes attachments, drawings, scans, handwriting, and rich formatting are
best preserved when the Shortcut creates the PDF on the iPad. Python conversion
of image and text files is intended as a fallback.

## Apple Shortcuts integration

See [docs/apple-shortcuts.md](docs/apple-shortcuts.md) for a recommended
Shortcut and optional Personal Automation. The essential flow is:

```text
Share note → Make PDF → Rename → Save File to Note Exports
```

The filename should begin with a configured subject label, for example:

```text
Math - Calculus Homework 3.pdf
```

## Testing

Install the dependencies, then run:

```bash
python3 -m unittest discover -s tests -v
```

For a safe manual test:

1. Point `config.json` to temporary empty inbox and destination folders.
2. Run with `--check`.
3. Add a small text file named `Math - Test Note.txt` to the inbox.
4. Run with `--once --dry-run` and review the proposed destination.
5. Run with `--once`.
6. Confirm the PDF appears in `Math Assignments` and review the log.

Do not test first with irreplaceable notes. Keep iCloud backups and begin with
copies.

## Privacy and GitHub safety

The project `.gitignore` should exclude `config.json`, logs, exported notes, and
generated PDFs. Do not commit school submissions, personal notes, student data,
credentials, or private iCloud paths. Commit only the example configuration and
sanitized sample names.

## Troubleshooting

- **No files appear:** confirm the Shortcut saves to the exact configured inbox.
- **Permission denied:** allow the terminal/editor to access iCloud Drive in
  macOS Privacy & Security settings.
- **A file is still downloading:** wait for iCloud sync, then run `--once`.
- **Wrong subject:** add a subject prefix or adjust the keyword rules.
- **Duplicate name:** the converter safely adds ` (2)`, ` (3)`, and so on.
- **Unsupported export:** create a PDF in the Shortcut before saving the file.

## Limitations

- Apple does not provide this script direct access to all Apple Notes content.
- Password-protected notes must be unlocked and exported by the user.
- Handwriting recognition and OCR are outside the current scope.
- Text/Markdown conversion preserves readable text, not rich Notes formatting.
- Continuous watching requires the Mac and this program to be running.

## Suggested Git commit

After reviewing `git status` and confirming no private notes are staged:

```bash
git add ipad-notes-converter
git commit -m "Build iPad Notes Converter"
git push
```
