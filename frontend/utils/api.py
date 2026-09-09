import requests
import streamlit as st
import os

# Docker sets API_URL as an environment variable; fall back to secrets.toml for local dev
def _get_api_url():
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

class _ApiUrlProxy:
    def __str__(self):
        return _get_api_url()
    def __format__(self, format_spec):
        return _get_api_url()

API_URL = _ApiUrlProxy()

def get_profile():
    from utils.auth import get_headers
    res = requests.get(f"{API_URL}/profile/me", headers=get_headers())
    return res

def create_profile(data):
    from utils.auth import get_headers
    res = requests.post(f"{API_URL}/profile/create", json=data, headers=get_headers())
    return res

def update_profile(data):
    from utils.auth import get_headers
    res = requests.put(f"{API_URL}/profile/update", json=data, headers=get_headers())
    return res

def submit_questionnaire(answers):
    from utils.auth import get_headers
    res = requests.post(f"{API_URL}/questionnaire/submit", json={"answers": answers}, headers=get_headers())
    return res

def generate_portfolio():
    from utils.auth import get_headers
    res = requests.post(f"{API_URL}/portfolio/generate", json={}, headers=get_headers())
    return res

def get_current_portfolio():
    from utils.auth import get_headers
    res = requests.get(f"{API_URL}/portfolio/current", headers=get_headers())
    return res

def get_portfolio_history():
    from utils.auth import get_headers
    res = requests.get(f"{API_URL}/portfolio/history", headers=get_headers())
    return res

def get_portfolio_summary():
    from utils.auth import get_headers
    res = requests.get(f"{API_URL}/portfolio/summary", headers=get_headers())
    return res

def get_expected_returns():
    from utils.auth import get_headers
    res = requests.get(f"{API_URL}/portfolio/expected-returns", headers=get_headers())
    return res

def compare_portfolio(risk_level):
    from utils.auth import get_headers
    res = requests.get(f"{API_URL}/portfolio/compare/{risk_level}", headers=get_headers())
    return res

def get_risk_profiles():
    res = requests.get(f"{API_URL}/reference/risk-profiles")
    return res

def import_transactions(file):
    from utils.auth import get_headers
    return requests.post(f"{API_URL}/finpulse/imports/transactions", files={"file": file}, headers=get_headers())

def get_imports():
    from utils.auth import get_headers
    return requests.get(f"{API_URL}/finpulse/imports", headers=get_headers())

def create_goal(data):
    from utils.auth import get_headers
    return requests.post(f"{API_URL}/finpulse/goals", json=data, headers=get_headers())

def get_goals():
    from utils.auth import get_headers
    return requests.get(f"{API_URL}/finpulse/goals", headers=get_headers())

def get_goal_simulation(goal_id):
    from utils.auth import get_headers
    return requests.get(f"{API_URL}/finpulse/goals/{goal_id}/simulation", headers=get_headers())

def get_health():
    from utils.auth import get_headers
    return requests.get(f"{API_URL}/finpulse/health", headers=get_headers())

def get_alerts():
    from utils.auth import get_headers
    return requests.get(f"{API_URL}/finpulse/alerts", headers=get_headers())

def get_rebalancing():
    from utils.auth import get_headers
    return requests.get(f"{API_URL}/finpulse/rebalancing", headers=get_headers())
