"""Example client script to register/login and chat with the LearnPath app.

This script demonstrates a minimal programmatic flow that a tester can use to
exercise the MVP without using the browser UI.

Usage (after running the Flask app):
    python example_client.py

It will attempt to log in with a test account, create it if missing, and then
send a short sequence of messages to request a learning plan. It prints the
JSON responses from `/api/chat` and, when a plan is created, prints the plan id.
"""
import requests
import random
import time

BASE = "http://127.0.0.1:5000"

# Choose an email that won't conflict often
RAND = random.randint(1000, 9999)
TEST_USER = {
    "name": f"TestUser{RAND}",
    "email": f"testuser{RAND}@example.com",
    "password": "TestPass123",
}

session = requests.Session()


def register_if_needed():
    # Try login first (in case account exists)
    login_data = {"email": TEST_USER["email"], "password": TEST_USER["password"]}
    r = session.post(f"{BASE}/login", data=login_data, allow_redirects=False)
    if r.status_code == 302:
        print("Logged in existing user.")
        return True

    # Otherwise try register
    reg_data = {"name": TEST_USER["name"], "email": TEST_USER["email"], "password": TEST_USER["password"]}
    r = session.post(f"{BASE}/register", data=reg_data, allow_redirects=False)
    if r.status_code == 302:
        print("Registered and logged in as new test user.")
        return True

    print("Registration/Login may have failed. Status:", r.status_code)
    return False


def send_chat(message, conversation_id=None):
    payload = {"message": message}
    if conversation_id is not None:
        payload["conversation_id"] = conversation_id
    r = session.post(f"{BASE}/api/chat", json=payload)
    try:
        return r.json()
    except Exception:
        print("Non-JSON response:", r.text[:200])
        return None


def main():
    ok = register_if_needed()
    if not ok:
        print("Cannot continue without login/register.")
        return

    # Chat sequence that should create a plan
    conv_id = None

    steps = [
        "Hi",
        "I want to learn Python",
        "Beginner",
        "I can study 5 hours per week for 5 weeks"
    ]

    last_response = None
    for msg in steps:
        print(f"-> Sending: {msg}")
        resp = send_chat(msg, conversation_id=conv_id)
        print("<- Reply:", resp.get("reply") if isinstance(resp, dict) else resp)
        if isinstance(resp, dict):
            conv_id = resp.get("conversation_id", conv_id)
            if resp.get("plan_ready"):
                print("Plan created! plan_id:", resp.get("plan_id"))
                last_response = resp
                break
        time.sleep(0.5)

    if last_response and last_response.get("plan_id"):
        plan_id = last_response["plan_id"]
        print(f"You can open the plan at: {BASE}/learning-path/{plan_id}")


if __name__ == "__main__":
    main()
