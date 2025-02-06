import os
import requests
import time
import streamlit as st

# Securely load API key from environment variable
API_KEY = os.getenv("VIDEO_API_KEY")

# Ensure API key exists
if not API_KEY:
    raise ValueError("❌ ERROR: VIDEO_API_KEY is not set. Please check your environment variables.")

# File path for the prompt
PROMPT_FILE_PATH = "/workspaces/allergy/allergy-inspector-main/prompts/prepare_video_prompt.txt"

def load_prompt(filepath):
    """Reads and returns the text from the prompt file."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read().strip()
    except FileNotFoundError:
        raise ValueError(f"❌ ERROR: Prompt file not found at {filepath}")
    except Exception as e:
        raise ValueError(f"⚠️ ERROR: Unable to read the prompt file: {e}")

def generate_video(duration="5", ratio="16:9"):
    """
    Generates a video using the API based on the text prompt from the file.
    
    :param duration: Length of the video (default: 5 seconds).
    :param ratio: Aspect ratio of the video (default: 16:9).
    :return: Video generation response
    """
    url = "https://api.aimlapi.com/v2/generate/video/kling/generation"

    # Load the prompt from the file
    prompt = load_prompt(PROMPT_FILE_PATH)

    payload = {
        "model": "kling-video/v1/standard/text-to-video",
        "prompt": prompt,
        "ratio": ratio,
        "duration": duration,
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    # Step 1: Send POST request
    response = requests.post(API_URL, json=payload, headers=headers)
    try:
        response_data = response.json()
    except requests.exceptions.JSONDecodeError:
        return "⚠️ Error: Failed to parse response JSON."

    print("🔍 DEBUG: Video Generation Response:", response_data)
    generation_id = response_data.get("id")
    if not generation_id:
        return "⚠️ Error: No video ID returned from API."

    print(f"🎥 Video Generation Started. Generation ID: {generation_id}")

    # Step 2: Wait (poll) for the video to be ready
    start_time = time.time()
    while (time.time() - start_time) < max_wait:
        print(f"⏳ Waiting for video processing... "
              f"({int(time.time() - start_time)}/{max_wait}s)")
        time.sleep(wait_time)

        # Step 3: Fetch status and video URL
        video_url = fetch_video(generation_id)
        if video_url and not video_url.startswith("⚠️"):
            return video_url

    return f"⚠️ Error: Video processing timed out. Generation ID: {generation_id}"

def fetch_video(generation_id):
    """
    Fetches the generated video URL from the AI API.
    """
    headers = {
        "Authorization": f"Bearer {VIDEO_API_KEY}",
        "Content-Type": "application/json"
    }
    params = {"generation_id": generation_id}

    try:
        response = requests.get(API_URL, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        return {"error": f"⚠️ API request failed: {e}"}

# ✅ Allow direct testing when running the script
if __name__ == "__main__":
    result = generate_video()
    print("Generation:", result)
