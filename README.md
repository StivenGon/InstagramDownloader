# Instagram Downloader

A Selenium-based Python script that opens an Instagram profile, collects post links, and downloads the images from each post into a local folder named after the target username.

## Requirements

- Python 3.10+
- Google Chrome installed
- Internet connection
- A valid Instagram username to visit

## Installation

1. Create and activate a virtual environment.
2. Install the dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Open [download_instagram.py](download_instagram.py).
2. Set `USERNAME` to the Instagram profile you want to download from.
3. Run the script:

```bash
python download_instagram.py
```

4. A small window will appear. Move the Chrome window into position, then click `Proceed`.
5. The script scrolls the profile, finds post links, and downloads images into a folder named after the username.

## Output

Downloaded images are saved in a folder with the same name as `USERNAME`.

## Notes

- The script uses `webdriver-manager` to download a matching ChromeDriver automatically.
- Instagram changes its page structure frequently, so selectors may need updates over time.
- Depending on the profile, some posts may require manual review because Instagram can limit access or load content dynamically.

## Dependencies

- selenium
- webdriver-manager
- requests
