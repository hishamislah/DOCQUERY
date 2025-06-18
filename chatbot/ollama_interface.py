# ollama_interface.py
# Provides functions and classes to interact with Ollama LLM models, including model selection, fallback, and text generation.
# Used by the backend and UI to generate answers from AI models and handle model failures gracefully.

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

class OllamaModelManager:
    def __init__(self, ollama_url="http://localhost:11434", fallback_models=None, logger=None):
        self.ollama_url = ollama_url
        self.fallback_models = fallback_models or ["llama3", "falcon-7b-instruct", "mistral"]
        self.logger = logger or self._get_default_logger()

    def _get_default_logger(self):
        import logging
        logger = logging.getLogger("OllamaModelManager")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def get_available_models_with_fallback(self):
        """Get available models with fallback options"""
        try:
            # Try to get models from Ollama
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = [model["name"] for model in data.get("models", [])]
                if models:
                    return models
            # Fallback to predefined models
            self.logger.warning("Using fallback model list")
            return self.fallback_models
        except Exception as e:
            self.logger.error(f"Error getting models: {e}")
            return self.fallback_models

def get_available_models_with_fallback():
    """Get available models with fallback options (standalone function)"""
    ollama_url = "http://localhost:11434"
    fallback_models = ["llama3", "falcon-7b-instruct", "mistral"]
    import logging
    logger = logging.getLogger("OllamaModelManager")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=10)
        if response.status_code == 200:
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            if models:
                return models
        logger.warning("Using fallback model list")
        return fallback_models
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        return fallback_models

def ollama_generate_with_fallback(prompt: str, model: str = None) -> str:
    """
    Try to generate a response using the selected Ollama model. If it fails, fallback to the first available fallback model.
    """
    from ollama import chat
    fallback_models = ["llama3", "falcon-7b-instruct", "mistral"]
    models_to_try = [model] if model else []
    models_to_try += [m for m in fallback_models if m != model]
    last_error = None
    for m in models_to_try:
        try:
            response = chat(model=m, messages=[{"role": "user", "content": prompt}])
            return response['message']['content']
        except Exception as e:
            last_error = e
            continue
    return f"[Fallback failed] Error from Ollama: {str(last_error)}"
