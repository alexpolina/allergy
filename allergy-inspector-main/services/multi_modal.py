import os
import base64
import json
from openai import OpenAI

# Load API Key
MULTIMODAL_API_KEY = os.getenv("MULTIMODAL_API_KEY")
if not MULTIMODAL_API_KEY:
    raise ValueError("❌ ERROR: MULTIMODAL_API_KEY is not set. Please check your environment variables.")

client = OpenAI(
    base_url="https://api.aimlapi.com/v1",
    api_key=MULTIMODAL_API_KEY
)

# Use the current working directory to locate the prompts folder.
# When running Streamlit, os.getcwd() is usually the project root.
PROMPT_DIR = os.path.join(os.getcwd(), "prompts")
CROSSING_PROMPT_FILE = os.path.join(PROMPT_DIR, "crossing_prompt.txt")
INGREDIENTS_PROMPT_FILE = os.path.join(PROMPT_DIR, "ingredients_prompt.txt")
INFERS_ALLERGY_PROMPT_FILE = os.path.join(PROMPT_DIR, "infers_allergy_prompt.txt")

def load_prompt(filepath):
    if not os.path.exists(filepath):
        print(f"⚠️ ERROR: Prompt file '{filepath}' not found.")
        return ""
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read().strip()

def _encode_image_to_base64(image_binary: bytes) -> str:
    try:
        return base64.b64encode(image_binary).decode("utf-8")
    except Exception as e:
        print(f"❌ ERROR: Failed to encode image: {e}")
        return ""

def get_ingredients_model_response(image_binary: bytes):
    """
    Detects ingredients in an uploaded image.
    - Removes duplicates
    """
    image_base64 = _encode_image_to_base64(image_binary)
    if not image_base64:
        print("❌ ERROR: Could not encode image.")
        return []

    try:
        prompt_text = load_prompt(INGREDIENTS_PROMPT_FILE)
        if not prompt_text:
            return []

        response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                    },
                    {
                        "type": "text",
                        "text": prompt_text
                    }
                ]
            }],
        )

        if response and response.choices:
            raw_text = response.choices[0].message.content.strip()
            detected_ingredients = [i.strip().lower() for i in raw_text.split(",")]
            return list(set(detected_ingredients))
        else:
            print("⚠️ ERROR: AI returned an empty response.")
            return []
    except Exception as e:
        print(f"❌ ERROR calling AI: {e}")
        return []

def get_crossing_data_model_response(ingredients_list, user_allergies):
    """
    Cross-checks detected ingredients vs. user allergies.
    Returns bracketed lines like "[status, emoji, ingredient, desc]"
    """
    if not ingredients_list or not user_allergies:
        print("⚠️ ERROR: No ingredients or allergies provided.")
        return []

    ingredients_text = ", ".join(ingredients_list)
    allergies_text = ", ".join(user_allergies)

    prompt_text = load_prompt(CROSSING_PROMPT_FILE)
    if not prompt_text:
        return []

    prompt_text = prompt_text.format(ingredients_text, allergies_text)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[{"role": "user", "content": prompt_text}],
        )

        if response and response.choices:
            raw_response = response.choices[0].message.content.strip()
            return [
                line.strip()
                for line in raw_response.split("\n")
                if line.startswith("[")
            ]
        else:
            print("⚠️ ERROR: AI returned an invalid response.")
            return []
    except Exception as e:
        print(f"❌ ERROR calling AI: {e}")
        return []

def get_infers_allergy_model_response(description: str):
    """
    Analyzes user description to extract known allergies.
    Returns a list of allergies.
    """
    if not description:
        return []

    prompt_text = load_prompt(INFERS_ALLERGY_PROMPT_FILE)
    if not prompt_text:
        return []

    prompt_text = prompt_text.format(description)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[{"role": "user", "content": prompt_text}],
        )

        if response and response.choices:
            raw_text = response.choices[0].message.content.strip()
            print("🔍 DEBUG: Inferring allergies ->", raw_text)

            if raw_text.lower() in ["[noone]", "none", ""]:
                # Re-try with a stricter query
                strict_prompt = f"""
                Extract allergens from this user statement:
                "{description}"
                - ONLY return allergens in a JSON array format: ["allergen1", "allergen2"]
                - DO NOT return "none", "[noone]", or explanations.
                """
                strict_response = client.chat.completions.create(
                    model="gpt-4o-mini-2024-07-18",
                    messages=[{"role": "user", "content": strict_prompt}],
                )
                raw_text = strict_response.choices[0].message.content.strip()
                print("🔍 DEBUG: Re-attempt ->", raw_text)

            # Try parse as JSON
            try:
                allergy_list = json.loads(raw_text)
                if isinstance(allergy_list, list):
                    return [item.strip().lower() for item in allergy_list]
            except json.JSONDecodeError:
                pass

            # Fallback to comma-split
            return [item.strip().lower() for item in raw_text.split(",") if item]
        else:
            print("⚠️ ERROR: AI did not return a valid response.")
            return []
    except Exception as e:
        print(f"❌ ERROR calling AI: {e}")
        return []
