import time
import json
import os

# --- Selenium Imports ---
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

def main():
    """
    1) Initialize Chrome WebDriver
    2) Navigate to the TikTok user's profile
    3) Scroll the page to load all video thumbnails
    4) Collect each /video/... link and store:
        - Titre (video title or ID)
        - URL (the link to the TikTok video)
    5) Save the results in a JSON file (tiktok_videos.json)
    """
    
    # ----------------------------------------------------------------
    # 1. Configuration
    # ----------------------------------------------------------------
    # Update this with your actual path to ChromeDriver:
    CHROMEDRIVER_PATH = r"C:\Users\Sohaib\Desktop\chromedriver-win64\chromedriver.exe"
    
    # Replace with the target TikTok user’s profile URL:
    TIKTOK_PROFILE_URL = "https://www.tiktok.com/@omx1l"
    
    # The JSON file name where we'll store the results:
    JSON_OUTPUT_FILE = "tiktok_videos.json"

    # ----------------------------------------------------------------
    # 2. Set up Selenium (ChromeDriver)
    # ----------------------------------------------------------------
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)

    # Optionally, you can maximize the window to ensure more content is loaded
    driver.maximize_window()

    try:
        # ----------------------------------------------------------------
        # 3. Navigate to the user's profile
        # ----------------------------------------------------------------
        print("[INFO] Navigating to the profile page...")
        driver.get(TIKTOK_PROFILE_URL)
        # Wait a few seconds to let TikTok load the initial content
        time.sleep(5)

        # ----------------------------------------------------------------
        # 4. Scroll to load all videos
        # ----------------------------------------------------------------
        # TikTok loads additional videos dynamically as you scroll.
        # We'll do multiple scrolls until the page stops growing.
        last_height = driver.execute_script("return document.body.scrollHeight")
        SCROLL_REPETITIONS = 5  # Increase if the user has many videos

        for _ in range(SCROLL_REPETITIONS):
            # Scroll to the bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Give it time to load new videos
            time.sleep(3)

            # Check if new content was loaded
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                # No more new content
                break
            last_height = new_height

        # ----------------------------------------------------------------
        # 5. Collect all "/video/" links
        # ----------------------------------------------------------------
        print("[INFO] Collecting video links...")
        # We'll look for all <a> tags, then filter those with "/video/" in href
        all_links = driver.find_elements(By.TAG_NAME, "a")

        video_data = []
        for link in all_links:
            href = link.get_attribute("href")
            if href and "/video/" in href:
                # Try to get a text that represents the 'title' or Titre
                # TikTok often doesn't have a real title in feed anchors,
                # so we'll fallback to using the video ID (from the URL).
                titre = link.text.strip()
                if not titre:
                    # fallback: get the numeric ID from the URL
                    titre = href.split("/")[-1]

                # Store each video's data
                video_data.append({
                    "Titre": titre,
                    "URL": href
                })

        # Remove duplicates if the same URL appears multiple times
        seen_urls = set()
        unique_data = []
        for item in video_data:
            if item["URL"] not in seen_urls:
                seen_urls.add(item["URL"])
                unique_data.append(item)

        print(f"[INFO] Found {len(unique_data)} unique video links.")

        # ----------------------------------------------------------------
        # 6. Save the results to a JSON file
        # ----------------------------------------------------------------
        print(f"[INFO] Saving results to '{JSON_OUTPUT_FILE}'...")
        with open(JSON_OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(unique_data, f, ensure_ascii=False, indent=2)

        print("[INFO] Done! JSON file created successfully.")

    finally:
        # ----------------------------------------------------------------
        # 7. Close the WebDriver
        # ----------------------------------------------------------------
        driver.quit()


# ----------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------
if __name__ == "__main__":
    main()
