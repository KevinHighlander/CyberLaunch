# Atlantic Hurricane Tracker V2

A Pyto/iPhone-friendly Python script that turns official NOAA weather feeds
into a daily Atlantic tropical-weather briefing. It focuses on disturbances
coming off Africa, active Atlantic cyclones, and alerts affecting Florida,
Georgia, South Carolina, North Carolina, and Virginia.

This is a briefing aid, not an emergency-warning service or a landfall
forecast. Always follow official NHC/NWS products and local public-safety
instructions.

## Version 2 highlights

- Uses the NHC Atlantic Tropical Weather Outlook and Tropical Weather
  Discussion RSS feeds.
- Uses NHC's machine-readable `CurrentStorms.json` feed and keeps only Atlantic
  systems.
- Checks the NWS active-alert API for FL, GA, SC, NC, and VA.
- Summarizes the situation in a 30-second quick look.
- Organizes disturbances, tropical waves, and storms into practical Atlantic
  zones.
- Compares each run with the prior snapshot and explains meaningful changes.
- Saves a current report, daily archive, and 30-snapshot JSON history.
- Prints `ALERT_REQUIRED=true` or `false` for Apple Shortcuts.
- Redirects away from Pyto's read-only Inbox to a writable Documents folder.
- Uses only Python's standard library—no package installation or API keys.
- Marks the report `GRAY — DATA UNAVAILABLE` instead of falsely reporting quiet
  conditions when every core NHC feed fails.

## Official data sources

- [NHC Atlantic Tropical Weather Outlook RSS](https://www.nhc.noaa.gov/xml/TWOAT.xml)
- [NHC Atlantic Tropical Weather Discussion RSS](https://www.nhc.noaa.gov/xml/TWDAT.xml)
- [NHC Current Storms JSON](https://www.nhc.noaa.gov/CurrentStorms.json)
- [NHC RSS documentation](https://www.nhc.noaa.gov/aboutrss.shtml)
- [NHC current-product documentation](https://www.nhc.noaa.gov/productexamples/)
- [NWS alerts API documentation](https://www.weather.gov/documentation/services-web-alerts)

## Requirements

- Python 3.10 or newer
- Internet access for live reports

There are no third-party dependencies. Leave `requirements.txt` as it is.

## Run on a computer

From the repository:

```bash
cd hurricane-tracker
python3 hurricane-report.py --output-dir ./output
```

To print the complete report:

```bash
python3 hurricane-report.py --output-dir ./output --print
```

The script writes:

```text
output/
├── latest_report.txt
├── report_YYYY-MM-DD.txt
└── hurricane_state.json
```

The first run creates the comparison baseline. Later runs explain what changed.
The generated `output/` directory is ignored by Git.

## Test without internet

The built-in demonstration is fictional and makes no network requests:

```bash
python3 hurricane-report.py --sample --output-dir ./output/demo --print
```

It exercises a disturbance, an African tropical wave, an Atlantic tropical
storm, a coastal alert, report generation, and the Shortcuts flag. It is
clearly labeled as demonstration data.

Run the automated tests:

```bash
python3 -m unittest discover -s tests -v
```

For a quick syntax check:

```bash
python3 -m py_compile hurricane-report.py
```

## Install or update on iPhone/Pyto

### First-time install

1. Install **Pyto** from the App Store.
2. Download `hurricane-report.py` from this repository.
3. In the iPhone Files app, create:
   `On My iPhone > Pyto > Hurricane Report Script`
4. Move `hurricane-report.py` into that folder.
5. Open that saved copy in Pyto and tap **Run**.

Do not run the imported copy from Pyto's `Inbox`; iOS treats that location as
read-only. Even if the script is accidentally opened there, Version 2 tries
writable fallback folders instead of saving reports beside the script.

The normal report location is:

```text
On My iPhone/Pyto/Hurricane Reports/
```

### Replace Version 1 with Version 2

1. Download the new `hurricane-report.py`.
2. Open **Files > On My iPhone > Pyto > Hurricane Report Script**.
3. Press and hold the old `hurricane-report.py`, choose **Rename**, and call it
   `hurricane-report-v1-backup.py`.
4. Move the newly downloaded `hurricane-report.py` into the same folder.
5. Open the new file in Pyto and tap **Run**.
6. Confirm the output ends with both `Report saved:` and
   `ALERT_REQUIRED=true` or `ALERT_REQUIRED=false`.
7. Open `Hurricane Reports/latest_report.txt` and confirm its heading says
   `ATLANTIC HURRICANE REPORT — VERSION 2`.
8. After the new version works, you may keep or delete the backup.

Renaming first makes the update recoverable and prevents iOS from creating an
ambiguous filename such as `hurricane-report (1).py`.

## Create the Apple Shortcut

Pyto action names can vary slightly by version:

1. Open **Shortcuts** and create **Atlantic Hurricane Report**.
2. Add Pyto's **Run Script** action.
3. Select the new `hurricane-report.py`.
4. Leave arguments empty.
5. Add an **If** action: if the Pyto result contains
   `ALERT_REQUIRED=true`.
6. In the Yes branch, add **Show Notification**:
   `The Atlantic briefing has a meaningful change.`
7. Optionally add **Quick Look** or **Open File** for `latest_report.txt`.

To display the entire report as the script result, pass:

```text
--print
```

For a daily run, add a **Time of Day** automation, select **Run Immediately**,
and run the shortcut. Test once with the phone unlocked before relying on
background execution.

## Notification rules

`ALERT_REQUIRED=true` is printed when, for example:

- A new Atlantic storm or relevant state alert appears.
- A new disturbance is already at 40% or greater formation probability.
- Formation probability reaches 40% or rises by at least 20 points.
- An active cyclone strengthens or changes classification.
- The overall status increases.
- All three core NHC feeds become unavailable.

Reports are saved even when the flag is false.

## Updating the tracked file in Git

After editing or replacing the script locally:

```bash
git status
git diff -- hurricane-tracker/hurricane-report.py
python3 -m unittest discover -s hurricane-tracker/tests -v
git add hurricane-tracker/
git commit -m "Upgrade Atlantic hurricane tracker to Version 2"
git push origin main
```

Review `git diff` before committing. Do not add the generated `output/` folder
or personal `hurricane_state.json`; the repository's `.gitignore` excludes
`hurricane-tracker/output/`.

## Project files

```text
hurricane-tracker/
├── hurricane-report.py
├── README.md
├── requirements.txt
├── sample-output.txt
└── tests/
    └── test_hurricane_report.py
```

## Optional controls

```text
--print, --print-report    print the complete report
--sample                   use fictional offline data
--output-dir FOLDER        choose the report folder
--fixtures FOLDER          use saved feed fixtures for development
-h, --help                 show command help
```

Advanced users can also set the `HURRICANE_REPORT_DIR` environment variable to
choose a report directory.

## Privacy and limitations

The script needs no credentials and sends no personal data. Feed structures and
wording can change, individual sources can fail, and automated text parsing can
miss nuance. A missing system is not a safety guarantee. Use the official links
inside each report when making decisions.
