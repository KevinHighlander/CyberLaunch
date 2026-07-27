# Contributing to CyberLaunch OS

## Working agreement

1. Keep training features defensive, transparent, and limited to authorized
   environments.
2. Open the project and confirm the existing app runs before changing it.
3. Keep UI logic in `ui/` and testable non-Android rules in `domain/`.
4. Add or update tests when behavior changes.
5. Run `./gradlew test lint` before committing.
6. Keep each commit focused on one purpose.

## Definition of done

A change is complete when it builds, its navigation path works, important states
are readable and accessible, tests pass, and the README is updated when setup or
behavior changes.
