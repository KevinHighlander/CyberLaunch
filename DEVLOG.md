# CyberLaunch Development Log

## Why I wrote this

I created this log so I would have one honest, readable account of how
CyberLaunch grew, what I built, what broke, what I repaired, and what I learned.
The repository contains the finished files and Git contains the individual
changes, but neither one tells the whole story by itself.

This is written from my point of view. It is a record of my progress, not a
claim that every idea is finished or that every experiment belongs in the final
portfolio.

## How to read the evidence

I use three labels throughout this log:

- **Confirmed in the repository** means the change is present in the local Git
  history or current tracked files.
- **Confirmed in development history** means the work or problem is recorded in
  the related development conversations or command output, even when it is not
  represented by a separate commit on the current branch.
- **Development note** means an idea, plan, or remembered next step. It should
  not be mistaken for completed work.

I use exact dates only where Git records them. Conversation memories are kept
separate when they cannot establish a reliable repository date.

## Current snapshot

The main CyberLaunch repository is a portfolio and learning workspace spanning
Python automation, defensive cybersecurity, stylometry, TypeScript and VS Code
extension development, and Kotlin/Android development.

At the time this log was assembled:

- `main` matched `origin/main` at the commit that added selectable AI code
  review modes to CyberLaunch Assistant.
- Hurricane Tracker was documented as Version 2.0 complete.
- Writing Pattern Analyzer was documented as Version 0.1.0 complete.
- Cybersecurity Labs contained a Version 1.0 set of eight defensive labs.
- iPad Notes Converter was a functional prototype still described as in
  development.
- CyberLaunch OS was documented as Version 0.2.0, with persistent incident
  response progress.
- A separate `feature/personalization` branch was visible in another local
  CyberLaunch checkout. It contained local notes and preference work, but it was
  not part of the canonical checkout's `main` branch, so I do not describe it as
  released.
- Lecture Downloader Version 1.0 was also present. Although it was not one of
  the projects named in the request for this log, it is included because it is
  a substantial verified part of CyberLaunch history.

## Chronological history

### July 24, 2026 — CyberLaunch begins

**Confirmed in the repository:** I created the initial CyberLaunch repository
and its root README. I then expanded the project index so the repository could
act as a portfolio rather than a loose collection of scripts.

The first project added was the Atlantic Hurricane Tracker. Its earliest form
was a Python report script with a README and requirements file. Later that day,
I substantially rebuilt it into a working tracker with official-source access,
plain-text output, documentation, dependency guidance, and a sample report.

I also established the initial multi-project structure. It included folders for
the hurricane tracker, lecture downloader, cybersecurity labs, iPad notes
converter, and an early `ai-submission-detector` placeholder.

The original submission-detector files were empty scaffolding. This matters:
the repository verifies that the idea existed, but it does not verify that an
AI detector had been implemented. I later replaced that framing with a more
scientifically honest Writing Pattern Analyzer.

On the same day, I built the first safe lecture-downloader implementation. It
was designed around legitimate access to course materials, not bypassing
authentication, DRM, access controls, or platform rules.

**Lessons I learned:**

- A repository needs structure and documentation from the beginning.
- A tool's name can overstate what the underlying technology can prove.
- Safety boundaries and privacy rules belong in the design, not as an
  afterthought.
- Generated output, credentials, and local configuration should be excluded
  from Git before they become a problem.

### July 25, 2026 — iPad automation and defensive labs

**Confirmed in the repository:** I built the iPad Notes Converter as a local
Python application with code, configuration examples, Apple Shortcuts guidance,
dependencies, documentation, and automated tests.

The converter was intentionally designed around Apple's supported export/share
workflow. It does not read the private Apple Notes database. Instead, an iPad
Shortcut creates or exports a file into a watched folder, and the Mac-side
program processes it.

I also added the Cybersecurity Labs portfolio. This was not a single demo; it
was a complete defensive learning structure containing:

1. Private-lab network discovery.
2. Windows log analysis.
3. Linux log analysis.
4. Basic vulnerability scanning in an isolated environment.
5. Docker lab setup.
6. File-integrity monitoring.
7. Safe phishing-email analysis.
8. Incident-response documentation.

