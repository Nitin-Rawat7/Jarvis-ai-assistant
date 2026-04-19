import os
import subprocess
import requests
import urllib.parse
import psutil
import platform
import re
import threading
from datetime import datetime

# ── Known sites and apps ───────────────────────────────────────────
KNOWN_SITES = {
    "youtube"      : "https://www.youtube.com",
    "google"       : "https://www.google.com",
    "github"       : "https://www.github.com",
    "facebook"     : "https://www.facebook.com",
    "instagram"    : "https://www.instagram.com",
    "twitter"      : "https://www.twitter.com",
    "whatsapp"     : "https://web.whatsapp.com",
    "gmail"        : "https://www.gmail.com",
    "netflix"      : "https://www.netflix.com",
    "amazon"       : "https://www.amazon.in",
    "flipkart"     : "https://www.flipkart.com",
    "stackoverflow": "https://www.stackoverflow.com",
    "chatgpt"      : "https://chat.openai.com",
    "spotify"      : "https://open.spotify.com",
}

KNOWN_APPS = {
    "notepad"      : "notepad.exe",
    "calculator"   : "calc.exe",
    "brave"        : "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
    "chrome"       : "chrome.exe",
    "word"         : "winword.exe",
    "excel"        : "excel.exe",
    "paint"        : "mspaint.exe",
    "file explorer": "explorer.exe",
    "task manager" : "taskmgr.exe",
    "vs code"      : "code.exe",
    "vlc"          : "vlc.exe",
}

BRAVE_PATHS = [
    "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
    "C:\\Program Files (x86)\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
    f"C:\\Users\\{os.environ.get('USERNAME', 'user')}\\AppData\\Local\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
]

# ── Brave path cached once at startup ─────────────────────────────
def _find_brave_path() -> str | None:
    for path in BRAVE_PATHS:
        if os.path.exists(path):
            print(f"✅ Brave found: {path}")
            return path
    print("⚠️ Brave not found — will use default browser")
    return None

_BRAVE_PATH: str | None = _find_brave_path()


def _open_url(url: str) -> bool:
    url = url.strip()
    print(f"🌐 Opening: {url}")
    if _BRAVE_PATH:
        try:
            subprocess.Popen([_BRAVE_PATH, "--new-tab", url])
            return True
        except Exception as e1:
            print(f"❌ Brave new-tab failed: {e1}")
            try:
                subprocess.Popen([_BRAVE_PATH, url])
                return True
            except Exception as e2:
                print(f"❌ Brave failed: {e2}")
    try:
        os.system(f'start "" "{url}"')
        return True
    except Exception as e:
        print(f"❌ All open methods failed: {e}")
        return False


# ─────────────────────────────────────────────────────────────
# 🎨  IMAGE GENERATION — RapidAPI Flux
# ─────────────────────────────────────────────────────────────
# Save folder: project folder (same directory as jarvis files)
IMAGE_SAVE_DIR = os.path.dirname(os.path.abspath(__file__))

# RapidAPI key — replace with your actual key
RAPIDAPI_KEY   = "22d028664amsh389744c3dbc5cbep163827jsn3a3ccf535e02"

# Style ID — 4 is default Flux style (good for most prompts)
IMAGE_STYLE_ID = 4

# Default size: 16:9 landscape (as selected)
IMAGE_SIZE     = "16-9"

