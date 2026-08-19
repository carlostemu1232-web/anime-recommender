# AniVerse Android build

The desktop package is built with PyInstaller. PyInstaller cannot create APK files.

To build an APK, the machine needs the Qt for Python Android deployment tool plus:

- Android SDK
- Android NDK
- Java/JDK
- Gradle-compatible Android tools
- A PySide6 version with Android deployment support

The existing PySide6 UI and SQLite backend are the source for the mobile build, but the APK must be built with the official PySide6 Android deployment workflow rather than the Windows PyInstaller spec.

The repository includes `packaging/build_android.ps1`. It validates the local toolchain before invoking the Android deployer:

```powershell
powershell -ExecutionPolicy Bypass -File packaging/build_android.ps1
```

At the moment this script stops intentionally because this machine does not have `ANDROID_HOME` or `ANDROID_SDK_ROOT`, `ANDROID_NDK_ROOT`, `javac`, `adb` or `pyside6-android-deploy`. It is better to stop with that diagnosis than to produce a file that is not an installable APK.

After installing and configuring those tools, the official deployer must be initialized for `main.py`, then the script can be used as the repeatable preflight entry point. The exact deployer options depend on the installed PySide6 Android release.

The current portable Windows package is:

```text
dist/AniVerse-0.9.0-portable.zip
```

Before producing an APK, test the responsive UI in a narrow PySide6 window and configure Android storage paths for user data and the SQLite cache.
