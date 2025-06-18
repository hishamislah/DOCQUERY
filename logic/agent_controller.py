# agent_controller.py
# Core backend logic for file processing, document classification, query routing, and error handling in DocQuery Agent.
# Handles integration with document loaders, parsers, and chatbot engines. Logs all major system events and errors.

from .document_loader import load_document
from .parser import detect_document_type
from chatbot.query_engine import query_data, query_pdf_text
from logic.logging_config import get_logger
import pandas as pd
import pdfplumber
import io

upload_logger = get_logger('upload_logger', 'upload')
classification_logger = get_logger('classification_logger', 'classification')
error_logger = get_logger('error_logger', 'errors')
user_actions_logger = get_logger('user_actions_logger', 'user_actions')


def process_file(file):
    filename = file.name.lower()
    upload_logger.info(f"Processing file: {filename}")
    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(file)
            doc_type = detect_document_type(df)
            classification_logger.info(f"Detected document type: {doc_type} for file: {filename}")
            return doc_type, df
        elif filename.endswith(".xlsx"):
            df = pd.read_excel(file)
            doc_type = detect_document_type(df)
            classification_logger.info(f"Detected document type: {doc_type} for file: {filename}")
            return doc_type, df
        elif filename.endswith(".pdf"):
            with pdfplumber.open(file) as pdf:
                all_text = ""
                for page in pdf.pages:
                    all_text += page.extract_text() + "\n"
            upload_logger.info(f"Extracted text from PDF file: {filename}")
            return "pdf_text", all_text
        else:
            error_logger.warning(f"Unknown file type for file: {filename}")
            return "unknown", None
    except Exception as e:
        error_logger.error(f"Error processing file {filename}: {e}")
        return "error", None

def handle_query(question, content, model=None):
    user_actions_logger.info(f"Handling query: '{question}'")
    try:
        if isinstance(content, pd.DataFrame):
            if content.empty:
                error_logger.warning("Query on empty DataFrame.")
                return "This document is empty. Please upload a valid file."
            return query_data(question, content, model=model)
        elif isinstance(content, str):
            if not content.strip():
                error_logger.warning("Query on empty text content.")
                return "This document is empty. Please upload a valid file."
            return query_pdf_text(question, content, model=model)
        else:
            error_logger.error("Unsupported document format for query.")
            return "Unsupported document format."
    except Exception as e:
        error_logger.error(f"Error processing query: {e}")
        return f"Sorry, there was an error processing your question: {e}"

def handle_uploaded_file(uploaded_file):
    upload_logger.info(f"Handling uploaded file: {uploaded_file.name}")
    content = extract_content(uploaded_file)
    if (isinstance(content, pd.DataFrame) and content.empty) or (isinstance(content, str) and not content.strip()):
        error_logger.warning(f"Uploaded file {uploaded_file.name} is empty.")
        return "empty", None
    doc_type = classify_doc_type(content)
    classification_logger.info(f"Classified uploaded file {uploaded_file.name} as type: {doc_type}")
    return doc_type, content

def route_query(doc_type, content, query):
    user_actions_logger.info(f"Routing query for doc_type: {doc_type}")
    if doc_type == "attendance":
        return answer_attendance(content, query)
    elif doc_type == "invoice":
        return answer_invoice(content, query)
    else:
        return default_llm_response(query)

def extract_content(uploaded_file):
    filename = uploaded_file.name.lower()
    try:
        if filename.endswith(".csv"):
            return pd.read_csv(uploaded_file)
        elif filename.endswith(".xlsx"):
            return pd.read_excel(uploaded_file)
        elif filename.endswith(".pdf"):
            with pdfplumber.open(uploaded_file) as pdf:
                all_text = ""
                for page in pdf.pages:
                    all_text += page.extract_text() + "\n"
            return all_text
        else:
            return None
    except Exception as e:
        error_logger.error(f"Error extracting content from {filename}: {e}")
        return None

def classify_doc_type(content):
    if isinstance(content, pd.DataFrame):
        from .parser import detect_document_type
        return detect_document_type(content)
    elif isinstance(content, str):
        lowered = content.lower()
        if "invoice" in lowered:
            return "invoice"
        elif "attendance" in lowered:
            return "attendance"
        else:
            return "unknown"
    else:
        return "unknown"

def answer_attendance(content, query):
    return query_data(query, content)

def answer_invoice(content, query):
    return query_data(query, content)

def default_llm_response(query):
    return f"Sorry, I couldn't find a specific answer. Here is a generic response to: {query}"

def handle_conflicting_answers(answers):
    if len(set(answers)) > 1:
        return "Multiple documents provide different answers:\n" + "\n---\n".join(answers)
    return answers[0] if answers else "No answer found."
