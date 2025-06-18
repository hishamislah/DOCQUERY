# query_engine.py
# Provides functions to query data tables and PDF text using LLMs via Ollama, with fallback and error handling.
# Used by backend logic to answer user questions based on document content.

import ollama
import pandas as pd
import io
from .ollama_interface import ollama_generate_with_fallback


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    return df.to_markdown(index=False)

def query_data(question, df, model=None):
    df_context = dataframe_to_markdown(df)
    prompt = f"""
You are an intelligent assistant. Below is a document in table format:

{df_context}

Now answer the question: {question}
"""
    return ollama_generate_with_fallback(prompt, model=model)
def query_pdf_text(question, extracted_text, model=None):
    prompt = f"""
You are a helpful assistant. Here is some content extracted from a PDF document:

{extracted_text}

Answer the following question clearly based on the document:

Question: {question}
"""
    return ollama_generate_with_fallback(prompt, model=model)
