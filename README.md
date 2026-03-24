# Instagram Downloader

A small desktop app for downloading images from an Instagram profile. Enter a username, click start, and the app saves the images into a folder with the same name.

## Requirements

- Windows
- Google Chrome installed
- Internet connection
- An Instagram username you want to download from

## Run From Source

1. Install the dependencies:

```bash
pip install -r requirements.txt
```

2. Launch the app:

```bash
python download_instagram.py
```

## Build a Windows App

You can package this project into a single `.exe` so other people do not need Python or the dependencies installed.

1. Install PyInstaller:

```bash
pip install pyinstaller
```

2. Build the app:

```bash
pyinstaller InstagramDownloader.spec
```

3. The executable will be created in the `dist` folder.

If Selenium-related modules are still missing, rebuild with the provided spec instead of the one-line command so PyInstaller includes the hidden imports.

## How to Use

1. Open the app.
2. Type the Instagram username.
3. Click `Open browser`.
4. Log in to Instagram if needed and wait until the target profile page is fully loaded.
5. Click `Start scraping`.
6. The app scrolls the page, collects posts, and downloads the images into a folder named after the username.
7. Use `Open output folder` after a run finishes to jump straight to the downloaded files.

## App Features

- Custom desktop window styling
- Progress bar with post counters
- Output folder shortcut button
- Packaged `.exe` support with PyInstaller

## Notes

- The app uses Selenium Manager to find or download a matching ChromeDriver automatically.
- Instagram changes its page structure frequently, so selectors may need updates over time.
- Some profiles may require manual review because Instagram can limit access or load content dynamically.
- Known issue: some profiles may be scanned more than once during a run, which can cause duplicate downloads.
