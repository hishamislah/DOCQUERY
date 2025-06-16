import pandas as pd
import pdfplumber
import io
from .document_loader import load_document
from .parser import detect_document_type
from chatbot.query_engine import query_data, query_pdf_text



def process_file(file):
    filename = file.name.lower()
    
    if filename.endswith(".csv"):
        df = pd.read_csv(file)
        doc_type = detect_document_type(df)
        return doc_type, df

    elif filename.endswith(".xlsx"):
        df = pd.read_excel(file)
        doc_type = detect_document_type(df)
        return doc_type, df

    elif filename.endswith(".pdf"):
        # Extract all text from PDF
        with pdfplumber.open(file) as pdf:
            all_text = ""
            for page in pdf.pages:
                all_text += page.extract_text() + "\n"

        return "pdf_text", all_text  # Will return plain text instead of DataFrame

    else:
        return "unknown", None

def handle_query(question, content):
    # LLM/model failure handler
    try:
        if isinstance(content, pd.DataFrame):
            if content.empty:
                return "This document is empty. Please upload a valid file."
            return query_data(question, content)
        elif isinstance(content, str):
            if not content.strip():
                return "This document is empty. Please upload a valid file."
            return query_pdf_text(question, content)
        else:
            return "Unsupported document format."
    except Exception as e:
        return f"Sorry, there was an error processing your question: {e}"

def handle_uploaded_file(uploaded_file):
    content = extract_content(uploaded_file)  # pdf/csv/txt parser
    # Empty content fallback
    if (isinstance(content, pd.DataFrame) and content.empty) or (isinstance(content, str) and not content.strip()):
        return "empty", None
    doc_type = classify_doc_type(content)     # attendance or invoice
    return doc_type, content

def route_query(doc_type, content, query):
    if doc_type == "attendance":
        return answer_attendance(content, query)
    elif doc_type == "invoice":
        return answer_invoice(content, query)
    else:
        return default_llm_response(query)

def extract_content(uploaded_file):
    filename = uploaded_file.name.lower()
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

def classify_doc_type(content):
    if isinstance(content, pd.DataFrame):
        from .parser import detect_document_type
        return detect_document_type(content)
    elif isinstance(content, str):
        # crude check for PDF text
        lowered = content.lower()
        if "invoice" in lowered:
            return "invoice"
        elif "attendance" in lowered:
            return "attendance"
        else:
            return "unknown"  # was 'pdf_text', now 'unknown' for manual handling
    else:
        return "unknown"

def answer_attendance(content, query):
    return query_data(query, content)

def answer_invoice(content, query):
    return query_data(query, content)

def default_llm_response(query):
    return f"Sorry, I couldn't find a specific answer. Here is a generic response to: {query}"

# Multi-document conflict handler stub (for future extension)
def handle_conflicting_answers(answers):
    # If multiple docs give conflicting answers, show all and let user choose
    if len(set(answers)) > 1:
        return "Multiple documents provide different answers:\n" + "\n---\n".join(answers)
    return answers[0] if answers else "No answer found."
