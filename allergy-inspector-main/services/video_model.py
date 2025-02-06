import os
import requests
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ Load API Key
VIDEO_API_KEY = os.getenv("VIDEO_API_KEY")
if not VIDEO_API_KEY:
    raise ValueError("❌ ERROR: VIDEO_API_KEY is not set. Please check your environment variables.")

# ✅ API Endpoint
API_URL = "https://api.aimlapi.com/v2/generate/video/kling/generation"

# ✅ Path to the Prompt File
PROMPT_FILE = "/workspaces/allergy/allergy-inspector-main/prompts/prepare_video_prompt.txt"

def load_prompt(filepath):
    """Loads a prompt file and ensures it exists."""
    if not os.path.exists(filepath):
        logging.error("⚠️ ERROR: Prompt file '%s' not found.", filepath)
        return ""
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read().strip()

def generate_dynamic_prompt(user_allergies):
    """
    Generates a visual storytelling prompt based on user allergens.
    """
    prompt_template = load_prompt(PROMPT_FILE)
    if not prompt_template:
        return "⚠️ Error: Video prompt file is missing or empty."
    
    allergy_story = (
        "A person eats a meal, unaware it contains {allergies}. "
        "Moments later, they begin feeling discomfort—itching, swelling, and difficulty breathing. "
        "Their hands scratch their skin, eyes become red, and their throat tightens. "
        "The animation smoothly shows microscopic allergens triggering the immune system. "
        "A visual transition highlights emergency steps—EpiPen, seeking medical help. "
        "The video ends with prevention tips and an encouraging message about food safety."
    )
    return prompt_template + "\n\n" + allergy_story.format(allergies=", ".join(user_allergies))

def generate_videos(
    user_allergies,
    ratio="16:9",
    duration=5, 
    wait_time=30,
    max_wait=1200
):
    """
    Generates a high-quality allergy awareness video using AI animation.
    :param user_allergies: List of user allergens.
    :param ratio: Video aspect ratio (e.g., "16:9").
    :param duration: Duration of the video in seconds.
    :param wait_time: Time (in seconds) between polling attempts.
    :param max_wait: Maximum total waiting time in seconds.
    :return: Video URL if available, else an error message.
    """
    prompt = generate_dynamic_prompt(user_allergies)
    if len(prompt) > 512:
        prompt = prompt[:512]
        logging.debug("🔍 DEBUG: Prompt truncated to 512 characters.")

    payload = {
        "model": "kling-video/v1.6/standard/text-to-video",
        "prompt": prompt,
        "ratio": ratio,
        "duration": str(duration)
    }

    headers = {
        "Authorization": f"Bearer {VIDEO_API_KEY}",
        "Content-Type": "application/json"
    }

    # Step 1: Send POST request
    response = requests.post(API_URL, json=payload, headers=headers)
    try:
        response_data = response.json()
    except requests.exceptions.JSONDecodeError:
        return "⚠️ Error: Failed to parse response JSON."

    logging.info("🔍 DEBUG: Video Generation Response: %s", response_data)
    generation_id = response_data.get("id")
    if not generation_id:
        logging.error("⚠️ Error: No video ID returned from API.")
        return "⚠️ Error: No video ID returned from API."

    logging.info("🎥 Video Generation Started. Generation ID: %s", generation_id)

    # Step 2: Poll for the video to be ready
    start_time = time.time()
    while (time.time() - start_time) < max_wait:
        logging.info("⏳ Waiting for video processing... (%d/%ds)", int(time.time() - start_time), max_wait)
        time.sleep(wait_time)
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
        data = response.json()
        logging.info("🔍 DEBUG: Fetch Video Response: %s", data)

        if data.get("status") == "error":
            error_detail = data.get("error", {}).get("detail", "Unknown error")
            logging.error("⚠️ Error in fetch_video: %s", error_detail)
            return f"⚠️ Error: {error_detail}"

        if data.get("status") == "completed":
            video_info = data.get("video", {})
            video_url = video_info.get("url")
            if video_url:
                logging.info("✅ Video Ready! URL: %s", video_url)
                return video_url

        status = data.get("status", "")
        if status in ("queued", "generating", "processing"):
            logging.info("⚠️ Video is still processing. Retrying soon...")
            return "⚠️ Error: Video is still processing."

        return f"⚠️ Error: Unexpected status: {status}"

    except requests.exceptions.RequestException as e:
        logging.error("❌ ERROR: Fetch request failed: %s", e)
        return f"⚠️ Error: {e}"

if __name__ == "__main__":
    # For testing purposes, call generate_videos with sample allergens.
    test_allergies = ["kale", "red cabbage", "cherry tomatoes", "bell peppers", "carrots", "mozzarella balls", "spinach"]
    video_result = generate_videos(test_allergies)
    print("Video Generation Result:", video_result)