The labs included safety rules, sanitization guidance, reusable evidence and
incident-report templates, synthetic sample artifacts, a Docker example, and
three local Python helpers for authentication-log summaries, email summaries,
and file-integrity checks.

**Problems addressed:**

- Lab work can expose real usernames, IP addresses, email addresses, tokens, or
  school/work data. I added explicit sanitization guidance and publication-safe
  samples.
- Security exercises can easily drift outside authorized scope. I documented
  ownership, permission, time-window, isolation, and reporting boundaries.
- Notes automation can destroy or misfile irreplaceable material. I added dry
  runs, duplicate-safe naming, logging, quarantine/unsorted handling, and advice
  to test with copies first.

### July 26, 2026 — From “AI detector” to Writing Pattern Analyzer

**Confirmed in the repository:** I removed the empty
`ai-submission-detector` scaffold and initialized the Writing Pattern Analyzer.
I built it incrementally instead of dropping in one unexplained finished
program.

The verified sequence was:

- Create the package structure, tests, README, requirements, and project
  devlog.
- Add tested word tokenization.
- Add vocabulary richness and unique-word measurements.
- Add sentence count and average sentence-length features.
- Add average word length while excluding internal punctuation from the letter
  count.
- Combine the measurements into stylometric profiles.
- Add validated text-file loading and clear missing/invalid-file behavior.
- Compare two profiles with absolute differences and feature similarities.
- Change similarity calculations so they were scale-independent.
- Add a visualization that explains per-feature similarity.
- Add a command-line workflow.
- Add a readable comparison report.
- Package the project with `pyproject.toml`.
- Complete the README and example visualization.

The final framing is deliberately limited: the application measures writing
patterns. It cannot reliably determine whether a document was generated by AI,
and it cannot establish authorship.

**Confirmed debugging notes from the project devlog:**

- One unique-word test expected four words when the correct count was three. I
  learned that a failing test can contain the mistake; I must inspect both the
  implementation and the expectation.
- A sentence tokenizer treated `Dr.` as a complete sentence. The current simple
  punctuation-based approach does not understand abbreviations, decimals, or
  every true sentence boundary.
- A test run initially reported 17 tests instead of 21. I inspected why four
  new punctuation tests were not being discovered, corrected the issue, and
  reran the full set.
- Two deliberately different samples produced nearly identical vocabulary
  richness, and the conversational sample had a slightly longer average
  sentence than the formal sample. I learned to let results challenge my
  expectations instead of forcing the interpretation I predicted.
- The chart originally treated features absent from both samples as 100%
  similar. I changed jointly absent features to “not scored” because a shared
  absence should not be presented as strong evidence of matching styles.
- I encountered unfinished-string prompts such as `dquote>`. I learned that a
  missing quotation mark can cause later terminal input to be interpreted as
  part of the same string, and that the right response is to cancel and inspect
  the quoting.

### July 27, 2026 — Portfolio integration, major upgrades, and Android

**Confirmed in the repository:** I added the Writing Pattern Analyzer and iPad
Notes Converter to the root portfolio index.

I then created CyberLaunch OS. The first commits scaffolded a complete Android
project with the Gradle wrapper, Kotlin build files, Android resources, app
manifest, launcher icons, and application module. I followed that with a
branded Jetpack Compose experience containing:

- A Command Center home screen.
- Compose navigation and shared UI components.
- A Password Lab with testable local scoring.
- A defensive Network Basics module.
- An Incident Response practice screen.
- A dark CyberLaunch theme and adaptive launcher icon.
- Unit tests for password-strength rules.

I added a CyberLaunch OS README, contribution guidance, setup instructions, and
a staged roadmap from a training app toward an optional launcher and, much
later, experimental AOSP work on dedicated hardware.

I repaired an Android build configuration issue by switching to Android's
built-in Kotlin support and removing redundant Kotlin plugin configuration.
That change is preserved as its own commit rather than being hidden inside a
feature commit.

