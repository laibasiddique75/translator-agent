import os
import json
from dotenv import load_dotenv
import chainlit as cl
from litellm import completion


# Load environment variables
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("❌ GEMINI_API_KEY is missing in the .env file")

# Chat start: initialize session
@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("chat_history", [])
    await cl.Message(
        content=(
            "👋 Welcome to the **Translator Agent by Laiba Siddique**!\n\n"
            "Please tell me:\n"
            "1️⃣ **What you want to translate?**\n"
            "2️⃣ **From which language to which language?**"
        )
    ).send()

# Handle incoming message
@cl.on_message
async def on_message(message: cl.Message):
    loading_msg = cl.Message(content="🔄 Translating... Please wait!")
    await loading_msg.send()

    # Validate the message
    user_input = message.content.strip()
    if not user_input:
        loading_msg.content = "⚠️ Please enter some text to translate."
        await loading_msg.update()
        return

    # Retrieve chat history
    history = cl.user_session.get("chat_history")
    if not isinstance(history, list):
        history = []

    # Append current user message
    history.append({"role": "user", "content": user_input})

    try:
        # Gemini model call via LiteLLM
        response = completion(
            model="gemini/gemini-1.5-flash",
            api_key=gemini_api_key,
            messages=history
        )

        # Extract response
        response_content = response.choices[0].message.content.strip()

        # Send translated response
        loading_msg.content = response_content
        await loading_msg.update()

        # Append assistant reply
        history.append({"role": "assistant", "content": response_content})
        cl.user_session.set("chat_history", history)

    except Exception as e:
        loading_msg.content = f"❌ Error: {str(e)}"
        await loading_msg.update()

# On chat end: save history
@cl.on_chat_end
async def on_chat_end():
    history = cl.user_session.get("chat_history") or []
    try:
        with open("Translation_chat_history.json", "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        print("✅ Chat history saved to 'Translation_chat_history.json'")
    except Exception as e:
        print(f"❌ Failed to save chat history: {str(e)}")
