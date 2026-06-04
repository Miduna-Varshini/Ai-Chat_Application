from supabase import create_client, Client
from dotenv import load_dotenv
import streamlit as st
import os

load_dotenv()


@st.cache_resource
def get_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url:
        raise ValueError("SUPABASE_URL not found in .env")

    if not key:
        raise ValueError("SUPABASE_KEY not found in .env")

    return create_client(url, key)


# -------------------------
# TASK FUNCTIONS
# -------------------------

def add_task(title, description=""):
    try:
        supabase = get_client()

        response = (
            supabase.table("tasks")
            .insert(
                {
                    "title": title,
                    "description": description
                }
            )
            .execute()
        )

        return response

    except Exception as e:
        print(f"ADD TASK ERROR: {e}")
        raise


def get_tasks():
    try:
        supabase = get_client()

        response = (
            supabase.table("tasks")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

        return response.data

    except Exception as e:
        print(f"GET TASKS ERROR: {e}")
        return []


def delete_task(task_id):
    try:
        supabase = get_client()

        (
            supabase.table("tasks")
            .delete()
            .eq("id", task_id)
            .execute()
        )

    except Exception as e:
        print(f"DELETE ERROR: {e}")
        raise


def update_status(task_id, status):
    try:
        supabase = get_client()

        (
            supabase.table("tasks")
            .update(
                {
                    "status": status
                }
            )
            .eq("id", task_id)
            .execute()
        )

    except Exception as e:
        print(f"UPDATE ERROR: {e}")
        raise


# -------------------------
# CHAT FUNCTIONS
# -------------------------

def save_message(session_id, role, message):
    try:
        supabase = get_client()

        (
            supabase.table("chat_history")
            .insert(
                {
                    "session_id": session_id,
                    "role": role,
                    "message": message
                }
            )
            .execute()
        )

    except Exception as e:
        print(f"SAVE CHAT ERROR: {e}")
        raise


def load_chat(session_id):
    try:
        supabase = get_client()

        response = (
            supabase.table("chat_history")
            .select("*")
            .eq("session_id", session_id)
            .order("created_at")
            .execute()
        )

        return response.data

    except Exception as e:
        print(f"LOAD CHAT ERROR: {e}")
        return []