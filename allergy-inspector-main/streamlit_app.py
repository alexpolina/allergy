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
            message(f'<img width="200px" src="data:image/png;base64,{e
