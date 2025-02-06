import time
import base64
import streamlit as st
from streamlit_chat import message

from utils.media_handler import image_to_base64
from utils.html import generate_alert
from services.multi_modal import (
    get_ingredients_model_response,
    get_crossing_data_model_response
)

unknow_user_image = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Unknown_person.jpg/434px-Unknown_person.jpg"
bot_image = "https://i.ibb.co/py1Kdv4/image.png"
doctor_image = "https://i.ibb.co/6HMSRys/2.png"

def parse_ingredient_assessment(assessment):
    """
    e.g. parse '[safe, 🥛, milk, short description]' into a dict:
      {
        "safety_status": "safe",
        "emoji": "🥛",
        "ingredient_name": "milk",
        "description": "short description"
      }
    """
    try:
        # Remove brackets if present
        trimmed = assessment.strip("[] ")
        elements = trimmed.split(", ")
        # Elements => [safety_status, emoji, ingredient_name, description]
        return {
            "safety_status": elements[0],
            "emoji": elements[1],
            "ingredient_name": elements[2],
            "description": elements[3]
        }
    except:
        return None

def media_input():
    apply_styling() 
    
    _, col1, col2, col3 = st.columns(4)

    gallery = col1.button(
        "🖼️ Upload a picture",
        type= "primary" if st.session_state["selected"] == "image" else "secondary"
    )

    camera = col2.button(
        "🤳 Take the picture",
        type= "primary" if st.session_state["selected"] == "camera" else "secondary"
    )

    if gallery or st.session_state["selected"] == "image":
        if st.session_state["selected"] != "image":
            st.session_state["selected"] = "image"
            st.rerun()
        handle_image_upload()
    
    if camera or st.session_state["selected"] == "camera":
        if st.session_state["selected"] != "camera":
            st.session_state["selected"] = "camera"
            st.rerun()
        handle_camera_input()

    handle_text_prompt()

def apply_styling():
    st.markdown("""
        <style>
            .reportview-container { background-color: #f9f9f9; color: #333333; font-family: Arial, sans-serif; }
            .stTextInput>div>div>input { color: #333333; background-color: #ffffff; }
            .ingredient-label, .allergy-label {
                background-color: #d9d9d9; color: #333333; padding: 5px 8px; border-radius: 3px;
                display: inline-block; margin: 0 4px 4px 0; font-weight: bold;
            }
            .allergy-label { background-color: #ff9999; color: white; }
            .ingredient-container {
                line-height: 1.5; margin-bottom: 20px; padding: 15px; border: 1px solid #ddd;
                border-radius: 5px; background-color: #ffffff; text-align: left;
            }
            .explanation { font-style: italic; color: #555555; margin-top: 8px; line-height: 1.4; }
        </style>
    """, unsafe_allow_html=True)

def handle_image_upload():
    uploaded_file = st.file_uploader("Upload an image of the food.", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        # Convert to base64
        users_image = image_to_base64(uploaded_file.getvalue())
        # Show a smaller pic in chat (width=25%)
        time.sleep(0.5)
        message(
            f'<img width="25%" style="float:right" src="data:image/png;base64,{users_image}"/>',
            is_user=True,
            allow_html=True,
            logo=unknow_user_image,
            key=f"user_image_{time.time()}"
        )
        time.sleep(0.5)
        message("A picture, cool! Analyzing the evidence...", logo=bot_image)

        # Now call the AI to get ingredients
        with st.spinner('Analyzing image...'):
            # This returns a streaming generator
            ingredients_generator = get_ingredients_model_response(users_image)
            # Combine the streamed text
            ingredients_text = "".join(ingredients_generator)

        bot_display_ingredients(ingredients_text)
        check_allergies(ingredients_text)

def handle_camera_input():
    enable = st.checkbox("Enable camera")
    img_file_buffer = st.camera_input("Take a picture", disabled=not enable)
    if img_file_buffer:
        image_data = img_file_buffer.getvalue()
        users_image = image_to_base64(image_data)
        
        time.sleep(0.5)
        message(
            f'<img width="25%" style="float:right" src="data:image/png;base64,{users_image}"/>',
            is_user=True,
            allow_html=True,
            logo=unknow_user_image,
            key=f"user_camera_{time.time()}"
        )
        time.sleep(0.5)
        message("Analyzing the captured picture...", logo=bot_image)

        with st.spinner('Wait for it...'):
            ingredients_generator = get_ingredients_model_response(users_image)
            ingredients_text = "".join(ingredients_generator)

        bot_display_ingredients(ingredients_text)
        check_allergies(ingredients_text)

def handle_text_prompt():
    prompt = st.chat_input("food and or known ingredients")
    if prompt:
        # You might parse the user text to figure out ingredients
        # For now, we just echo them
        items = prompt.split(",")
        labels_html = generate_labels(items)
        message(
            f'<div class="ingredient-container"><strong>🔎 Clues (Food or Ingredients):</strong><br>{labels_html}</div>',
            allow_html=True,
            is_user=True,
            logo=unknow_user_image
        )
        check_allergies(", ".join(items))

def generate_labels(items, label_type="ingredient"):
    css_class = "ingredient-label" if label_type == "ingredient" else "allergy-label"
    labels_html = ", ".join(f'<span class="{css_class}">{item}</span>' for item in items)
    return labels_html

def bot_display_ingredients(ingredients_text):
    """
    Displays the recognized ingredients in a container for the user.
    """
    time.sleep(0.5)
    message(
        f"<div class='ingredient-container'><strong>🔎 Clues (Ingredients):</strong><br>{ingredients_text}</div>",
        allow_html=True,
        logo=bot_image
    )

def check_allergies(ingredients_text):
    """
    Calls get_crossing_data_model_response, which yields bracketed items like:
       [dangerous, 🍤, shrimp, "Allergy to shellfish..."]
    Then we parse them and display color-coded results with generate_alert().
    """
    # Access the allergies from session_state
    allergies = st.session_state.get("user_allergies", [])
    labels_html = generate_labels(allergies, label_type="allergy")
    message(
        f"<div class='ingredient-container'>and I'm also allergic to: <strong>{labels_html}</strong></div>",
        is_user=True,
        allow_html=True,
        logo=unknow_user_image
    )
    message("Cool, let's take that into account.", logo=bot_image)

    if allergies:
        with st.spinner("loading.."):
            # crossing_data_model_response streams bracketed items
            messages = list(get_crossing_data_model_response(ingredients_text, ", ".join(allergies)))
            alarm = False

        first = False
        for advice in messages:
            # advice is something like: "[safe, 🍅, tomato, short desc]"
            if not first:
                first = True
                message("Here are some things to watch out for.", logo=bot_image)

            obj = parse_ingredient_assessment(advice)
            if obj:
                # If the safety status is "dangerous", we can optionally play a sound
                if not alarm and obj["safety_status"].lower() == "dangerous":
                    # You can insert logic to play an alert sound
                    alarm = True

                # Use generate_alert(...) for color-coded block
                from utils.html import generate_alert
                alert_html = generate_alert(
                    obj["emoji"],
                    obj["ingredient_name"],
                    obj["safety_status"],
                    obj["description"].replace('"', '')
                )
                message(alert_html, logo=bot_image, allow_html=True, key=f'msg_{time.time()}')

        message(
            "Learn more about your allergies. We are preparing videos and info about the symptoms. This may take a while.",
            logo=doctor_image
        )
        
        # Possibly call your video generation or other logic here
        # from services.video_model import generate_videos
        # generate_videos(", ".join(allergies))