def generate_image(prompt: str) -> str:
    """
    Generate an AI image using Flux API via RapidAPI.

    Steps:
      1. Send prompt to Flux API
      2. Get back an image URL
      3. Download the image
      4. Save to project folder with timestamp filename
      5. Open the image automatically

    Usage in Jarvis:
      "generate image a sunset over the mountains"
      "generate image cyberpunk city at night"
      "generate image jarvis hologram interface"
    """
    prompt = prompt.strip()
    if not prompt:
        return "Please provide an image description. Example: generate image a lion in jungle"

    print(f"🎨 Generating image: '{prompt}'")

    # ── Step 1: Call Flux API ──────────────────────────────────
    try:
        url     = (
            "https://ai-text-to-image-generator-flux-free-api.p.rapidapi.com"
            "/aaaaaaaaaaaaaaaaaiimagegenerator/quick.php"
        )
        payload = {
            "prompt"  : prompt,
            "style_id": IMAGE_STYLE_ID,
            "size"    : IMAGE_SIZE,         # "16-9" landscape
        }
        headers = {
            "x-rapidapi-key" : RAPIDAPI_KEY,
            "x-rapidapi-host": "ai-text-to-image-generator-flux-free-api.p.rapidapi.com",
            "Content-Type"   : "application/json",
        }

        print("📡 Calling Flux API...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        data     = response.json()
        print(f"📦 API response: {data}")

    except requests.Timeout:
        return "Image generation timed out. Please try again."
    except Exception as e:
        return f"Image API error: {e}"

    # ── Step 2: Extract image URL from response ────────────────
    image_url = None

    # Check standard fields first
    image_url = (
        data.get("url")
        or data.get("image_url")
        or data.get("image")
    )

    # ✅ FIX: This API returns URLs inside final_result list
    # Response: {'final_result': [{'origin': 'https://...webp', 'thumb': '...'}, ...]}
    if not image_url:
        final_result = data.get("final_result", [])
        if isinstance(final_result, list) and len(final_result) > 0:
            image_url = (
                final_result[0].get("origin")   # full quality image
                or final_result[0].get("thumb") # thumbnail fallback
            )
    if not image_url:
        print(f"⚠️ Could not find image URL in response: {data}")
        return f"Could not get image URL from API. Response: {data}"

    print(f"🔗 Image URL: {image_url}")

    # ── Step 3: Download the image ────────────────────────────
    try:
        img_response = requests.get(image_url, timeout=30)
        img_response.raise_for_status()
    except Exception as e:
        return f"Failed to download image: {e}"

    # ── Step 4: Save to project folder ────────────────────────
    # Filename: jarvis_image_YYYYMMDD_HHMMSS.png
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Clean prompt for filename (first 30 chars, no special chars)
    clean_prompt = re.sub(r'[^a-zA-Z0-9 ]', '', prompt)[:30].strip().replace(' ', '_')
    filename  = f"jarvis_{clean_prompt}_{timestamp}.png"
    save_path = os.path.join(IMAGE_SAVE_DIR, filename)

    try:
        with open(save_path, "wb") as f:
            f.write(img_response.content)
        print(f"✅ Image saved: {save_path}")
    except Exception as e:
        return f"Failed to save image: {e}"

    # ── Step 5: Open the image automatically ──────────────────
    try:
        if platform.system() == "Windows":
            os.startfile(save_path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", save_path])
        else:
            subprocess.Popen(["xdg-open", save_path])
        print("🖼️ Image opened!")
    except Exception as e:
        print(f"⚠️ Could not auto-open image: {e}")

    return f"Image created and saved as '{filename}' in your project folder, sir."


# ─────────────────────────────────────────────────────────────
# YouTube
# ─────────────────────────────────────────────────────────────
def play_on_youtube(song_name: str) -> str:
    song_name = song_name.strip()
    try:
        query      = urllib.parse.quote(song_name)
        search_url = f"https://www.youtube.com/results?search_query={query}"
        headers    = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        print(f"🔍 Fetching YouTube for: {song_name}")
        response  = requests.get(search_url, headers=headers, timeout=5)
        video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', response.text)

        if video_ids:
            seen, unique_ids = set(), []
            for vid in video_ids:
                if vid not in seen:
                    seen.add(vid)
                    unique_ids.append(vid)
            video_url = f"https://www.youtube.com/watch?v={unique_ids[0]}"
            print(f"▶️  Playing: {video_url}")
            _open_url(video_url)
            return f"Playing: {song_name}"

        query = urllib.parse.quote(song_name)
        _open_url(f"https://www.youtube.com/results?search_query={query}")
        return f"Searching YouTube for: {song_name}"

    except requests.Timeout:
        query = urllib.parse.quote(song_name)
        _open_url(f"https://www.youtube.com/results?search_query={query}")
        return f"Searching YouTube for: {song_name}"
    except Exception as e:
        print(f"❌ play_on_youtube error: {e}")
        query = urllib.parse.quote(song_name)
        _open_url(f"https://www.youtube.com/results?search_query={query}")
        return f"Searching YouTube for: {song_name}"


def play_on_youtube_auto(song_name: str) -> str:
    song_name = song_name.strip()
    def _auto_play():
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            import time

            options = Options()
            if _BRAVE_PATH:
                options.binary_location = _BRAVE_PATH
            options.add_argument("--start-maximized")
            options.add_argument("--autoplay-policy=no-user-gesture-required")
            options.add_experimental_option(
                "prefs",
                {"profile.default_content_setting_values.notifications": 2}
            )
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            query = urllib.parse.quote(song_name)
            driver.get(f"https://www.youtube.com/results?search_query={query}")
            wait = WebDriverWait(driver, 10)
            wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "ytd-video-renderer #video-title")
                )
            ).click()
            time.sleep(2)
            for _ in range(10):
                time.sleep(1)
                for selector in [".ytp-skip-ad-button", ".ytp-ad-skip-button"]:
                    try:
                        btn = driver.find_element(By.CSS_SELECTOR, selector)
                        if btn.is_displayed():
                            btn.click()
                            break
                    except Exception:
                        pass
                try:
                    if not driver.find_element(
                        By.CSS_SELECTOR, ".ytp-ad-simple-ad-badge"
                    ).is_displayed():
                        break
                except Exception:
                    break
        except Exception as e:
            print(f"❌ Selenium error: {e}")
            play_on_youtube(song_name)

    threading.Thread(target=_auto_play, daemon=True).start()
    return f"Auto-playing: {song_name}"


