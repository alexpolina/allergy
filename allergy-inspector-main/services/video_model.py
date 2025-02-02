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

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        return {"error": f"⚠️ API request failed: {e}"}

# ✅ Allow direct testing when running the script
if __name__ == "__main__":
    result = generate_video()
    print("Generation:", result)
