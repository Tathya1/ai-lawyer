"""
conversation_manager_st.py
Manages chat history using Streamlit's session state (passed as an argument).
"""

def initialize_chat_history(st_session_state):
    """Initializes chat history in Streamlit's session state if not present."""
    if "messages" not in st_session_state:
        st_session_state.messages = [] # Each item: {"role": "user/assistant", "content": "..."}
    if "current_country" not in st_session_state:
        st_session_state.current_country = "Japan" # Default country changed to Japan

def add_to_history_st(st_session_state, role: str, content: str):
    """Adds a message to the chat history in Streamlit's session state."""
    st_session_state.messages.append({"role": role, "content": content})

def clear_history_st(st_session_state):
    """Clears the chat history in Streamlit's session state."""
    st_session_state.messages = []
    # Optionally, you might want to reset other session-specific states here
    # st_session_state.current_country = "Japan" # Or keep the country
    return "Chat history cleared. The AI will not remember this conversation in the current session display."

def get_history_for_llm(st_session_state) -> list:
    """Returns the chat history in a format suitable for some LLM APIs."""
    return st_session_state.messages[:] # Return a copy