# ─────────────────────────────────────────────────────────────
# Website / App
# ─────────────────────────────────────────────────────────────
def open_website(url: str) -> str:
    url = url.strip()
    if not url.startswith("http"):
        url = "https://www." + url
    _open_url(url)
    return f"Opened {url}"


def open_app(app_name: str) -> str:
    try:
        if platform.system() == "Windows":
            os.startfile(app_name)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", "-a", app_name])
        else:
            subprocess.Popen([app_name])
        return f"Opened {app_name}"
    except Exception as e:
        return f"Could not open {app_name}: {e}"


# ─────────────────────────────────────────────────────────────
# File operations
# ─────────────────────────────────────────────────────────────
def read_file(filepath: str) -> str:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"


def write_file(filepath: str, content: str) -> str:
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"File saved: {filepath}"
    except Exception as e:
        return f"Error writing file: {e}"


def list_files(directory: str = ".") -> str:
    try:
        return "\n".join(os.listdir(directory))
    except Exception as e:
        return f"Error: {e}"


# ─────────────────────────────────────────────────────────────
# Terminal / Search / System
# ─────────────────────────────────────────────────────────────
def run_command(command: str) -> str:
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"Command error: {e}"


def web_search(query: str) -> str:
    try:
        url  = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1"
        r    = requests.get(url, timeout=4)
        data = r.json()
        abstract = data.get("AbstractText", "")
        related  = [t.get("Text", "") for t in data.get("RelatedTopics", [])[:3]]
        result   = abstract if abstract else "No direct answer found."
        if related:
            result += "\n\nRelated:\n" + "\n".join(related)
        return result
    except requests.Timeout:
        return "Search timed out. Try a more specific query."
    except Exception as e:
        return f"Search error: {e}"


def get_system_info() -> str:
    cpu  = psutil.cpu_percent(interval=0.1)
    ram  = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return (
        f"CPU Usage: {cpu}%\n"
        f"RAM: {ram.used // (1024**2)}MB used / "
        f"{ram.total // (1024**2)}MB total\n"
        f"Disk: {disk.used // (1024**3)}GB used / "
        f"{disk.total // (1024**3)}GB total\n"
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


def take_screenshot(filename: str = "screenshot.png") -> str:
    try:
        import pyautogui
        pyautogui.screenshot().save(filename)
        return f"Screenshot saved as {filename}"
    except Exception as e:
        return f"Screenshot error: {e}"


# ─────────────────────────────────────────────────────────────
# 🎯  MAIN DISPATCHER
# ─────────────────────────────────────────────────────────────
def execute_tool(command: str) -> str:
    cmd = command.lower().strip()

    # ── Image generation (check FIRST — has spaces in prefix) ──
    if cmd.startswith("generate image:") or cmd.startswith("generate image "):
        prompt = command[15:].strip() if ":" in command[:16] else command[15:].strip()
        return generate_image(prompt)

    elif cmd.startswith("read:"):
        return read_file(command[5:].strip())

    elif cmd.startswith("play:"):
        return play_on_youtube(command[5:].strip())

    elif cmd.startswith("write:"):
        parts = command[6:].split("|", 1)
        if len(parts) == 2:
            return write_file(parts[0].strip(), parts[1].strip())
        return "Format: write: filepath | content"

    elif cmd.startswith("run:"):
        return run_command(command[4:].strip())

    elif cmd.startswith("search:"):
        return web_search(command[7:].strip())

    elif cmd.startswith("open:"):
        target = cmd[5:].strip()
        for name, url in KNOWN_SITES.items():
            if name in target:
                return open_website(url)
        for name, exe in KNOWN_APPS.items():
            if name in target:
                return open_app(exe)
        if "." in target:
            return open_website(target)
        return open_app(target)

    elif cmd in ["sysinfo", "system info", "system information"]:
        return get_system_info()

    elif cmd == "screenshot":
        return take_screenshot()

    return "Unknown command"
