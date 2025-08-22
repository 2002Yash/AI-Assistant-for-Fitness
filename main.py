import streamlit as st
import db

# --- PAGE CONFIGURATION ---
# This command reads the .streamlit/config.toml file for theme settings.
st.set_page_config(
    page_title="Personal Fitness AI",
    page_icon="💪",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- DATABASE INITIALIZATION ---
database = db.get_db()
db.personal_data_collection = database.get_collection("personal_data")
db.notes_collection = database.get_collection("Notes1") 

from ai import ask_ai, get_macros
from profiles import create_profile, get_notes, get_profile
from form_submit import update_personal_info, add_note, delete_note

# --- CUSTOM CSS FOR DARK THEME REFINEMENTS ---
def load_css():
    """Injects custom CSS to refine the dark theme."""
    st.markdown("""
        <style>
            /* Import a clean, modern font */
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

            html, body, [class*="st-"], [class*="css-"] {
                font-family: 'Poppins', sans-serif;
            }

            /* Main title styling */
            h1 {
                color: #FFFFFF; /* White title for high contrast */
                font-weight: 600;
                text-align: center;
            }
            
            /* Section headers */
            h2, h3 {
                color: #EAEAEA; /* Light grey for headers */
                font-weight: 600;
            }

            /* Input widgets - refining the dark theme */
            .stTextInput > div > div > input,
            .stNumberInput > div > div > input,
            .stTextArea > div > textarea,
            .stMultiSelect > div > div {
                border-radius: 8px;
                border: 1px solid #3a3a3a; /* Darker border */
                background-color: #1E1E1E; /* Match secondary background */
                color: #EAEAEA;
                font-size: 16px;
                padding: 12px;
            }
            
            /* Primary button styling */
            .stButton > button, .stFormSubmitButton > button {
                border-radius: 8px;
                border: none;
                background-color: #3D5CFF; /* Bright blue accent color */
                color: #FFFFFF;
                padding: 12px 28px;
                width: 100%;
                transition: all 0.2s ease;
                font-weight: 600;
                font-size: 16px;
            }

            /* Button hover effect */
            .stButton > button:hover, .stFormSubmitButton > button:hover {
                background-color: #3149cc; /* Slightly darker blue on hover */
            }
            
            /* Container styling for forms and sections */
            div[data-testid="stForm"], .st-emotion-cache-1r4qj8v {
                background-color: #1E1E1E; /* Match secondary background */
                border: 1px solid #2e2e2e;
                border-radius: 12px;
                padding: 25px;
            }

            /* Style for st.metric to improve readability */
            div[data-testid="stMetric"] {
                background-color: #2e2e2e;
                padding: 15px;
                border-radius: 8px;
            }
        </style>
    """, unsafe_allow_html=True)

# Load the styles into the app
load_css()

# --- APP LAYOUT AND CONTENT ---
st.title("Personal Fitness AI")

# (The rest of the Python functions for the app layout are the same as before)

@st.fragment
def personal_data_form():
    with st.form("personal_data"):
        st.header("Personal Data")
        profile = st.session_state.profile
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name", value=profile["general"]["name"])
            weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1, value=float(profile["general"]["weight"]))
        with col2:
            age = st.number_input("Age", min_value=1, step=1, value=profile["general"]["age"])
            height = st.number_input("Height (cm)", min_value=0.0, step=0.1, value=float(profile["general"]["height"]))
        
        genders = ["Male", "Female", "Other"]
        gender = st.radio("Gender", genders, horizontal=True, index=genders.index(profile["general"].get("gender", "Male")))
        
        activities = ("Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Super Active")
        activity_level = st.selectbox("Activity Level", activities, index=activities.index(profile["general"].get("activity_level", "Moderately Active")))

        if st.form_submit_button("Save Personal Data"):
            update_personal_info(st.session_state.profile, "general", name=name, age=age, weight=weight, height=height, gender=gender, activity_level=activity_level)
            st.success("Personal data saved.")


@st.fragment
def goals_and_macros_section():
    col1, col2 = st.columns(2)
    with col1:
        with st.form("goals_form"):
            st.header("Goals")
            profile = st.session_state.profile
            goals = st.multiselect("Select your Goals", ["Muscle Gain", "Fat Loss", "Stay Active"], default=profile.get("goals", ["Muscle Gain"]))
            if st.form_submit_button("Save Goals"):
                update_personal_info(st.session_state.profile, "goals", goals=goals)
                st.success("Goals saved.")
    
    with col2:
        with st.container(border=True):
            st.header("Macros")
            profile = st.session_state.profile
            col_a, col_b = st.columns(2)
            col_a.metric("Calories", profile["nutrition"].get("calories", "N/A"))
            col_b.metric("Protein", f"{profile['nutrition'].get('protein', 'N/A')}g")
            col_c, col_d = st.columns(2)
            col_c.metric("Fat", f"{profile['nutrition'].get('fat', 'N/A')}g")
            col_d.metric("Carbs", f"{profile['nutrition'].get('carbs', 'N/A')}g")

            if st.button("Generate Macros with AI"):
                with st.spinner("Calculating your macros..."):
                    result = get_macros(profile.get("general"), profile.get("goals"))
                    st.session_state.profile["nutrition"] = result
                st.success("AI has generated your macros.")
                st.rerun()


@st.fragment
def notes_and_ai_section():
    st.markdown("---")
    st.header("Notes & AI Assistant")
    
    new_note = st.text_input("Add a new note:", placeholder="e.g., I am vegetarian")
    if st.button("Add Note"):
        if new_note:
            note = add_note(new_note, st.session_state.profile_id)
            st.session_state.notes.append(note)
            st.rerun()

    if st.session_state.notes:
        with st.expander("View All Notes"):
            for i, note in enumerate(st.session_state.notes):
                note_cols = st.columns([0.9, 0.1])
                note_cols[0].info(note.get("text"))
                if note_cols[1].button("🗑️", key=f"del_{i}", help="Delete note"):
                    delete_note(note.get("_id"))
                    st.session_state.notes.pop(i)
                    st.rerun()

    user_question = st.text_area("Ask AI a question:", height=150, placeholder="e.g., Give me a 7-day workout plan...")
    if st.button("Get AI Advice"):
        if user_question:
            with st.spinner("AI is thinking..."):
                result = ask_ai(st.session_state.profile, user_question)
                st.info(result)
        else:
            st.warning("Please enter a question.")


def main_app():
    if "profile" not in st.session_state:
        try:
            database.create_collection("personal_data")
        except Exception:
            pass
        profile_id = 1
        profile = get_profile(profile_id)
        if not profile:
            _, profile = create_profile(profile_id)
        st.session_state.profile = profile
        st.session_state.profile_id = profile_id

    if "notes" not in st.session_state:
        st.session_state.notes = get_notes(st.session_state.profile_id)

    personal_data_form()
    st.markdown("<br>", unsafe_allow_html=True)
    goals_and_macros_section()
    notes_and_ai_section()


if __name__ == "__main__":
    main_app()