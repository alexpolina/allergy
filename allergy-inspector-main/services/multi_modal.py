import os

# Define correct paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get current script's directory
PROMPT_DIR = os.path.join(BASE_DIR, "../prompts")  # Move to the prompts folder
INGREDIENTS_PROMPT_PATH = os.path.join(PROMPT_DIR, "ingredients_prompt.txt")

def load_prompt(filepath):
    """Reads and returns the text from the prompt file."""
    
    # ✅ Debugging: Print exact file path
    print(f"🔍 DEBUG: Checking if file exists at: {filepath}")

    if not os.path.exists(filepath):
        raise ValueError(f"❌ ERROR: Prompt file not found at {filepath}")

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read().strip()
    except Exception as e:
        raise ValueError(f"⚠️ ERROR: Unable to read the prompt file: {e}")

# ✅ Test the function directly when running this file
if __name__ == "__main__":
    print("Testing prompt loading...")
    prompt_text = load_prompt(INGREDIENTS_PROMPT_PATH)
    print("✅ Loaded prompt:", prompt_text)
