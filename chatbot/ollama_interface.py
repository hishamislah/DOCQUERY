# ollama_interface.py
import requests

def query_ollama(prompt: str) -> str:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3", "prompt": prompt}
    )
    return response.json()['response']
# chatbot/ollama_interface.py

from ollama import chat

def ollama_generate(prompt: str) -> str:
    response = chat(model="llama3", messages=[{"role": "user", "content": prompt}])
    return response['message']['content']
