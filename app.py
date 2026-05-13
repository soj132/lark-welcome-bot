import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- Config ---
APP_ID = "cli_aa8e8364f563de15"
APP_SECRET = "mt8PFUb75aCh8jq993Lblcxw8NHki1Do"
VERIFICATION_TOKEN = "gLmv9matJzhWQRCSnUrgZee4pkwrOd1J
"

def get_tenant_access_token():
    url = "https://open.larksuite.com/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    return resp.json().get("tenant_access_token")

def send_welcome_message(chat_id, user_ids):
    token = get_tenant_access_token()
    url = "https://open.larksuite.com/open-apis/im/v1/messages"
    mentions = " ".join([f'<at user_id="{uid}"></at>' for uid in user_ids])
    content = json.dumps({"text": f"Welcome to the chat! 👋 {mentions}"})
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    params = {"receive_id_type": "chat_id"}
    body = {"receive_id": chat_id, "msg_type": "text", "content": content}
    requests.post(url, headers=headers, params=params, json=body)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if data.get("type") == "url_verification":
        return jsonify({"challenge": data["challenge"]})
    header = data.get("header", {})
    if header.get("token") != VERIFICATION_TOKEN:
        return jsonify({"error": "Invalid token"}), 403
    if header.get("event_type") == "im.chat.member.user.added_v1":
        event = data.get("event", {})
        chat_id = event.get("chat_id")
        new_members = event.get("users", [])
        user_ids = [u["user_id"]["user_id"] for u in new_members if u.get("user_id")]
        if chat_id and user_ids:
            send_welcome_message(chat_id, user_ids)
    return jsonify({"code": 0})

if __name__ == "__main__":
    app.run(port=3000)
