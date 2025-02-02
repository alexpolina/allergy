import os
from together import Together
from dotenv import load_dotenv

# ✅ Load API key securely
load_dotenv()
API_KEY = os.getenv("MULTIMODAL_API_KEY")

# ✅ Ensure API key exists
if not API_KEY:
    raise ValueError("❌ ERROR: MULTIMODAL_API_KEY is not set. Please check your .env file.")

# ✅ Initialize API client
client = Together(base_url="https://api.aimlapi.com/v1", api_key=API_KEY)

def get_ingredients_model_response(image_url):
    """Calls the multimodal API to analyze an image and return detected ingredients."""

    # ✅ Define the API request payload
    payload = {
        "model": "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Identify and list each unique ingredient in this image:"},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        "max_tokens": 1024,
    }

    # ✅ Debugging: Print the full request payload
    print("🔍 DEBUG: Sending API request with payload:", payload)

    try:
        response = client.chat.completions.create(**payload)
        print("🔍 DEBUG: Full API Response:", response)

        return response.choices[0].message.content
    except Exception as e:
        print(f"⚠️ ERROR: API request failed: {e}")
        return None

# ✅ Test function when running the script directly
if __name__ == "__main__":
    test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/LLama.jpg/444px-LLama.jpg?20050123205659"
    print("🛠️ Running test...")
    ingredients = get_ingredients_model_response(test_image_url)
    print("✅ Ingredients Detected:", ingredients)
