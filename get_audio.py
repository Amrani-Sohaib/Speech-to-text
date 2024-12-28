import os
import json
import time
import re
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# For waiting on elements / conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# BeautifulSoup for parsing the HTML / JSON
from bs4 import BeautifulSoup


def download_audio(audio_url: str, output_path: str) -> None:
    """
    Downloads the audio from 'audio_url' and saves it to 'output_path'.
    Uses requests with a custom User-Agent to look like a normal browser.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/96.0.4664.93 Safari/537.36"
        )
    }
    resp = requests.get(audio_url, headers=headers, stream=True)
    if resp.status_code == 200:
        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"[OK] Audio saved: {output_path}")
    else:
        print(f"[ERROR] Failed to download audio from {audio_url}. Status code: {resp.status_code}")


def main():
    """
    1) Loads the JSON file of TikTok video data (Titre, URL).
    2) For each video URL:
       - Opens the link in Selenium.
       - Extracts the audio URL from the page's HTML/JSON.
       - Downloads the audio file into a local folder.
    """

    # ----------------------------------------------------------------
    # 1. Configuration
    # ----------------------------------------------------------------

    # Path to ChromeDriver (update if needed).
    CHROMEDRIVER_PATH = r"C:\Users\Sohaib\Desktop\chromedriver-win64\chromedriver.exe"
    # Name of the JSON file with "Titre" and "URL" fields.
    JSON_INPUT_FILE = "tiktok_videos.json"
    # Folder to store downloaded audio files.
    AUDIO_DOWNLOAD_FOLDER = "tiktok_audios"

    # Create the output folder if it doesn't exist:
    os.makedirs(AUDIO_DOWNLOAD_FOLDER, exist_ok=True)

    # ----------------------------------------------------------------
    # 2. Load the JSON data
    # ----------------------------------------------------------------
    with open(JSON_INPUT_FILE, "r", encoding="utf-8") as f:
        video_list = json.load(f)

    print(f"[INFO] Loaded {len(video_list)} video entries from {JSON_INPUT_FILE}.")

    # ----------------------------------------------------------------
    # 3. Set up Selenium
    # ----------------------------------------------------------------
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)

    try:
        # Optional: Maximize window to ensure the full page layout
        driver.maximize_window()

        # ----------------------------------------------------------------
        # 4. Process each video URL
        # ----------------------------------------------------------------
        for i, video_info in enumerate(video_list, start=1):
            titre = video_info.get("Titre", f"video_{i}")
            url = video_info.get("URL")

            print(f"\n[INFO] Processing {i}/{len(video_list)}: '{titre}' => {url}")

            if not url:
                print("[WARNING] No URL found, skipping.")
                continue

            # 4a) Open the TikTok video page
            driver.get(url)
            time.sleep(5)  # wait for page to load a bit

            # Optionally, wait for a specific element (like the <video> or <body>)
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except:
                print("[ERROR] Page load timeout or body not found.")
                continue

            # 4b) Parse the page HTML with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # ----------------------------------------------------------------
            # 5. Find the audio URL (the tricky part)
            # ----------------------------------------------------------------
            # TikTok often stores data in a <script> tag, e.g. "window.__NEXT_DATA__"
            # We look for the JSON that includes an "audio" or "music" node with "playUrl"
            # or "playUrlList". The exact key can vary, so we parse and search.

            audio_download_url = None

            # Find all <script> tags
            script_tags = soup.find_all("script")
            for script in script_tags:
                # We only care about those containing "playUrl" or "playUrlList"
                if script.string and ("playUrl" in script.string or "playUrlList" in script.string):
                    # This might be the JSON we need
                    data_str = script.string.strip()

                    # Extract the "playUrl" or "playUrlList" using a simple regex or JSON parse
                    # We'll do a naive search for "playUrl"
                    # Then refine if needed to get the actual link.
                    # Example snippet inside the JSON might look like:
                    # "playUrl":"https://p16.muscdn....
                    match = re.search(r'"playUrl":"(https:[^"]+)"', data_str)
                    if match:
                        # Found a direct URL
                        audio_download_url = match.group(1)
                        break

                    # If "playUrl" wasn't matched, check "playUrlList":[...]
                    match_list = re.search(r'"playUrlList":\["(https:[^"]+)"', data_str)
                    if match_list:
                        audio_download_url = match_list.group(1)
                        break

            if not audio_download_url:
                print("[WARNING] Could not find an audio URL in the page script data.")
                continue

            # 1) Decode unicode escapes:
            decoded_url = audio_download_url.encode('utf-8').decode('unicode_escape')

            # 2) Replace the literal "\u002F" with "/"
            decoded_url = decoded_url.replace("\\u002F", "/")

            # 3) Also fix the "https:\" -> "https://"
            #    (Because sometimes it appears like "https:\" or "https:\\")
            decoded_url = decoded_url.replace("https:\\", "https://")
            decoded_url = decoded_url.replace("http:\\",  "http://")

            print(f"[INFO] Found audio URL (decoded): {decoded_url}")

            # Now decoded_url should be something like:
            # https://v77.tiktokcdn-eu.com/b6a132c930a9836dc331f6873dfaab7d/...

            # ----------------------------------------------------------------
            # 6. Download the audio
            # ----------------------------------------------------------------
            safe_title = re.sub(r'[\\/*?:"<>|]', "_", titre)
            audio_file_name = f"{safe_title}.mp3"
            output_path = os.path.join(AUDIO_DOWNLOAD_FOLDER, audio_file_name)

            download_audio(decoded_url, output_path)
    finally:
        # ----------------------------------------------------------------
        # 7. Cleanup
        # ----------------------------------------------------------------
        print("\n[INFO] Finished. Closing browser.")
        driver.quit()


# ----------------------------------------------------------------
# Run the main function
# ----------------------------------------------------------------
if __name__ == "__main__":
    main()
