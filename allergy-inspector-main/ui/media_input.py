import base64
import time
from PIL import Image
import streamlit as st
from streamlit_chat import message
from utils.media_handler import image_to_base64
from utils.html import generate_alert
from services.multi_modal import get_crossing_data_model_response, get_ingredients_model_response
from services.video_model import generate_videos
unknow_user_image = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Unknown_person.jpg/434px-Unknown_person.jpg"
bot_image = "https://i.ibb.co/py1Kdv4/image.png"
doctor_image = "https://i.ibb.co/6HMSRys/2.png"


actual_response = ""

def parse_ingredient_assessment(assessment):
    try:
        elements = assessment.strip("[]").split(", ")
        
        return {
            "safety_status": elements[0],
            "emoji": elements[1],
            "ingredient_name": elements[2],
            "description": elements[3]
        }
    except:
        return None
 
def generate_labels(items, label_type="ingredient"):
    css_class = "ingredient-label" if label_type == "ingredient" else "allergy-label"
    labels_html = ", ".join(f'<span class="{css_class}">{item} </span>' for item in items)
    return labels_html
 
def media_input():
    apply_styling() 
    
    _,col1, col2, col3 = st.columns(4)

    gallery = col1.button("🖼️ Upload a picture", type= "primary" if  st.session_state["selected"] == "image" else "secondary")

    camera =  col2.button("🤳 Take the picture", type= "primary" if  st.session_state["selected"] == "camera" else "secondary")
    # video =  col3.button("📹 Add the video", type= "primary" if  st.session_state["selected"] == "video" else "secondary")
    if gallery or st.session_state["selected"] == "image":
        if(st.session_state["selected"] !=  "image"):
            st.session_state["selected"] = "image"
            st.rerun() 
        handle_image_upload()
    
    if camera or st.session_state["selected"] == "camera":
         if(st.session_state["selected"] !=  "camera"):
             st.session_state["selected"] = "camera"
             st.rerun()
         handle_camera_input()
    # if video or st.session_state["selected"] == "video":
    #     if(st.session_state["selected"] !=  "video"):
    #         st.session_state["selected"] = "video"
    #         st.rerun()
    #     handle_video_upload()

    handle_text_prompt()

# Function to apply custom styling to Streamlit UI
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
            .ingredient-container { line-height: 1.5; margin-bottom: 20px; padding: 15px; border: 1px solid #ddd;
                                    border-radius: 5px; background-color: #ffffff; text-align: left; }
            .explanation { font-style: italic; color: #555555; margin-top: 8px; line-height: 1.4; }
        </style>
    """, unsafe_allow_html=True)

def handle_image_upload():
    uploaded_file = st.file_uploader("Upload an image of the food.", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        users_image = image_to_base64(uploaded_file.getvalue())
        with st.spinner("..."):
            time.sleep(0.5)
            message(f'<img width="40%" style="float:right" src="data:image/png;base64,{users_image}"/>', is_user=True, allow_html=True, logo=unknow_user_image, key=f"user_image_{time.time()}")
        with st.spinner("..."):
            time.sleep(0.5)
            message("A picture, cool! Analyzing the evidence...", logo=bot_image, key=f"bot_image_{time.time()}")
        
        # try: 
        encoded_image = image_to_base64(uploaded_file.getvalue())
        with st.spinner('Wait for it...'):
            ingredients_text = "".join(get_ingredients_model_response(encoded_image))
        bot_display_ingredients(ingredients_text)
        check_allergies(ingredients_text)
            
        # except Exception:
        #     message("🔍 Something went wrong while analyzing the image.", is_user=True, allow_html=True)
    # for video in st.session_state['videos']:
        

def handle_video_upload():
    uploaded_file = st.file_uploader("Upload a video of the food", type=["mp4", "mov"])
    if uploaded_file:
        st.video(uploaded_file)
        get_model_response("Example OCR result text for video.")  # Placeholder for actual OCR implementation


def handle_camera_input():
    enable = st.checkbox("Enable camera")
    img_file_buffer = st.camera_input("Take a picture", disabled=not enable)
    if img_file_buffer:
        image_data = img_file_buffer.getvalue()
        users_image = image_to_base64(image_data)
        with st.spinner("..."):
            time.sleep(0.5)
            message(f'<img width="40%" style="float:right" src="data:image/png;base64,{users_image}"/>', is_user=True, allow_html=True, logo=unknow_user_image, key=f"user_camera_{time.time()}")
        with st.spinner("..."):
            time.sleep(0.5)
            message("Analyzing the captured picture...", logo=bot_image, key=f"bot_camera_{time.time()}")
        with st.spinner('Wait for it...'):
            ingredients_text = "".join(get_ingredients_model_response(users_image))
        bot_display_ingredients(ingredients_text)
        check_allergies(ingredients_text)

def handle_text_prompt():
    prompt = st.chat_input("food and or known ingredients")
    if prompt:
        ingredients_list = prompt.split(",")
        labels_html = generate_labels(ingredients_list)
        message(f'<div class="ingredient-container"><strong>🔎 Clues (Food or Ingredients):</strong><br>{labels_html}</div>', allow_html=True, is_user=True, logo=unknow_user_image)
        check_allergies(", ".join(ingredients_list))

# Helper function to display ingredients
def bot_display_ingredients(ingredients_text):
     with st.spinner("..."):
        time.sleep(0.5)
        message(f"<div class='ingredient-container'><strong>🔎 Clues (Ingredients):</strong><br>{ingredients_text}</div>", allow_html=True, logo=bot_image)

# Helper function to check allergies 
def check_allergies(ingredients_text):

    allergies = st.session_state.get("user_allergies", [])
    labels_html = generate_labels(allergies, label_type="allergy")
    message(f"<div class='ingredient-container'>and I'm also allergic to: <strong>{labels_html}</strong></div>", is_user=True, allow_html=True, logo=unknow_user_image)
    message("Cool, let's take that into account.", logo=bot_image)

    if allergies:
        messages = []
        with st.spinner("loading.."):
            messages = get_crossing_data_model_response(ingredients_text, ", ".join(allergies))
            alarm = False
        first = False
        for advice in messages:  
            if not first:
                first = True
                message("Here are some things to watch out for.", logo=bot_image)
            with st.spinner("loading.."):  
                time.sleep(1)
                obj = parse_ingredient_assessment(advice)
                if obj:
                    if alarm == False and obj["safety_status"] == "dangerous":
                        with open("./static/alert.mp3", "rb") as f:
                            data = f.read()
                            audio_base64 = base64.b64encode(data).decode('utf-8')
                            audio_tag = f'<audio autoplay="true" src="data:audio/wav;base64,{audio_base64}">'
                            # st.markdown(audio_tag, unsafe_allow_html=True)
                        alarm = True 
                    result = generate_alert(obj["emoji"], obj["ingredient_name"], obj["safety_status"], obj["description"].replace('"', ''))
                    message(result, logo=bot_image, allow_html=True, key=f'msg_{time.time()}')
 
              
        message("Learn more about your allergies, we are preparing videos and information about the symptoms of your allergies. this may take a while.", logo=doctor_image)
    
        allergies = ", ".join(allergies) 
        print(allergies)
        generate_videos(allergies)

                        