The Hurricane Tracker received its largest upgrade: Version 2. It became a
Pyto/iPhone-friendly Atlantic briefing system using official NOAA/NHC and NWS
machine-readable feeds where practical. It now:

- Tracks Atlantic disturbances, tropical waves, and active cyclones.
- Groups activity into practical Atlantic zones.
- Checks relevant alerts for Florida, Georgia, South Carolina, North Carolina,
  and Virginia.
- Produces a 30-second summary and a full report.
- Compares the current run with saved state and reports meaningful changes.
- Saves `latest_report.txt`, a dated archive, and a bounded JSON history.
- Prints `ALERT_REQUIRED=true` or `false` for Apple Shortcuts.
- Uses only the Python standard library.
- Reports data unavailability instead of falsely describing failed feeds as
  quiet weather.
- Redirects output away from Pyto's read-only Inbox to a writable Documents
  location.

The repository also preserves a Version 1.1 hurricane commit on the
`backup/hurricane-v1.1` branch. That intermediate version added structured JSON,
feed timestamps, status reporting, and offline tests, but Version 2 on `main`
superseded it.

I completed Lecture Downloader Version 1.0 with a safer, smaller implementation,
offline fixtures, a sample manifest, automated tests, HTTPS and host controls,
download limits, duplicate detection, configuration examples, and clearer
documentation.

**Confirmed Git recovery episode:** My local branch and GitHub diverged. The
local branch contained Hurricane Tracker 1.1, GitHub contained later work
including Version 2, and unfinished Lecture Downloader changes were in the
working tree. The work was protected by creating `backup/hurricane-v1.1` and a
stash before reconciling `main` with the remote. Restoring the stash produced a
conflict in the root README. I resolved it by keeping the correct Version 2
status, retained the stash as a temporary backup, and avoided mixing the
superseded hurricane version into the downloader work.

**Lessons I learned:**

- “Divergent branches” is a state to inspect, not a prompt to guess between
  merge and rebase.
- Before a risky Git operation, preserve each distinct line of work in a branch
  or stash.
- A stash conflict does not mean the work is lost.
- Resolve the smallest conflicted file possible, verify the result, and keep a
  recovery point until the replacement commit is safely pushed.
- Mobile file-system permissions are part of application design. A script that
  works on a Mac can still fail in an iOS app's read-only import location.

### July 29–30, 2026 — Stable Android toolchain and persistence

**Confirmed in the repository:** I aligned CyberLaunch OS with a stable Android
36 toolchain and adjusted navigation code to match it. This was a targeted
compatibility repair, not a feature rewrite.

I then made the Incident Response checklist persistent. The work added a
DataStore-backed repository, separated checklist content/progress rules into a
domain model, connected saved progress to the app UI and Command Center, added
a reset action, and added tests for progress conversion.

This moved CyberLaunch OS from a static demonstration toward an app that
remembers training progress between sessions. Its README was updated to call
the current stage Version 0.2.0.

### July 31–August 1, 2026 — CyberLaunch Assistant

**Confirmed in the repository:** I added `cyberlaunch-assistant`, a TypeScript
VS Code extension that sends only the user's selected code to OpenAI for review.
Its first pushed version included secure API-key storage through VS Code's
secret storage, selection and size checks, sensitive-file blocking, an output
channel, provider-error handling, and an AI-powered inspection command.

The next pushed commit expanded the assistant into selectable review modes:

- Explain selected code.
- Find bugs in selected code.
- Perform a security review.
- Suggest code improvements.

The modes were added to VS Code's command palette and editor context menu. The
extension was type-checked, linted, bundled, launched in an Extension
Development Host, and pushed to `main` after the selectable-mode changes were
reviewed.

**Confirmed development notes:** Dependency installation reported a deprecation
warning for an indirect `glob` version and a pending install-script notice for
`esbuild`; the audit reported zero active vulnerabilities. The compile pipeline
then completed successfully through TypeScript checking, ESLint, and esbuild.
The warning was treated as information rather than proof that the extension
itself had failed.

I used the extension's Improve mode on its own `extension.ts`. That self-review
identified several credible robustness issues:

