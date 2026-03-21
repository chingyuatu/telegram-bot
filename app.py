@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")
    
    print(f"收到訊息: {incoming_msg} 來自: {sender}")  # ← 加這行

    if sender not in chat_history:
        chat_history[sender] = []

    chat_history[sender].append({
        "role": "user",
        "parts": [{"text": incoming_msg}]
    })

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=chat_history[sender]
        )
        reply_text = response.text
        print(f"Gemini 回覆: {reply_text}")  # ← 加這行

        chat_history[sender].append({
            "role": "model",
            "parts": [{"text": reply_text}]
        })

        if len(chat_history[sender]) > 20:
            chat_history[sender] = chat_history[sender][-20:]

    except Exception as e:
        reply_text = f"Error: {str(e)}"
        print(f"錯誤: {str(e)}")  # ← 加這行

    resp = MessagingResponse()
    resp.message(reply_text)
    return str(resp)
