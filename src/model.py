import os
import time
from langchain_openai import ChatOpenAI
from typing import Any, Dict




from dotenv import load_dotenv


load_dotenv()



model = ChatOpenAI(model="gpt-3.5-turbo", temperature=1.2, api_key=os.getenv("OPENAI_API_KEY"), max_completion_tokens=30)
result = model.invoke("write a poem for me?")
print(result.content)