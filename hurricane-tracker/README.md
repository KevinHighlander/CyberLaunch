# Atlantic Hurricane Tracker

A beginner-friendly Python command-line project that creates a plain-text
Atlantic tropical-weather briefing from official National Hurricane Center
(NHC) RSS feeds.

## What it does

- Reads the NHC Atlantic tropical-cyclone feed.
- Identifies cyclone-specific advisory products, when present.
- Includes entries from the NHC Graphical Tropical Weather Outlook feed.
- Saves a readable report in `output/atlantic_hurricane_report.txt`.
- Offers a fictional offline sample so the project can be tested without
  internet access or an active storm.
- Requires no account, API key, or secret.

This is a portfolio and educational project—not an emergency-alert service.
Always use current NHC products and local emergency-management instructions
for safety decisions.

## Official data sources

The script uses public feeds published by NOAA's National Hurricane Center:

- [Atlantic Basin Tropical Cyclones RSS](https://www.nhc.noaa.gov/index-at.xml)
- [Atlantic Tropical Weather Outlook RSS](https://www.nhc.noaa.gov/xml/TWOAT.xml)
- [NHC RSS documentation](https://www.nhc.noaa.gov/aboutrss.shtml)

NHC controls the feeds and may change their availability or structure. The
tracker reports connection and parsing errors clearly instead of silently
showing old data. It does not cache a live report.

## Requirements

- Python 3.10 or newer
- Internet access for live mode

There are no third-party Python packages to install. `requirements.txt`
documents that intentionally.

## Run it

Open Terminal and enter:

```bash
cd ~/CyberLaunch/hurricane-tracker
python3 hurricane-report.py --print
```

The report appears in Terminal and is also saved to:

```text
output/atlantic_hurricane_report.txt
```

To choose a different output file:

```bash
python3 hurricane-report.py --print --output ~/Desktop/hurricane-report.txt
```

## Test safely with offline sample data

Sample mode makes no internet request and uses clearly labeled fictional data:

```bash
python3 hurricane-report.py --sample --print
```

Compare the result with `sample-output.txt`. A successful run ends with a
`Saved report:` message. Then check the process result:

```bash
echo $?
```

`0` means the program completed successfully. An unavailable feed, invalid
feed, or unwritable output location produces a helpful message and returns
`1`.

For a syntax check:

```bash
python3 -m py_compile hurricane-report.py
```

## Command options

```text
--print              show the report in Terminal
--sample             use fictional bundled data and stay offline
-o, --output PATH    choose the saved report path
--timeout SECONDS    change the live-request timeout
-h, --help           show built-in help
```

## Project files

```text
hurricane-tracker/
├── hurricane-report.py   # main program
├── README.md             # setup, usage, and source documentation
├── requirements.txt      # confirms there are no external dependencies
└── sample-output.txt     # expected shape of an offline sample report
```

The generated `output/` folder is excluded from Git because reports change
each time the program runs.

## Privacy and secrets

This project needs no credentials. Do not add passwords, tokens, `.env` files,
or private location data. The main CyberLaunch `.gitignore` excludes common
secret and generated files.

## Limitations

- An RSS entry is a pointer to an official product, not a complete risk
  assessment.
- A missing cyclone-specific entry does not guarantee that tropical weather
  poses no threat.
- Feed wording and structure are controlled by NHC.
- The script does not send notifications or run automatically.

## Possible future improvements

- Optional desktop notifications
- Scheduled daily reports
- Structured JSON output
- Tests with saved, sanitized RSS fixtures
- A map that links to official NHC forecast graphics