- Some secret-storage failures could occur outside the existing error handler.
- VS Code selections are end-exclusive, so a selection ending at column zero of
  the next line could report an ending line one line too high.
- The selection-limit wording said “fewer than 12,000” even though exactly
  12,000 characters were allowed.
- Concurrent reviews shared and cleared one output channel, so overlapping
  requests could mix or erase results.
- An empty provider response could still lead to a success notification.
- Repeated output-header construction and in-function sensitive-file lists
  could be simplified.

These findings were evaluated as useful, but I do **not** treat the resulting
fixes as confirmed on `main`: the current repository history verifies the review
modes, not a later commit implementing every self-review recommendation. They
remain a clearly defined improvement batch until the diff and commit are
verified.

The extension README is also still the generated starter template. That is a
documentation gap, not a finished project description.

### Personalization branch — not yet part of main

**Confirmed in a separate local checkout:** A `feature/personalization` branch
contained a follow-up CyberLaunch OS commit titled “Add local notes and safety
preferences.” The diff added a combined training repository, local persistence
tests, a field-notes safety policy and tests, Field Notes and Settings screens,
new navigation destinations, and related dependency/configuration changes.

Because this branch was not present in the canonical checkout's branch list at
the time of this review, I record it as verified branch work, not as a released
main-branch feature. It should be reviewed, tested, and deliberately integrated
or preserved before any cleanup of alternate checkouts.

## Project-by-project account

### CyberLaunch Assistant

**What I created:** A VS Code extension written in TypeScript, backed by the
OpenAI SDK, with editor-selection commands, four task-specific review modes,
context-menu entries, secret storage, selection limits, sensitive-file checks,
provider error messages, and bundled output.

**What I repaired or improved:** I expanded one general inspection workflow into
clearer review modes and validated it against its own source. That self-test
gave me a concrete backlog of error-boundary, line-range, concurrency, wording,
and empty-response improvements.

**Current status:** The pushed extension compiles successfully, but it is still
Version 0.0.1. The generated README needs replacement, and the self-review fixes
must be checked against the current source before being described as complete.

**Next steps:**

1. Implement only the verified high-value self-review fixes.
2. Add automated tests for selection ranges, blocked files, empty responses,
   and concurrent command behavior.
3. Replace the starter README with installation, privacy, usage, known-issue,
   and release documentation.
4. Confirm the supported VS Code version and package the extension for a local
   installation test.
5. Keep API keys in secret storage and never log selected private code or
   credentials.

### Atlantic Hurricane Tracker

**What I created:** A standard-library Python briefing tool for NOAA/NHC and NWS
data, a state/history model, change detection, report/archive output, Apple
Shortcuts signaling, fictional offline sample mode, documentation, and tests.

**What I repaired or improved:** I replaced the simpler early tracker with a
more resilient Version 2; handled Pyto's read-only Inbox; avoided false “quiet”
reports when all core feeds fail; preserved Version 1.1 on a backup branch; and
resolved the README conflict caused while restoring stashed downloader work.

**Current status:** Version 2.0 is documented as complete. During preparation of
this devlog, all 6 current automated tests passed, including the sample
end-to-end output, Atlantic-storm filtering, outlook probability/zoning,
tropical-wave parsing, alert filtering, and live discussion format parsing.

**Next steps:** Periodically verify upstream feed formats, add saved fixture
coverage for unusual or malformed products, and keep the tool clearly labeled
as a briefing aid rather than an emergency-warning or landfall-prediction
service.

### Cybersecurity Labs

**What I created:** Eight defensive labs, safe sample evidence, lab and incident
templates, sanitization and authorization guidance, a Docker exercise, and
three local analysis tools.

**What I repaired or improved:** The design addressed the biggest portfolio
risks before publication: unsafe scope, leaking private lab data, and confusing
observation with exploitation.

**Current status:** Version 1.0 content is present and ongoing as a hands-on
portfolio. No dedicated automated test files were found by a conventional
`test*.py` discovery run; the included helper tools are documented for manual
use.

