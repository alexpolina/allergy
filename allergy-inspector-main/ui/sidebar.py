import os
import sys
import streamlit as st

# Ensure this script can be run directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.session_state import init_session_state
from utils.media_handler import image_to_base64
from services.multi_modal import get_infers_allergy_model_response

def sidebar_setup():
    """Sets up the sidebar UI for user allergy preferences."""
    init_session_state()
    st.sidebar.markdown("# Allergy Detector 🕵️‍♀️")

    if "setup_complete" not in st.session_state:
        st.session_state["setup_complete"] = False

    def setup():
        with st.container():
            st.session_state["user_name"] = st.text_input(
                "Enter your name (optional):",
                value=st.session_state.get("user_name", "Guest")
            )

            description = st.text_area(
                "Describe what made you sick previously when you ate it (optional):",
                value=st.session_state.get("user_description", "")
            )

            # Automatically infer allergies from user description
            if description:
                with st.spinner("Processing..."):
                    response = get_infers_allergy_model_response(description)
                    if response and response != "[noone]":
                        response_list = [item.strip() for item in response]  # Ensure clean list
                        for item in response_list:
                            st.session_state["allergy_options"].append(item)
                            st.session_state["user_allergies"].append(item)

                        # Remove duplicates while preserving order
                        st.session_state["allergy_options"] = list(dict.fromkeys(st.session_state["allergy_options"]))
                        st.session_state["user_allergies"] = list(dict.fromkeys(st.session_state["user_allergies"]))
                    else:
                        st.write("No allergies identified.")

            user_allergies = st.multiselect(
                "Select your allergies:",
                options=st.session_state["allergy_options"],
                default=st.session_state["user_allergies"],
                help="Choose from common allergy categories."
            )

            if st.button("Confirm Your Choice"):
                if user_allergies:
                    st.session_state["allergies_selected"] = True
                    st.session_state["user_allergies"] = user_allergies
                    st.session_state["setup_complete"] = True
                    # Replaces `st.experimental_set_query_params()`
                    st.query_params.update()  # Update query params without args
                    st.rerun()
                else:
                    st.warning("Please select at least one allergy.")

    if not st.session_state["setup_complete"]:
        setup()
    else:
        st.sidebar.markdown("---")
        if st.sidebar.button("Edit preferences"):
            st.session_state["setup_complete"] = False
            st.session_state["allergies_selected"] = False
            st.rerun()

        # Show user avatar or default
        if st.session_state.get("user_avatar"):
            st.sidebar.image(st.session_state["user_avatar"], width=120)
        else:
            st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Unknown_person.jpg/434px-Unknown_person.jpg", width=120)

        # Show user name
        st.sidebar.markdown("## " + (st.session_state["user_name"] or "Guest"))

        # Show user allergies
        allergies_text = ", ".join(st.session_state.get("user_allergies", []))
        st.sidebar.markdown(f"⚠️ **Allergies:** {allergies_text if allergies_text else 'None selected'}")

        st.sidebar.markdown("We are one of the famous allergy detectors that keep people from getting sick.")

        # Quick bullet points
        st.sidebar.markdown("## Why you should choose us?")
        st.sidebar.markdown("✅ We don't ask you for any fee. You can use us freely anytime!")
        st.sidebar.markdown("✅ We are really accurate!*")
        st.sidebar.markdown("✅ We are fun to interact with!")

        st.sidebar.markdown("## Fun fact*")
        option = st.sidebar.radio(
            "Do you want to know why we are so accurate?",
            ("Select an option ❗", "Yes, tell me!", "No, I don't want to know this!")
        )
        if option == "Yes, tell me!":
            st.sidebar.markdown("Well, we use the powerful Aria model 💪.")
            st.sidebar.markdown("The Aria model helps us analyze ingredients efficiently!")
        elif option == "No, I don't want to know this!":
            st.sidebar.markdown("No issues, your loss :)")

