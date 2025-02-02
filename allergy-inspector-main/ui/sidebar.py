import streamlit as st

# Remove incorrect import if it was causing issues
# from services.multi_modal import get_infers_allergy_model_response

def sidebar_setup():
    st.sidebar.markdown("# Allergy Detector 🕵️‍♀️")
    st.sidebar.markdown("---")
    if st.sidebar.button("Edit preferences"):
        st.session_state["allergies_selected"] = None
        st.rerun()
    st.sidebar.markdown("We help detect allergies using AI.")
