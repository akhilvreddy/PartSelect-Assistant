import os
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")