import os
import streamlit as st
import time
import logging
import threading
from streamlit_chat import message

from services.multi_modal import (
    get_ingredients_model_response,
    get_crossing_data_model_response
)
from services.video_model import generate_videos
from utils.media_handler import image_to_base64
from ui.sidebar import sidebar_setup

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

##################################################
# Helper: Safe Rerun Function (notification removed)
##################################################
def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()

##################################################
# Helpers: Chat Messages
##################################################
def bot_message(text: str):
    """Displays a bot-styled message using streamlit_chat.message with a bot logo."""
    message(text, logo="https://i.ibb.co/py1Kdv4/image.png")

def user_message(text: str):
    """Displays a user-styled message using streamlit_chat.message with a user logo."""
    message(text, is_user=True, logo="https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Unknown_person.jpg/434px-Unknown_person.jpg")

##################################################
# Helpers: Ingredient Display
##################################################
def format_ingredient_list(ingredients):
    # Clean each ingredient and filter out empty strings.
    cleaned = [ing.strip() for ing in ingredients if ing.strip()]
    if not cleaned:
        return "No ingredients detected."
    # Header on one line and each ingredient on its own line.
    return "🔍 Detected Ingredients:\n" + "\n".join(cleaned)

def display_ingredient_cards(ingredient_data_list):
    for item in ingredient_data_list:
        status = item["status"].lower()
        color = "#ff6961" if status == "dangerous" else "#FFD700" if status == "alert" else "#77DD77"
        card_html = f"""
        <div style="border: 2px solid {color}; 
                    border-radius: 10px; 
                    width: 250px; 
                    padding: 10px; 
                    margin-bottom: 10px; 
                    background-color: {color}20;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.5em;">{item["emoji"]}</span>
                <h4 style="margin: 0; color: {color}; text-transform: capitalize;">
                    {item["ingredient"]}
                </h4>
            </div>
            <span style="color: {color}; font-weight: bold; text-transform: uppercase;">
                {item["status"]}
            </span>
            <p style="margin-top: 5px; font-size: 0.9em;">
                {item["description"]}
            </p>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

def parse_ingredient_assessment(bracket_str):
    try:
        parts = bracket_str.strip("[]").split(", ")
        return {
            "status": parts[0],
            "emoji": parts[1],
            "ingredient": parts[2],
            "description": parts[3].strip('"')
        }
    except Exception as e:
        logging.error("⚠️ ERROR parsing ingredient assessment: %s", e)
        return None

##################################################
# Background Video Generation Thread
##################################################
class VideoGenerationThread(threading.Thread):
    """
    Runs generate_videos(...) in a separate thread so the UI doesn't freeze.
    """
    def __init__(self, user_allergies, user_concern=""):
        super().__init__()
        self.user_allergies = user_allergies
        self.user_concern = user_concern
        self.video_url = None
        self.keep_checking = True

    def run(self):
        try:
            logging.info("🎥 Starting background video generation ...")
            self.video_url = generate_videos(self.user_allergies)
            retries = 0
            while (not self.video_url or self.video_url.startswith("⚠️")) and self.keep_checking:
                logging.warning("🚨 Video not ready yet. Retrying... (Attempt %d)", retries + 1)
                time.sleep(30)
                self.video_url = generate_videos(self.user_allergies)
                retries += 1
                if retries > 20:
                    logging.error("❌ Maximum retries reached. Video generation failed.")
                    self.video_url = "⚠️ Video generation failed after multiple attempts."
                    break
            logging.info("🎞️ Video generation finished: %s", self.video_url)
        except Exception as e:
            logging.error("⚠️ Error in generate_videos thread: %s", e)
            self.video_url = f"⚠️ Error: {e}"

##################################################
# Allergy Check & Video Generation
##################################################
def check_allergies(ingredients_list):
    try:
        user_allergies = st.session_state.get("user_allergies", [])
        if user_allergies:
            user_message(f"And I'm also allergic to: {', '.join(user_allergies)}")
            bot_message("Let's see how they interact...")
            bracketed = get_crossing_data_model_response(ingredients_list, user_allergies)
            card_data = [parse_ingredient_assessment(bstr) for bstr in bracketed if parse_ingredient_assessment(bstr)]
            if card_data:
                bot_message("Here are the findings for each ingredient:")
                display_ingredient_cards(card_data)
            else:
                bot_message("No recognized risks found.")
            user_concern = st.text_area("Describe your allergy concerns (optional):", placeholder="e.g., I get severe reactions to peanuts.")
            if st.button("🎥 Make a Video About My Allergies"):
                process_video_generation(user_allergies, user_concern)
        else:
            bot_message(format_ingredient_list(ingredients_list))
    except Exception as e:
        logging.error("⚠️ Error in check_allergies(): %s", e)
        st.error("An error occurred while checking allergies.")

def process_video_generation(user_allergies, user_concern):
    if not user_concern:
        user_concern = "General allergy information."
    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.text("Processing your video...")
    thread = VideoGenerationThread(user_allergies, user_concern)
    thread.start()
    i = 0
    while thread.is_alive():
        i = (i + 1) % 100
        progress_bar.progress(i + 1)
        time.sleep(1.5)
    progress_bar.progress(100)
    video_url = thread.video_url
    if video_url and not video_url.startswith("⚠️"):
        status_text.text("✅ Video is ready!")
        st.video(video_url)
    else:
        status_text.text("")
        st.warning(video_url or "Video generation failed.")

##################################################
# Media Input Section with Two Buttons & Chat Integration
##################################################
def media_input():
    st.subheader("Select Input Method")
    # Option to change input method if already selected
    if "input_method" in st.session_state:
        if st.button("🔄 Change Input Method"):
            del st.session_state["input_method"]
            safe_rerun()
    # If no input method is selected, show the two buttons
    if "input_method" not in st.session_state:
        col1, col2 = st.columns(2)
        if col1.button("📷 Take a Picture"):
            st.session_state["input_method"] = "camera"
            safe_rerun()
        if col2.button("📁 Upload"):
            st.session_state["input_method"] = "upload"
            safe_rerun()
    # Display the corresponding input widget
    if st.session_state.get("input_method") == "camera":
        st.subheader("Take a Picture")
        img_data = st.camera_input("Take a picture of your meal")
        if img_data is not None:
            b64_img = image_to_base64(img_data.getvalue())
            # Display the image aligned to the right as a thumbnail
            st.markdown(
                f'<div style="text-align: right;"><img src="data:image/png;base64,{b64_img}" width="100" style="border-radius:10px;" /></div>',
                unsafe_allow_html=True
            )
            bot_message("Analyzing your meal...")
            with st.spinner("Detecting ingredients..."):
                ingredients_list = get_ingredients_model_response(img_data.getvalue())
            bot_message(format_ingredient_list(ingredients_list))
            check_allergies(ingredients_list)
    elif st.session_state.get("input_method") == "upload":
        st.subheader("Upload Meal Image")
        uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            b64_img = image_to_base64(uploaded_file.getvalue())
            # Display the image aligned to the right as a thumbnail
            st.markdown(
                f'<div style="text-align: right;"><img src="data:image/png;base64,{b64_img}" width="100" style="border-radius:10px;" /></div>',
                unsafe_allow_html=True
            )
            bot_message("Analyzing your meal...")
            with st.spinner("Detecting ingredients..."):
                ingredients_list = get_ingredients_model_response(uploaded_file.getvalue())
            bot_message(format_ingredient_list(ingredients_list))
            check_allergies(ingredients_list)

##################################################
# Main Application
##################################################
def main():
    st.set_page_config(page_title="Allergy Detector", page_icon="🔍")
    
    # Hide GitHub link and other Streamlit chrome elements
    hide_github_icon = """
    <style>
    .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob, 
    .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137, .viewerBadge_text__1JaDK {
        display: none; 
    }
    #MainMenu { visibility: hidden; } 
    footer { visibility: hidden; } 
    header { visibility: hidden; }
    </style>
    """
    st.markdown(hide_github_icon, unsafe_allow_html=True)
    
    sidebar_setup()
    if st.session_state.get("allergies_selected"):
        bot_message(f"Hello {st.session_state.get('user_name', 'Guest')}! Let's see what's in your food.")
        media_input()
    else:
        st.info("Please set your allergies in the sidebar first.")

if __name__ == "__main__":
    main()