**Next steps:** Perform each lab in an owned, isolated environment; add sanitized
`REPORT.md` results; add unit tests for the three helper tools; and keep raw
logs, credentials, public targets, and personal data out of Git.

### iPad Notes Converter

**What I created:** A local watcher and one-shot converter for PDF, image, text,
and Markdown exports; subject routing; keyword and prefix rules; duplicate-safe
naming; logging; dry-run and configuration checks; unsupported-file quarantine;
Apple Shortcuts instructions; and tests.

**What I repaired or improved:** The workflow avoids unsupported direct access
to Apple's private Notes database. It includes safeguards against processing
outside the configured inbox, overwriting files, acting before iCloud finishes
writing, or testing first with irreplaceable notes.

**Current status:** Functional prototype/in development. During preparation of
this devlog, all 9 tests passed, covering routing, dry runs, PDF handling,
outside-inbox refusal, filename sanitization, duplicate numbering, and
unsupported-file quarantine.

**Next steps:** Test the complete Shortcut-to-iCloud-to-Mac workflow with copies,
document the actual macOS permissions encountered, consider OCR only as a
separate opt-in feature, and decide what is required for a Version 1.0 release.

### Writing Pattern Analyzer / former Submission Detector

**What I created:** A packaged Python stylometry tool with tokenization,
vocabulary, sentence, word-length, punctuation, profile comparison, reporting,
visualization, CLI, sample data, tests, and extensive learning notes.

**What I repaired or improved:** I replaced an unimplemented and misleading “AI
Submission Detector” concept with a measurable, explainable analyzer. I fixed
test expectations and discovery, normalized feature comparisons, and stopped
visualizing jointly absent features as perfect matches.

**Current status:** Version 0.1.0 is documented as complete. Running tests with
the system Python first exposed two environment issues: the package source path
was not on the import path and `matplotlib` was not installed there. Running the
project's own virtual-environment interpreter, which has its declared
dependencies, produced 45 passing tests. This was an environment/launch-context
problem, not a failing application test.

**Next steps:** Improve sentence segmentation, expand sample diversity, document
how sample length affects metrics, add more transparent explanation of feature
weighting, and continue resisting any claim that similarity proves AI use or
authorship.

### CyberLaunch OS

**What I created:** A Kotlin/Jetpack Compose Android application with a branded
theme, navigation, reusable components, Password Lab, Network Basics, Incident
Response practice, persistent checklist progress, reset controls, icons,
documentation, and unit tests.

**What I repaired or improved:** I removed redundant Kotlin plugin setup in
favor of Android's built-in support, aligned the project with a stable Android
36 toolchain, and moved checklist progress from memory into DataStore-backed
persistence.

**Current status:** Version 0.2.0 on `main`. During preparation of this devlog,
`./gradlew test` completed successfully. A personalization commit exists on a
separate local branch/checkout and is not counted as released on `main`.

**Next steps:** Reconcile and test the personalization branch; keep the training
console simulated and defensive; add UI/instrumentation tests; verify emulator
behavior; and move toward a launcher only as an explicit, opt-in phase. AOSP
work remains a long-term hardware-lab goal, not a current feature.

### Lecture Downloader

**What I created:** A legitimate course-material downloader with safe
configuration, HTTPS and allowed-host restrictions, file type and size checks,
duplicate handling, manifests, offline samples, automated tests, and
documentation.

**What I repaired or improved:** I replaced a much larger early script with a
smaller Version 1.0 module and preserved unfinished work safely through the Git
divergence/stash recovery.

**Current status:** The Version 1.0 commit is on `main`, although the root README
still calls the project “In Development.” That status mismatch should be
resolved deliberately rather than silently rewritten here.

**Next steps:** Re-run its offline test suite in its virtual environment, update
the root project status if Version 1.0 is the intended release, and add a live
source adapter only for a user-authorized export or direct-link workflow.

## Verification performed while creating this log

I did not rely only on commit messages. I inspected the canonical local
repository, all branches visible in the available checkouts, project files,
READMEs, existing project devlogs, and relevant development conversations.

I also ran the following checks without changing project source code:

