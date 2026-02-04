print("✅ message_handler.py loaded from:", __file__)

import datetime
import random
import re
import webbrowser

from services.state_service import memory, knowledge_mode
from services.speech_service import speak_async
from services.ai_service import get_huggingface_response
from services.wiki_service import get_wikipedia_answer
from services.news_weather_service import get_news, get_weather
from services.utility_service import translate, play_music


def handle_message(user_message, speechtx):
    msg = user_message.lower().strip()
    response_message = ""

    # -------------------------------------------------
    # 1️⃣ FIXED IDENTITY / GREETINGS (RESTORED)
    # -------------------------------------------------
    if msg in ["hi", "hii", "hello", "hey"]:
        response_message = "Hello! How can I help you today?"

    elif msg in ["what is your name", "your name", "who are you"]:
        response_message = "My name is ZAX. I'm your AI assistant."

    # -------------------------------------------------
    # 2️⃣ MEMORY HANDLING (UNCHANGED)
    # -------------------------------------------------
    elif "my name is" in msg:
        name = user_message.split("is")[-1].strip().replace(".", "")
        memory["name"] = name
        response_message = f"Nice to meet you, {name}!"

    # -------------------------------------------------
    # 3️⃣ KNOWLEDGE / FACTUAL QUESTIONS (RESTORED)
    # -------------------------------------------------
    elif msg.startswith(("who is", "what is", "when is", "where is")):
        response_message = get_wikipedia_answer(user_message)

    # -------------------------------------------------
    # 4️⃣ UTILITIES (UNCHANGED)
    # -------------------------------------------------
    elif "joke" in msg:
        from services.utility_service import pyjokes
        response_message = pyjokes.get_joke()

    elif "time" in msg:
        response_message = f"The current time is {datetime.datetime.now().strftime('%H:%M:%p')}"

    elif "news" in msg:
        response_message = get_news()

    elif "weather" in msg:
        match = re.search(r"weather in ([a-zA-Z\s]+)", msg)
        response_message = get_weather(match.group(1)) if match else "Please tell the city."

    elif "translate" in msg:
        match = re.search(r"translate (.+) to ([a-zA-Z]+)", msg)
        if match:
            text, lang = match.groups()
            response_message = translate(text, lang)
        else:
            response_message = "Say: Translate hello to Hindi"

    elif "youtube" in msg:
        webbrowser.open("https://www.youtube.com")
        response_message = "Opening YouTube."

    # -------------------------------------------------
    # 5️⃣ AI FALLBACK (LAST — AS IT SHOULD BE)
    # -------------------------------------------------
    else:
        response_message = (
            get_wikipedia_answer(user_message)
            if knowledge_mode
            else get_huggingface_response(user_message)
        )

    speak_async(response_message)
    return response_message
