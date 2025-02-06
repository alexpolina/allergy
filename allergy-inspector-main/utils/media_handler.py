import base64
import streamlit as st
from PIL import Image
import io

def image_to_base64(image_bytes):
    """
    Converts image bytes to a base64-encoded string.
    """
    try:
        return base64.b64encode(image_bytes).decode("utf-8")
    except FileNotFoundError:
        return "Image file not found. Please check the path."
    except Exception as e:
        return f"An error occurred: {str(e)}"
