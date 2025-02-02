import os
from together import Together
from dotenv import load_dotenv

# ✅ Load API key
load_dotenv()
API_KEY = os.getenv("MULTIMODAL_API_KEY")
if not API_KEY:
    raise ValueError("❌ ERROR: MULTIMODAL_API_KEY is missing!")

# ✅ Initialize API client
client = Together(base_url="https://api.aimlapi.com/v1", api_key=API_KEY)

def get_ingredients_model_response(image_data):
    """Calls the AI model to identify ingredients in the uploaded meal image."""

    payload = {
        "model": "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
        "messages": [
            {"role": "user", "content": [
                {"type": "text", "text": "Identify and list ingredients in this image."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}},
            ]}
        ],
        "max_tokens": 1024
    }

    try:
        response = client.chat.completions.create(**payload)
        return response.choices[0].message.content
    except Exception as e:
        print(f"⚠️ ERROR: API request failed: {e}")
        return None
