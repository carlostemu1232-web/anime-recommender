# AniVerse Mobile APK (Kivy)

This mobile app is a dedicated Android frontend that uses the local exported anime catalog.

## Included now

- Mobile entry point: `mobile_kivy/main.py`
- Local data source: `mobile_kivy/catalog.json` (1000 records)
- Buildozer config: `mobile_kivy/buildozer.spec`
- Windows build helper: `packaging/build_apk_kivy.ps1`

## Build with GitHub Actions (recommended)

This repository includes a CI workflow that builds the APK in the cloud:

- Workflow file: `.github/workflows/build-android-apk.yml`
- Job artifact name: `aniverse-mobile-apk`

How to use it:

1. Push this repository to GitHub.
2. Open the **Actions** tab.
3. Run **Build Android APK** (or push changes to `main` touching `mobile_kivy/`).
4. Download artifact `aniverse-mobile-apk` from the workflow run.

## Build on Windows with Docker (local alternative)

Prerequisite:

- Docker Desktop running

Command:

```powershell
powershell -ExecutionPolicy Bypass -File packaging/build_apk_kivy.ps1
```

Output APK location:

```text
mobile_kivy/bin/
```

## Refresh catalog data

If desktop catalog changes, regenerate mobile JSON:

```python
from database.database import get_all_animes_with_genres
```

and export again to `mobile_kivy/catalog.json`.
