import requests
import streamlit as st
import os

def get_api_url() -> str:
    """Dynamically get the API backend URL, auto-detecting Docker vs Local host."""
    env_url = os.environ.get("API_URL")
    if env_url and env_url != "http://localhost:8000":
        return env_url
    try:
        import socket
        socket.gethostbyname("backend")
        return "http://backend:8000"
    except Exception:
        pass
    return env_url or st.secrets.get("API_URL", "http://localhost:8000")

def sign_up(name: str, email: str, password: str):
    api_url = get_api_url()
    try:
        res = requests.post(f"{api_url}/auth/sign-up", json={
            "name": name, "email": email, "password": password
        }, timeout=20)
        
        try:
            data = res.json()
        except Exception:
            data = {"error": res.text or f"Status: {res.status_code}"}

        if res.status_code == 200 and isinstance(data, dict) and "token" in data:
            token_val = data["token"]
            st.session_state["token"] = token_val.get("access_token") if isinstance(token_val, dict) else token_val
            st.session_state["user"] = data.get("user")
        elif res.status_code != 200 and isinstance(data, dict) and "error" not in data:
            data["error"] = data.get("message") or data.get("detail") or res.text
        return data
    except requests.exceptions.ConnectionError:
        return {"error": f"Failed to connect to backend at {api_url}. Is the FastAPI backend running?"}
    except Exception as e:
        return {"error": str(e)}

def sign_in(email: str, password: str):
    api_url = get_api_url()
    try:
        res = requests.post(f"{api_url}/auth/sign-in", json={
            "email": email, "password": password
        }, timeout=20)
        
        try:
            data = res.json()
        except Exception:
            data = {"error": res.text or f"Status: {res.status_code}"}

        if res.status_code == 200 and isinstance(data, dict) and "token" in data:
            token_val = data["token"]
            st.session_state["token"] = token_val.get("access_token") if isinstance(token_val, dict) else token_val
            st.session_state["user"] = data.get("user")
        elif res.status_code != 200 and isinstance(data, dict) and "error" not in data:
            data["error"] = data.get("message") or data.get("detail") or res.text
        return data
    except requests.exceptions.ConnectionError:
        return {"error": f"Failed to connect to backend at {api_url}. Is the FastAPI backend running?"}
    except Exception as e:
        return {"error": str(e)}

def sign_out():
    if "token" in st.session_state:
        del st.session_state["token"]
    if "user" in st.session_state:
        del st.session_state["user"]

def get_headers():
    if "token" in st.session_state:
        return {"Authorization": f'Bearer {st.session_state["token"]}'}
    return {}

def require_auth():
    if "token" not in st.session_state:
        st.warning("Please sign in to access this page.")
        st.stop()
