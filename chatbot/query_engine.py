import ollama
import pandas as pd
import io
from .ollama_interface import ollama_generate


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    return df.to_markdown(index=False)

def query_data(question, df):
    df_context = dataframe_to_markdown(df)
    prompt = f"""
You are an intelligent assistant. Below is a document in table format:

{df_context}

Now answer the question: {question}
"""
    try:
        response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
        return response['message']['content']
    except Exception as e:
        return f"Error from Ollama: {str(e)}"
def query_pdf_text(question, extracted_text):
    prompt = f"""
You are a helpful assistant. Here's the content from a PDF document:

{extracted_text}

Answer the question as clearly as possible based on this content.

Question: {question}
"""
    return ollama_generate(prompt)
from .ollama_interface import ollama_generate

def query_pdf_text(question, extracted_text):
    prompt = f"""
You are a helpful assistant. Here is some content extracted from a PDF document:

{extracted_text}

Answer the following question clearly based on the document:

Question: {question}
"""
    return ollama_generate(prompt)
