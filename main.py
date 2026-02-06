import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Hugging Face Configuration
HF_TOKEN = os.getenv("HF_TOKEN")
# Friendly AI / Serverless URL
HF_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"

# Evolution API Configuration
EVO_URL = os.getenv("EVO_URL")
EVO_KEY = os.getenv("EVO_KEY")
INSTANCE = os.getenv("INSTANCE_NAME", "Pushpita")

@app.route('/webhook', methods=['POST'])
def handle_whatsapp():
    data = request.json
    
    # Check if message is incoming
    if data.get('event') == 'messages.upsert' and not data['data']['key']['fromMe']:
        user_msg = data['data']['message'].get('conversation') or ""
        sender = data['data']['key']['remoteJid']

        if user_msg:
            # 1. Hugging Face (Mistral v0.3) se answer lo
            headers = {"Authorization": f"Bearer {HF_TOKEN}"}
            # v0.3 prompt format
            payload = {"inputs": f"<s>[INST] {user_msg} [/INST]"}
            
            hf_res = requests.post(HF_URL, headers=headers, json=payload)
            response_json = hf_res.json()
            
            # Text clean-up
            ai_reply = response_json[0]['generated_text'].split('[/INST]')[-1].strip()

            # 2. Evolution API se reply bhejo
            requests.post(f"{EVO_URL}/message/sendText/{INSTANCE}", 
                          headers={"apikey": EVO_KEY}, 
                          json={"number": sender, "text": ai_reply})

    return "OK", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
