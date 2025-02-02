import os
import requests

# ✅ Fix Path Issues
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_DIR = os.path.join(BASE_DIR, "../prompts")
if not os.path.exists(PROMPT_DIR):
    PROMPT_DIR = os.path.join(BASE_DIR, "prompts")

PROMPT_FILE_PATH = os.path.join(PROMPT_DIR, "prepare_video_prompt.txt")

def load_prompt(filepath):
    """Reads and returns the text from the prompt file."""
    if not os.path.exists(filepath):
        raise ValueError(f"❌ ERROR: Prompt file not found at {filepath}")
    
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read().strip()
    except Exception as e:
        raise ValueError(f"⚠️ ERROR: Unable to read the prompt file: {e}")

def generate_videos(allergies):
    """Generates a video using the API based on the allergy input."""

    url = "https://api.aimlapi.com/v2/generate/video/kling/generation"
    prompt = load_prompt(PROMPT_FILE_PATH)

    payload = {
        "model": "kling-video/v1/standard/text-to-video",
        "prompt": f"{prompt}\n\nAllergies considered: {allergies}",
        "ratio": "16:9",
        "duration": "5",
    }

    headers = {
        "Authorization": f"Bearer {os.getenv('VIDEO_API_KEY')}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()

        # ✅ Debugging: Print full API response
        print("🔍 DEBUG: Full API Response:", response_data)

        # ✅ Extract video URL
        video_url = response_data.get("video_url")
        if not video_url:
            print("⚠️ No video URL returned. Full response:", response_data)
        
        return video_url

    except requests.exceptions.RequestException as e:
        print(f"⚠️ ERROR: API request failed: {e}")
        return None
