import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai

app = Flask(__name__)

# 設定 Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# 儲存每個用戶的對話歷史
chat_history = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    # 接收訊息
    incoming_msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")  # 發送者的號碼

    # 每個用戶有自己的對話歷史
    if sender not in chat_history:
        chat_history[sender] = []

    # 加入用戶訊息
    chat_history[sender].append({
        "role": "user",
        "parts": [incoming_msg]
    })

    # 呼叫 Gemini
    try:
        chat = model.start_chat(history=chat_history[sender][:-1])
        response = chat.send_message(incoming_msg)
        reply_text = response.text

        # 加入 AI 回覆到歷史
        chat_history[sender].append({
            "role": "model",
            "parts": [reply_text]
        })

        # 限制歷史長度，避免太長
        if len(chat_history[sender]) > 20:
            chat_history[sender] = chat_history[sender][-20:]

    except Exception as e:
        reply_text = f"發生錯誤：{str(e)}"

    # 回傳給 WhatsApp
    resp = MessagingResponse()
    resp.message(reply_text)
    return str(resp)

@app.route("/", methods=["GET"])
def index():
    return "WhatsApp Bot is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
```

---

## 第三步：部署到 Render

1. 把這兩個檔案上傳到 [GitHub](https://github.com)（建立新 repo）
2. 去 [render.com](https://render.com) 註冊，連結 GitHub
3. 建立新的 **Web Service**，選你的 repo
4. 設定：
```
Build Command: pip install -r requirements.txt
Start Command: python app.py
```
5. 在 Environment Variables 加入：
```
GEMINI_API_KEY = 你的Gemini Key
```
6. 部署完成後會得到一個網址，例如：
```
https://whatsapp-bot-xxxx.onrender.com
```

---

## 第四步：設定 Twilio Webhook

1. 回到 Twilio Console
2. 找到 WhatsApp Sandbox 設定
3. 在 **"When a message comes in"** 填入：
```
https://whatsapp-bot-xxxx.onrender.com/webhook
```
4. 儲存

---

## 測試

用手機傳訊息給 Twilio 的 WhatsApp Sandbox 號碼，就會收到 Gemini 的回覆！

---

## 整個流程圖
```
你的手機 WhatsApp
    ↓ 傳訊息
Twilio Sandbox
    ↓ 轉發到 webhook
Render 伺服器（app.py）
    ↓ 呼叫
Gemini API（免費）
    ↓ 回覆
Render 伺服器
    ↓ 回傳
你的手機 WhatsApp
