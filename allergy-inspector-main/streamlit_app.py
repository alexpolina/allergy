import os
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Securely load API key
API_KEY = os.getenv("VIDEO_API_KEY")

if not API_KEY:
    st.error("❌ ERROR: VIDEO_API_KEY is not set. Please check your environment variables.")
    st.stop()

# ✅ Define the correct prompt file path
VIDEO_PROMPT_FILE = "/workspaces/allergy/allergy-inspector-main/prompts/prepare_video_prompt.txt"

def load_prompt(filepath):
    """Reads and returns the text from the prompt file."""
    if not os.path.exists(filepath):
        st.error(f"❌ ERROR: Prompt file not found at {filepath}")
        st.stop()
    
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read().strip()
    except Exception as e:
        st.error(f"⚠️ ERROR: Unable to read the prompt file: {e}")
        st.stop()

def generate_videos(allergies):
    """
    Generates a video using the API based on the allergy input.
    
    :param allergies: List of allergies selected by the user.
    :return: Video URL or error message.
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
                return video_url
            else:
                return None  # No video returned
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# ✅ Streamlit UI
st.title("🎥 Allergy Video Generator")

# User selects allergies
selected_allergies = st.multiselect(
    "Select allergies to generate video:",
    ["Peanuts", "Dairy", "Gluten", "Seafood", "Soy", "Eggs", "Sesame", "Corn"],
    default=[]
)

# ✅ Wait for user to click "Generate Video"
if st.button("Generate Video"):
    if not selected_allergies:
        st.warning("⚠️ Please select at least one allergy before generating the video.")
    else:
        video_url = generate_videos(", ".join(selected_allergies))

        if video_url:
            st.success("🎬 Your video is ready!")
            st.video(video_url)
        else:
            st.error("⚠️ Error: No video URL returned from the API.")
