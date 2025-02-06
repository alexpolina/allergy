import os
import base64
import json
from openai import OpenAI

# Load environment variables
load_dotenv()
API_KEY = os.getenv("MULTIMODAL_API_KEY")

# Ensure API key exists
if not API_KEY:
    raise ValueError("❌ ERROR: MULTIMODAL_API_KEY is not set. Please check your .env file.")

# Initialize Together API client
client = Together(base_url="https://api.aimlapi.com/v1", api_key=API_KEY)

# File paths for prompts
CROSSING_PROMPT_PATH = "/workspaces/allergy/allergy-inspector-main/prompts/crossing_prompt.txt"
INFERS_ALLERGY_PROMPT_PATH = "/workspaces/allergy/allergy-inspector-main/prompts/infers_allergy_prompt.txt"
INGREDIENTS_PROMPT_PATH = "/workspaces/allergy/allergy-inspector-main/prompts/ingredients_prompt.txt"

def load_prompt(filepath, *args):
    """
    Reads a prompt file and formats it with given arguments.

    :param filepath: Path to the prompt file.
    :param args: Variables to insert into the prompt.
    :return: Formatted prompt text.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            prompt_text = file.read().strip()
            return prompt_text.format(*args) if args else prompt_text
    except FileNotFoundError:
        raise ValueError(f"❌ ERROR: Prompt file not found at {filepath}")
    except Exception as e:
        raise ValueError(f"⚠️ ERROR: Unable to read the prompt file: {e}")

def get_ingredients_model_response(image_url):
    """
    Identifies ingredients in a food image.
    
    :param image_url: URL of the image.
    :return: List of identified ingredients.
    """
    prompt_text = load_prompt(INGREDIENTS_PROMPT_PATH)

    response = client.chat.completions.create(
        model="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
        messages=[
            {"role": "user", "content": [{"type": "image_url", "image_url": {"url": image_url}}, {"type": "text", "text": prompt_text}]}
        ],
        max_tokens=1024,
    )

    return response.choices[0].message.content

def get_crossing_data_model_response(ingredients_text, allergies_text):
    """
    Assesses each ingredient against the user's allergies.
    
    :param ingredients_text: List of detected ingredients.
    :param allergies_text: List of user allergies.
    :return: Structured allergy safety report.
    """
    prompt_text = load_prompt(CROSSING_PROMPT_PATH, ingredients_text, allergies_text)

    response = client.chat.completions.create(
        model="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
        messages=[
            {"role": "user", "content": [{"type": "text", "text": prompt_text}]}
        ],
        max_tokens=1024,
    )

    return response.choices[0].message.content

def get_infers_allergy_model_response(user_description):
    """
    Identifies allergies based on a user's allergy description.
    
    :param user_description: User's allergy description.
    :return: List of detected allergies or "[noone]" if none are found.
    """
    prompt_text = load_prompt(INFERS_ALLERGY_PROMPT_PATH, user_description)

    response = client.chat.completions.create(
        model="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
        messages=[
            {"role": "user", "content": [{"type": "text", "text": prompt_text}]}
        ],
        max_tokens=1024,
    )

    return response.choices[0].message.content

# ✅ Allow direct testing when running the script
if __name__ == "__main__":
    test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/LLama.jpg/444px-LLama.jpg?20050123205659"
    test_ingredients = "peanuts, milk, wheat"
    test_allergies = "nuts, dairy"
    test_user_description = "I get sick when I eat bread and shrimp."

    print("🔍 Identified Ingredients:", get_ingredients_model_response(test_image_url))
    print("⚠️ Allergy Risk Assessment:", get_crossing_data_model_response(test_ingredients, test_allergies))
    print("📌 Inferred Allergies:", get_infers_allergy_model_response(test_user_description))
