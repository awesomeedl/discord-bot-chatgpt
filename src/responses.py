from revChatGPT.V3 import Chatbot
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("APPSETTING_OPENAI_API_KEY")
ENGINE = os.getenv("OPENAI_ENGINE") or os.getenv("APPSETTING_OPENAI_API_KEY")

official_chatbot = Chatbot(api_key=OPENAI_API_KEY, engine=ENGINE)


async def official_handle_response(message) -> str:
    return official_chatbot.ask(message)
