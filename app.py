import os
import uuid
import streamlit as st

from groq import Groq
from dotenv import load_dotenv

from supabase_db import save_message
from supabase_db import load_chat

# --------------------------------
# CONFIG
# --------------------------------

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("GROQ_API_KEY not found in .env")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# --------------------------------
# PAGE
# --------------------------------

st.set_page_config(
    page_title="Groq AI Chat",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<div class="main-title">
    <h1>🤖 Groq AI Chat</h1>
    <p>Powered by Groq • Llama 3.3 • Supabase</p>
</div>
""", unsafe_allow_html=True)

# --------------------------------
# NEW CHAT BUTTON
# --------------------------------

col1, col2 = st.columns([1, 6])

with col1:
    if st.button("🆕 New Chat"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

# --------------------------------
# SESSION
# --------------------------------

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

session_id = st.session_state.session_id

# --------------------------------
# LOAD HISTORY
# --------------------------------

if "messages" not in st.session_state:

    try:

        history = load_chat(session_id)

        st.session_state.messages = [
            {
                "role": item["role"],
                "content": item["message"]
            }
            for item in history
        ]

    except Exception as e:

        st.error(f"Failed to load chat history: {e}")
        st.session_state.messages = []

# --------------------------------
# DISPLAY CHAT
# --------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --------------------------------
# USER INPUT
# --------------------------------

prompt = st.chat_input("Type your message...")

if prompt:

    # Show user message

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # Save user message

    try:

        save_message(
            session_id,
            "user",
            prompt
        )

    except Exception as e:

        st.warning(
            f"Could not save user message: {e}"
        )

    # Generate assistant response

    with st.chat_message("assistant"):

        response_placeholder = st.empty()

        full_response = ""

        try:

            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages,
                temperature=0.7,
                stream=True
            )

            for chunk in stream:

                if (
                    chunk.choices
                    and chunk.choices[0].delta
                ):

                    content = (
                        chunk.choices[0]
                        .delta
                        .content
                    )

                    if content:

                        full_response += content

                        response_placeholder.markdown(
                            full_response + "▌"
                        )

            response_placeholder.markdown(
                full_response
            )

        except Exception as e:

            full_response = (
                f"❌ Error generating response:\n\n{e}"
            )

            response_placeholder.markdown(
                full_response
            )

    # Store assistant response

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": full_response
        }
    )

    # Save assistant response

    try:

        save_message(
            session_id,
            "assistant",
            full_response
        )

    except Exception as e:

        st.warning(
            f"Could not save assistant message: {e}"
        )

# ==================================
# MODERN AI CHAT UI
# ==================================

st.markdown("""
<style>

/* App Background */
.stApp {
    background: linear-gradient(
        135deg,
        #0f172a 0%,
        #1e293b 50%,
        #111827 100%
    );
}

/* Hide Streamlit Branding */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

/* Main Container */
.block-container {
    padding-top: 1rem;
    max-width: 1200px;
}

/* Title Styling */
.main-title {
    text-align: center;
    margin-bottom: 20px;
}

.main-title h1 {
    color: #38bdf8;
    font-size: 3rem;
    margin-bottom: 5px;
}

.main-title p {
    color: #cbd5e1;
    font-size: 1rem;
}

/* Buttons */
.stButton > button {
    width: 100%;
    height: 45px;
    border-radius: 12px;
    border: none;
    font-weight: 600;
    color: white;
    background: linear-gradient(
        135deg,
        #06b6d4,
        #3b82f6
    );
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0px 8px 20px rgba(59,130,246,0.4);
}

/* Chat Input */
.stChatInput input {
    background-color: #1e293b !important;
    color: white !important;
    border-radius: 15px !important;
    border: 1px solid #475569 !important;
}

/* User Message */
[data-testid="chat-message-user"] {
    background: linear-gradient(
        135deg,
        #2563eb,
        #1d4ed8
    );
    border-radius: 15px;
    padding: 10px;
    margin-bottom: 10px;
}

/* Assistant Message */
[data-testid="chat-message-assistant"] {
    background: rgba(30,41,59,0.95);
    border-radius: 15px;
    padding: 10px;
    margin-bottom: 10px;
    border-left: 4px solid #38bdf8;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid #334155;
}

/* Success Messages */
.stSuccess {
    border-radius: 12px;
}

/* Warning Messages */
.stWarning {
    border-radius: 12px;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-thumb {
    background: #38bdf8;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)
