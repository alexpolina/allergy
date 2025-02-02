import os

# ✅ Fix Path Issues
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_DIR = os.path.join(BASE_DIR, "../prompts")  # If running inside `services/`
if not os.path.exists(PROMPT_DIR):
    PROMPT_DIR = os.path.join(BASE_DIR, "prompts")  # If running from root

INGREDIENTS_PROMPT_PATH = os.path.join(PROMPT_DIR, "ingredients_prompt.txt")

def load_prompt(filepath):
    """Reads and returns the text from the prompt file."""
    print(f"🔍 DEBUG: Checking if file exists at: {filepath}")

    if not os.path.exists(filepath):
        raise ValueError(f"❌ ERROR: Prompt file not found at {filepath}")

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read().strip()
    except Exception as e:
        raise ValueError(f"⚠️ ERROR: Unable to read the prompt file: {e}")
