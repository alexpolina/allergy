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
# Debugging: Print Working Directory and Files
##################################################
st.write("Current working directory:", os.getcwd())
st.write("Files in directory:", os.listdir())

##################################################
# Helper: Safe Rerun Function
##################################################
def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()

##################################################
# Allergy Check & Ingredient Detection Debugging
##################################################
def check_allergies(ingredients_list):
    try:
        st.write("✅ Received ingredients list:", ingredients_list)  # Debug ingredient detection
        if not ingredients_list:
            st.error("⚠️ No ingredients detected. Check model/API response.")

        user_allergies = st.session_state.get("user_allergies", [])
        if user_allergies:
            user_message(f"And I'm also allergic to: {', '.join(user_allergies)}")
            bot_message("Let's see how they interact...")
            bracketed = get_crossing_data_model_response(ingredients_list, user_allergies)
            st.write("🔍 Allergy Check Response:", bracketed)  # Debug model output
    except Exception as e:
        logging.error("⚠️ Error in check_allergies(): %s", e)
        st.error(f"An error occurred: {e}")

##################################################
# Media Input Section Debugging
##################################################
def media_input():
    st.subheader("Select Input Method")
    if "input_method" in st.session_state:
        if st.button("🔄 Change Input Method"):
            del st.session_state["input_method"]
            safe_rerun()
    
    if "input_method" not in st.session_state:
        col1, col2 = st.columns(2)
        if col1.button("📷 Take a Picture"):
            st.session_state["input_method"] = "camera"
            safe_rerun()
        if col2.button("📁 Upload"):
            st.session_state["input_method"] = "upload"
            safe_rerun()
    
    if st.session_state.get("input_method") == "camera":
        st.subheader("Take a Picture")
        img_data = st.camera_input("Take a picture of your meal")
        if img_data is not None:
            st.write("📸 Image received from camera.")  # Debugging statement
            st.write("Image type:", type(img_data))
            st.write("Image size:", len(img_data.getvalue()))
            
            bot_message("Analyzing your meal...")
            with st.spinner("Detecting ingredients..."):
                ingredients_list = get_ingredients_model_response(img_data.getvalue())
            st.write("🧪 Model Ingredient Response:", ingredients_list)  # Debugging statement
            bot_message(format_ingredient_list(ingredients_list))
            check_allergies(ingredients_list)
    
    elif st.session_state.get("input_method") == "upload":
        st.subheader("Upload Meal Image")
        uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            st.write("📂 Image uploaded by user.")  # Debugging statement
            st.write("Image type:", type(uploaded_file))
            st.write("Image size:", len(uploaded_file.getvalue()))
            
            bot_message("Analyzing your meal...")
            with st.spinner("Detecting ingredients..."):
                ingredients_list = get_ingredients_model_response(uploaded_file.getvalue())
            st.write("🧪 Model Ingredient Response:", ingredients_list)  # Debugging statement
            bot_message(format_ingredient_list(ingredients_list))
            check_allergies(ingredients_list)

##################################################
# Main Application Debugging
##################################################
def main():
    st.set_page_config(page_title="Allergy Detector", page_icon="🔍")
    sidebar_setup()
    
    if st.session_state.get("allergies_selected"):
        bot_message(f"Hello {st.session_state.get('user_name', 'Guest')}! Let's see what's in your food.")
        media_input()
    else:
        st.info("Please set your allergies in the sidebar first.")

if __name__ == "__main__":
    main()
