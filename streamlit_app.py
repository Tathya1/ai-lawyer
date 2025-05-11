import streamlit as st
import os

# Import backend modules
from country_selector_st import SUPPORTED_COUNTRIES
from data_loader_st import DATA_DIR, load_constitution_text
from legal_data_handler_st import get_legal_context_st
from llm_integration_st import get_ai_response_st, SYSTEM_PROMPT
from conversation_manager_st import (
    initialize_chat_history,
    add_to_history_st,
    clear_history_st,
    get_history_for_llm
)

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Lawyer Prototype",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Styling (Optional) ---
st.markdown("""
<style>
    .stApp {
        /* background-color: #f0f2f6; */
    }
    .stButton>button {
        border-radius: 5px;
        padding: 10px 15px;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
initialize_chat_history(st.session_state)

# --- Ensure we have a current_country in state ---
if "current_country" not in st.session_state:
    st.session_state.current_country = list(SUPPORTED_COUNTRIES.keys())[0]

# --- Seed constitution into history once per country ---
if (
    "const_loaded_for" not in st.session_state
    or st.session_state.const_loaded_for != st.session_state.current_country
):
    # 1) Clear any prior conversation
    clear_history_st(st.session_state)

    # 2) Load the full constitution text once
    raw_const = load_constitution_text(st.session_state.current_country)

    # 3) Seed the history with:
    #    a) your SYSTEM_PROMPT
    #    b) the full constitution text
    add_to_history_st(st.session_state, "system", SYSTEM_PROMPT)
    add_to_history_st(
        st.session_state,
        "system",
        f"--- CONSTITUTION OF {st.session_state.current_country.upper()} ---\n{raw_const}"
    )

    # 4) Remember we did this for this country
    st.session_state.const_loaded_for = st.session_state.current_country


# --- Helper to check data files ---
def check_data_files_exist():
    if not os.path.exists(DATA_DIR):
        st.error(f"The '{DATA_DIR}/' directory is missing. Please create it.")
        return False
    for fname in ["japan_constitution.txt", "monaco_constitution.txt"]:
        path = os.path.join(DATA_DIR, fname)
        if not os.path.exists(path):
            st.warning(f"File '{path}' not found. Please add and populate it.")
    return True

# --- Sidebar ---
with st.sidebar:
    st.title("⚖️ AI Lawyer Settings")
    st.markdown("---")

    # Country selector (updates state and triggers a rerun automatically)
    selected = st.selectbox(
        "Select Jurisdiction:",
        options=list(SUPPORTED_COUNTRIES.keys()),
        format_func=lambda k: SUPPORTED_COUNTRIES[k],
        index=list(SUPPORTED_COUNTRIES.keys()).index(st.session_state.current_country),
        key="country_select_key",
    )
    if selected != st.session_state.current_country:
        st.session_state.current_country = selected
        # Reset the loaded flag so the constitution is re-seeded on next run
        if "const_loaded_for" in st.session_state:
            del st.session_state.const_loaded_for
        # st.experimental_rerun()

    st.markdown("---")
    st.markdown("### Client-Lawyer Privilege")
    if st.button("🗑️ Clear Conversation History"):
        clear_history_st(st.session_state)
        # Also clear the seed so next message will re-add constitution
        if "const_loaded_for" in st.session_state:
            del st.session_state.const_loaded_for
        st.success("Conversation history cleared for this session.")

    st.markdown("---")
    st.info("This is a prototype. Always consult a qualified human lawyer.")
    st.markdown("Ask 'show constitution' to view the loaded constitutional text.")

# --- Main Interface ---
st.title(f"AI Lawyer ({SUPPORTED_COUNTRIES[st.session_state.current_country]})")
st.caption("Your AI-powered legal information assistant prototype.")

check_data_files_exist()

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle user input
if prompt := st.chat_input(f"Ask about {SUPPORTED_COUNTRIES[st.session_state.current_country]} law..."):
    # save and show user prompt
    add_to_history_st(st.session_state, "user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    # generate AI response
    with st.chat_message("assistant"):
        with st.spinner("Researching..."):
            history = get_history_for_llm(st.session_state)
            ai_response = get_ai_response_st(
                prompt,
                st.session_state.current_country,
                history
            )
            st.markdown(ai_response)

    # save AI response
    add_to_history_st(st.session_state, "assistant", ai_response)
