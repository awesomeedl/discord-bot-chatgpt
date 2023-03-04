from revChatGPT.V3 import Chatbot
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_EMAIL = os.getenv("OPENAI_EMAIL")
OPENAI_PASSWORD = os.getenv("OPENAI_PASSWORD")
SESSION_TOKEN = os.getenv("SESSION_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ENGINE = os.getenv("OPENAI_ENGINE")

official_chatbot = Chatbot(api_key=OPENAI_API_KEY, engine=ENGINE)


async def official_handle_response(message) -> str:
    return official_chatbot.ask(message)