- Hurricane Tracker: **6 tests passed**.
- iPad Notes Converter: **9 tests passed**.
- Writing Pattern Analyzer: **45 tests passed** in its project virtual
  environment.
- CyberLaunch Assistant: TypeScript type-check, ESLint, and esbuild compilation
  completed successfully.
- CyberLaunch OS: Gradle unit-test build completed successfully.
- Cybersecurity Labs: no conventional automated `test*.py` suite was present.

The first root-level attempt to run the Writing Pattern Analyzer could not
import its `src` package, and the system Python lacked `matplotlib`. The first
assistant compile attempt was also made from the repository root, which has no
root `package.json`. Both checks succeeded when rerun from the correct project
environment. I include this because choosing the correct working directory and
environment is part of reproducible testing.

## Broader lessons from CyberLaunch

1. **Preserve evidence before repairing Git.** A backup branch and stash turned
   a divergent-history problem into a recoverable workflow.
2. **Tests are evidence, not infallible truth.** Test expectations and test
   discovery can be wrong too.
3. **Run each project in its declared environment.** A missing import or package
   in the system interpreter does not automatically mean the project is broken.
4. **Use honest names and limitations.** Stylometry can measure patterns; it
   cannot prove AI generation or authorship.
5. **Design for failure.** Weather feeds fail, iOS folders can be read-only,
   iCloud files can still be syncing, and API calls can return errors or empty
   output.
6. **Security work starts with authorization and privacy.** Safe scope,
   isolation, sanitization, secret storage, and local-only processing are core
   features.
7. **Separate features from repairs.** Small commits for toolchain alignment,
   persistence, or review modes make the history understandable.
8. **Do not call branch work released work.** A feature can be real and tested
   without being merged into `main`.
9. **Documentation is part of the product.** A starter README or stale status
   can make working software look unfinished or misrepresent its behavior.
10. **Change, run, observe, test, commit.** This is the development loop I want
    to keep using as CyberLaunch grows.

## Repository-wide next steps

1. Review the existing uncommitted project changes independently; do not bundle
   them into this documentation change without understanding their origin.
2. Decide whether to merge, revise, or preserve the CyberLaunch OS
   personalization branch.
3. Replace CyberLaunch Assistant's generated README and implement the verified
   self-review fixes with tests.
4. Add test coverage for Cybersecurity Labs helpers.
5. Reconcile stale status wording in the root README, especially Lecture
   Downloader and the CyberLaunch OS version description.
6. Add a lightweight release/status table to the root README only after each
   project's status is agreed upon.
7. Keep generated reports, personal notes, exported school material, API keys,
   Android local configuration, build products, and private lab evidence out of
   source control.
8. Commit this devlog separately if it is approved, so the personal history can
   evolve without being mixed into application code.

## Closing reflection

CyberLaunch began as a place to collect projects, but it became a record of how
I learn: I build something useful, test it, discover where the assumptions fail,
repair the design, and document why the change mattered. The most important
progress is not the number of folders. It is the shift toward smaller verified
changes, safer defaults, clearer limits, recoverable Git workflows, and tools I
can explain rather than merely run.

This log should continue to be updated after meaningful releases, repairs, and
lessons. Future entries should preserve the same distinction between what Git
confirms, what development history confirms, and what is still only planned.
### CI Exposed Missing Model Package

After introducing GitHub Actions CI, CLIM's first remote test run failed even though all 100 tests passed locally.

Investigation showed that the CyberLaunch repository's parent `.gitignore` contained a broad `models/` rule. This unintentionally excluded CLIM's `app/models/` package from Git while leaving the files available on the local development machine.

As a result, the local environment masked a repository integrity problem that appeared immediately on a clean GitHub Actions runner.

The ignore configuration was corrected to explicitly preserve CLIM's model package, the missing source files were added to version control, and the complete quality gate was rerun.

Final result:

- Ruff: PASS
- pytest: 100 PASS
- GitHub Actions: PASS
- Repository checkout independently verified

This became the first defect discovered specifically because of CLIM's new continuous integration pipeline.