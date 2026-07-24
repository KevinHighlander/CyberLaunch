# ENGL 200 Campuswire Downloader

This Mac utility watches the ENGL 200 Campuswire Files page and downloads only
new PDF, PowerPoint, Keynote, and Word files.

## First-time setup

Open Terminal, type `cd ` (including the space), drag this folder into the
Terminal window, and press Return. Then run:

```bash
chmod +x *.command
./0-install.command
./1-login.command
./2-create-baseline.command
```

The baseline records everything already posted without downloading it.

## Check for new files

```bash
./3-scan-for-new-files.command
```

Downloads are saved to:

```text
~/Downloads/ENGL 200 Slides
```

If a scan cannot see files that are visible on Campuswire, run:

```bash
./4-visible-debug-scan.command
```

Diagnostic files are private because page HTML may contain account or course
information. They are saved under `~/.engl200-campuswire-downloader/debug`.
The saved browser session and history are also kept in that private local
folder. Do not share it or commit it to source control.

## Supported files

`.pdf`, `.ppt`, `.pptx`, `.key`, `.doc`, and `.docx`.

The watcher is preconfigured for:

`https://campuswire.com/c/G7F2FCEEC/modules/files`

