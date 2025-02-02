import os
import sys
import requests
import streamlit as st
from dotenv import load_dotenv

# ✅ Ensure the correct module path is set
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICES_DIR = os.path.join(BASE_DIR, "services")
sys.path.append(SERVICES_DIR)

# ✅ Ensure `services/` is recognized as a module
if not os.path.exists(os.path.join(SERVICES_DIR, "__init__.py")):
    open(os.path.join(SERVICES_DIR, "__init__.py"), 'a').close()

# ✅ Now import the functions from services
from services.multi_modal import get_ingredients_model_response, get_crossing_data_model_response
from services.video_model import generate_videos

# ✅ Load environment variables
load_dotenv()

# ✅ Securely load API key
API_KEY = os.getenv("VIDEO_API_KEY")

if not API_KEY:
    st.error("❌ ERROR: VIDEO_API_KEY is not set. Please check your environment variables.")
    st.stop()

# ✅ Define the correct prompt file path
VIDEO_PROMPT_FILE = os.path.join(BASE_DIR, "prompts", "prepare_video_prompt.txt")

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

st.title("🍽️ Allergy Detector & Educational AI")

# ✅ Step 1: User uploads a meal image
uploaded_file = st.file_uploader("📸 Upload a meal image", type=["jpg", "jpeg", "png"])
allergy_risk = None  # Placeholder for risk detection

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Meal", use_column_width=True)

    # Convert image to base64 (for AI processing)
    image_url = uploaded_file.getvalue()

    with st.spinner("🔍 Detecting ingredients..."):
        ingredients = get_ingredients_model_response(image_url)

    if ingredients:
        st.success(f"✅ Detected Ingredients: {', '.join(ingredients)}")

        # ✅ Step 2: Check for allergens
        with st.spinner("⚠️ Checking for allergens..."):
            allergy_risk = get_crossing_data_model_response(ingredients, ", ".join(st.session_state["user_allergies"]))

        if allergy_risk:
            st.warning("⚠️ Allergy Risk Detected!")
            for risk in allergy_risk:
                status, emoji, name, description = risk
                color = "red" if status == "dangerous" else "yellow" if status == "alert" else "green"
                st.markdown(f"""
                <div style="background-color:{color};padding:10px;border-radius:10px;">
                <h4>{emoji} {name} - {status.upper()}</h4>
                <p>{description}</p>
                </div>""", unsafe_allow_html=True)
        else:
            st.success("✅ No major allergens detected!")

# ✅ Step 3: Generate Educational Video
if st.button("🎬 Generate Educational Video"):
    if uploaded_file and allergy_risk:
        st.warning("⚠️ This meal contains allergens! Video generation is disabled.")
    else:
        video_url = generate_videos(", ".join(st.session_state["user_allergies"]))

        if video_url:
            st.success("🎬 Your educational video is ready!")
            st.video(video_url)
        else:
            st.error("⚠️ Error: No video URL returned from the API.")
