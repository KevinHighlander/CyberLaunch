# CyberLaunch OS

CyberLaunch OS is a mobile-first cybersecurity learning environment built with
Kotlin and Jetpack Compose. Version `0.2.1` establishes the visual language,
navigation, safe training modules, and the first persistent training progress
that can later grow into a custom launcher and, eventually, an AOSP-based
system.

> **Training boundary:** The starter modules are offline and defensive. They do
> not scan networks, collect credentials, or interact with external targets.

## What is included

- Branded Command Center home screen
- Compose Navigation between training modules
- Password Lab with local, in-memory strength feedback
- Persistent incident-response practice checklist with a reset action
- Command Center incident-response progress
- Local Field Notes with explicit save and confirmed clear actions
- Persistent safety-reminder preference
- Defensive network-basics reference cards
- Unit tests for password assessment and saved-progress conversion rules
- Adaptive Android launcher icon and dark cyber-themed design system

## Project map

```text
app/src/main/java/com/cyberlaunch/os/
├── MainActivity.kt                 # Android entry point
├── data/
│   └── TrainingRepository.kt       # DataStore-backed progress and preferences
├── domain/
│   ├── FieldNotesPolicy.kt         # Note length and character safeguards
│   ├── IncidentResponseChecklist.kt # Checklist content and progress rules
│   └── PasswordStrength.kt         # Testable password-training rules
├── navigation/
│   └── Destination.kt              # App routes and module metadata
└── ui/
    ├── CyberLaunchApp.kt           # Navigation host and app shell
    ├── components/                 # Reusable UI pieces
    ├── screens/                    # Home and training modules
    └── theme/                      # Color, typography, and Material theme
```

## Mac setup

1. Install the latest stable **Android Studio** from
   [developer.android.com/studio](https://developer.android.com/studio).
2. During first-run setup, allow Android Studio to install the Android SDK.
3. In **SDK Manager**, install the Android 36 SDK platform and an API 36 emulator
   image. The project uses `minSdk 26`, so it can run on older test devices too.
4. Open this repository folder in Android Studio.
5. Let Gradle sync. The project requires JDK 17; Android Studio's bundled JDK is
   the simplest choice.
6. Create a virtual device in **Device Manager**, select it, and press **Run**.

Android Studio may offer newer compatible dependency versions later. Upgrade
them deliberately in a separate commit rather than accepting unrelated changes
while building a feature.

## Command-line checks

After Android Studio and the SDK are installed:

```bash
./gradlew test
./gradlew lint
./gradlew assembleDebug
```

The debug app will be generated under `app/build/outputs/apk/debug/`.

## How to stay hands-on

Start by changing one small thing and running the emulator after each edit:

1. Edit the Command Center subtitle in `HomeScreen.kt`.
2. Add a defensive concept to the `concepts` list in `NetworkBasicsScreen.kt`.
3. Add a response step to `IncidentResponseChecklist.steps`.
4. Add a Field Notes policy test before changing its storage limits.

This mirrors the development loop we will use throughout the project:
**change → run → observe → test → commit**.

## Roadmap

- **v0.1 — Foundation (complete):** branded app shell and offline learning modules
- **v0.2 — Persistence (complete):** saved checklist progress and reset controls
- **v0.2.1 — Personalization (complete):** local notes and saved safety preference
- **v0.3 — Training console:** simulated commands with guided explanations
- **v0.4 — Dashboard:** local device posture and permission education
- **v1.0 — Launcher:** opt-in Android home-screen experience
- **Later — AOSP:** dedicated test hardware and custom system image

## Git workflow

Feature branches should be small and descriptive:

```text
feature/training-console
feature/lab-notes
fix/password-feedback
```

Use short commits that describe one understandable change. Never commit
`local.properties`, signing keys, APKs, or Android Studio's generated files.
