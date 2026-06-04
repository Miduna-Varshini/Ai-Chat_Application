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

st.title("🤖 Groq AI Chat")
st.caption("Streamlit + Groq + Supabase")

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