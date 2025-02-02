import os
import sys
import time
import requests
import streamlit as st
from dotenv import load_dotenv
from streamlit_chat import message
from services.multi_modal import get_ingredients_model_response, get_crossing_data_model_response
from services.video_model import generate_videos
from utils.media_handler import image_to_base64
from utils.html import generate_alert

# ✅ Ensure the correct module path is set
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICES_DIR = os.path.join(BASE_DIR, "services")
sys.path.append(SERVICES_DIR)

# ✅ Ensure `services/` is recognized as a module
if not os.path.exists(os.path.join(SERVICES_DIR, "__init__.py")):
    open(os.path.join(SERVICES_DIR, "__init__.py"), 'a').close()

# ✅ Load environment variables
load_dotenv()

# ✅ Securely load API key
API_KEY = os.getenv("VIDEO_API_KEY")

if not API_KEY:
    st.error("❌ ERROR: VIDEO_API_KEY is not set. Please check your environment variables.")
    st.stop()

# ✅ Store user preferences in session state
if "user_name" not in st.session_state:
    st.session_state["user_name"] = ""
if "user_allergies" not in st.session_state:
    st.session_state["user_allergies"] = []

# ✅ Personalized onboarding
st.sidebar.title("👤 Personalized Profile")
st.session_state["user_name"] = st.sidebar.text_input("Enter your name", value=st.session_state["user_name"])
st.session_state["user_allergies"] = st.sidebar.multiselect(
    "Select your allergies",
    ["Peanuts", "Dairy", "Gluten", "Seafood", "Soy", "Eggs", "Sesame", "Corn"],
    default=st.session_state["user_allergies"]
)

st.sidebar.write("Your allergens:", ", ".join(st.session_state["user_allergies"]))

st.title("🍽️ Allergy Chat Assistant")

# ✅ Step 1: Chat Asks User About Their Meal
message(f"👋 Hello {st.session_state['user_name']}! What meal do you have today?", logo="https://i.ibb.co/py1Kdv4/image.png")

# ✅ Step 2: Upload Meal Image
uploaded_file = st.file_uploader("📸 Upload your meal image:", type=["jpg", "jpeg", "png"])
if uploaded_file:
    # Convert image to base64
    encoded_image = image_to_base64(uploaded_file.getvalue())

    # ✅ Display image in chat (Standardized size: 200px)
    message(f'<img width="200px" src="data:image/png;base64,{encoded_image}"/>', 
            is_user=True, allow_html=True, logo="https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Unknown_person.jpg/434px-Unknown_person.jpg", 
            key=f"user_image_{time.time()}")

    # ✅ Step 3: AI Detects Ingredients
    with st.spinner("🔍 Detecting ingredients..."):
        ingredients_text = get_ingredients_model_response(encoded_image)
    
    # ✅ Display Detected Ingredients
    message(f"🧪 **Detected Ingredients:** {ingredients_text}", logo="https://i.ibb.co/py1Kdv4/image.png")

    # ✅ Step 4: AI Checks Ingredients Against Allergies
    allergies = st.session_state.get("user_allergies", [])
    if allergies:
        with st.spinner("⚠️ Checking allergens..."):
            messages = get_crossing_data_model_response(ingredients_text, ", ".join(allergies))

        # ✅ Display allergy assessment in chat
        for advice in messages:
            obj = parse_ingredient_assessment(advice)
            if obj:
                alert_card = generate_alert(obj["emoji"], obj["ingredient_name"], obj["safety_status"], obj["description"])
                message(alert_card, logo="https://i.ibb.co/py1Kdv4/image.png", allow_html=True, key=f"alert_{time.time()}")

        # ✅ Offer to Generate Educational Video
        message("🎬 **Would you like a video about these allergens?**", logo="https://i.ibb.co/py1Kdv4/image.png")
        if st.button("Generate Educational Video"):
            video_url = generate_videos(", ".join(allergies))
            if video_url:
                message(f"🎬 **Your educational video is ready!**", logo="https://i.ibb.co/py1Kdv4/image.png")
                st.video(video_url)
            else:
                message("⚠️ **Error: No video URL returned from the API.**", logo="https://i.ibb.co/py1Kdv4/image.png")
