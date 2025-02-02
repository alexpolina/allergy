import base64
import time
import streamlit as st
from streamlit_chat import message
from services.multi_modal import get_crossing_data_model_response, get_ingredients_model_response
from services.video_model import generate_videos
from utils.media_handler import image_to_base64
from utils.html import generate_alert

bot_image = "https://i.ibb.co/py1Kdv4/image.png"
unknow_user_image = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Unknown_person.jpg/434px-Unknown_person.jpg"

def media_input():
    """Handles user media input and processes allergen detection."""

    uploaded_file = st.file_uploader("📸 Upload your meal image:", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        # Convert image to base64
        encoded_image = image_to_base64(uploaded_file.getvalue())

        # Display image in chat (standardized size)
        with st.spinner("🔄 Processing Image..."):
            message(f'<img width="200px" src="data:image/png;base64,{encoded_image}"/>', 
                    is_user=True, allow_html=True, logo=unknow_user_image, key=f"user_image_{time.time()}")

        # AI Analysis: Detect ingredients
        with st.spinner("🔍 Detecting ingredients..."):
            ingredients_text = "".join(get_ingredients_model_response(encoded_image))
        
        # Show detected ingredients in chat
        display_detected_ingredients(ingredients_text)

        # Check allergens against user allergies
        check_allergies(ingredients_text)

def display_detected_ingredients(ingredients_text):
    """Displays detected ingredients in chat."""
    message(f"🧪 **Detected Ingredients:** {ingredients_text}", logo=bot_image)

def check_allergies(ingredients_text):
    """Compares detected ingredients with user allergies and categorizes them."""

    allergies = st.session_state.get("user_allergies", [])
    if allergies:
        with st.spinner("🔄 Checking allergens..."):
            messages = get_crossing_data_model_response(ingredients_text, ", ".join(allergies))

        first = False
        for advice in messages:
            if not first:
                message("⚠️ **Here’s what I found:**", logo=bot_image)
                first = True
            obj = parse_ingredient_assessment(advice)
            if obj:
                alert_card = generate_alert(obj["emoji"], obj["ingredient_name"], obj["safety_status"], obj["description"])
                message(alert_card, logo=bot_image, allow_html=True, key=f"alert_{time.time()}")

        # Offer to generate educational video
        message("🎬 **Would you like a video about these allergens?**", logo=bot_image)
        if st.button("Generate Educational Video"):
            generate_videos(", ".join(allergies))
