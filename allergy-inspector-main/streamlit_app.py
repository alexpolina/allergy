import os
import requests
import time
import streamlit as st
from dotenv import load_dotenv

# Load API key securely
load_dotenv()
API_KEY = os.getenv("VIDEO_API_KEY")

if not API_KEY:
    raise ValueError("❌ ERROR: VIDEO_API_KEY is not set. Please check your environment variables.")

# File path for the video generation prompt
VIDEO_PROMPT_FILE = "/workspaces/allergy/allergy-inspector-main/prompts/prepare_video_prompt.txt"

def load_prompt(filepath):
    """Reads and returns the text from the prompt file."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read().strip()
    except FileNotFoundError:
        raise ValueError(f"❌ ERROR: Prompt file not found at {filepath}")
    except Exception as e:
        raise ValueError(f"⚠️ ERROR: Unable to read the prompt file: {e}")

def generate_videos(allergies):
    """
    Generates a video using the API based on the allergy input.

    :param allergies: List of allergies to use in video generation.
    :return: Streamlit video display or API response.
    """
    url = "https://api.aimlapi.com/v2/generate/video/kling/generation"

    # Load the prompt from the file
    prompt = load_prompt(VIDEO_PROMPT_FILE)

    payload = {
        "model": "kling-video/v1/standard/text-to-video",
        "prompt": f"{prompt}\n\nAllergies considered: {allergies}",
        "ratio": "16:9",
        "duration": "5",
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        with st.spinner(f"🎥 Generating video for allergies: {allergies}..."):
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            response_data = response.json()
            video_url = response_data.get("video_url")

            if video_url:
                st.video(video_url)
                return video_url
            else:
                st.error("⚠️ Error: No video URL returned from the API.")
                return response_data

    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ API request failed: {e}")
        return {"error": str(e)}

# ✅ Allow direct testing when running the script
if __name__ == "__main__":
    test_allergies = "peanuts, dairy"
    print("🎬 Video Generation Response:", generate_videos(test_allergies))
