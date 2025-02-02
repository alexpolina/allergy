import os
import requests
import time
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Securely load API key
API_KEY = os.getenv("VIDEO_API_KEY")

if not API_KEY:
    raise ValueError("❌ ERROR: VIDEO_API_KEY is not set. Please check your environment variables.")

# ✅ Hardcoded path to the correct prompt file
VIDEO_PROMPT_FILE = "/workspaces/allergy/allergy-inspector-main/prompts/prepare_video_prompt.txt"

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
    """
    Generates a video using the API based on the allergy input.

    :param allergies: List of allergies to use in video generation.
    :return: Streamlit video display or API response.
    """
    url = "https://api.aimlapi.com/v2/generate/video/kling/generation"

    # Load the prompt from the file
    prompt = load_prompt(VIDEO_PROMPT_FILE)

    payload 
