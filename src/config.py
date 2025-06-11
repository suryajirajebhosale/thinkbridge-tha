# -----------------------------------------------------
# Author: Surya Bhosale
# Date: 2025-06-11
# Project: ThinkBridge Assignment
# -----------------------------------------------------
import os
from langchain_openai import ChatOpenAI

class Config:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    SERP_API_KEY = os.environ.get("SERP_API_KEY")
    MODEL_NAME = os.environ.get("MODEL_NAME")
    LLM = ChatOpenAI(
        model=MODEL_NAME,
        api_key=OPENAI_API_KEY,
        temperature=0.3
    )