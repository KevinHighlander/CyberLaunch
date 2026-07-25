# Apple Shortcuts and iPad Setup

The Python program cannot directly monitor the private Apple Notes database.
Use the Notes share sheet and Apple Shortcuts to place an export in a shared
iCloud Drive inbox.

## Prepare the folders

1. Open the Files app on the iPad.
2. In iCloud Drive, create a folder named `Note Exports`.
3. Optionally create `Organized Notes`; the Python program can also create it.
4. Use these same folder locations in `config.json` on the Mac.

Allow iCloud Drive to finish syncing before the first test.

## Build the recommended Shortcut

Open Shortcuts on the iPad and create a shortcut named **Export Note for
CyberLaunch**.

Add these actions in order:

1. **Receive input from Share Sheet**
   - Enable the shortcut in the Share Sheet.
   - Accept Notes, rich text, text, images, and PDFs where the installed iPadOS
     version offers those choices.
2. **Choose from Menu**
   - Add one choice per configured subject, such as `Math`, `English`, and
     `Cybersecurity`.
   - Store the selected choice in a `Subject` variable.
3. **Ask for Input**
   - Prompt: `Name this note`
   - Input type: Text
   - Store the answer in a `Title` variable.
4. **Make PDF**
   - Input: Shortcut Input
   - Include the note content and attachments when iPadOS makes them available.
5. **Set Name**
   - Name: `[Subject] - [Title].pdf`
   - Insert the Subject and Title variables; do not type the brackets.
6. **Save File**
   - Destination: `iCloud Drive/Note Exports`
   - Turn off **Ask Where to Save** for a consistent inbox.
   - Keep **Overwrite If File Exists** off.
7. Optional: **Show Notification**
   - Message: `Note queued for organization`

Exact action names can vary slightly with iPadOS language and release. Search
the Shortcuts action picker for `PDF`, `Name`, and `Save File` if the labels
differ.

## Use the Shortcut

1. Open and unlock the note.
2. Tap Share.
3. Select **Export Note for CyberLaunch**.
4. Select the subject and enter a descriptive title.
5. Wait for the confirmation and iCloud synchronization.

The saved file might be named:

```text
Math - Limits Practice.pdf
```

The Python program maps `Math` to the configured `Math Assignments` folder.

## Optional automation

iPadOS personal automations generally cannot trigger solely because an Apple
Note changed. A reliable workflow is user-initiated sharing from Notes.

On the Mac, the Python watcher may run continuously from Terminal. Advanced
users can create a macOS LaunchAgent later, but first confirm that `--once` and
normal watch mode work correctly. A background service must have permission to
access iCloud Drive and its paths must match `config.json`.

## When Make PDF is unavailable

Depending on the content and iPadOS version, Notes may expose text, an image, or
a scanned PDF differently. Use one of these alternatives:

- From Notes, choose **Markup** or **Print**, expand the preview, then share/save
  the resulting PDF.
- Save an image or text export into `Note Exports`; the Python program can
  convert supported formats.
- For scans and handwriting, prefer Apple-generated PDF output to preserve
  layout.

## Privacy

Do not export locked or sensitive notes into a folder synchronized to machines
you do not control. Never commit the inbox, organized notes, configuration with
personal paths, or log files to GitHub.

