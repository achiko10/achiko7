import requests
import time
import os

TOKEN = "8774946365:AAH4zW_4yOdagyWD3p9xQn6qobmNor-RqOI"
URL = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

print("Waiting for you to send a message to the bot...")

while True:
    response = requests.get(URL).json()
    if response.get("ok") and response.get("result"):
        # Get the chat id of the first message
        chat_id = response["result"][0]["message"]["chat"]["id"]
        print(f"\nSUCCESS! Found your Chat ID: {chat_id}")
        
        # Save it to a file so we can read it automatically
        with open("chat_id.txt", "w") as f:
            f.write(str(chat_id))
        break
    time.sleep(2)
