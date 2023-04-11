import os
import langchain
from langchain.llms import OpenAI, Cohere, HuggingFaceHub
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"

def botresp(text ):
    flan = HuggingFaceHub(repo_id="google/flan-t5-xl")
    print(flan(text))
    return flan(text)














