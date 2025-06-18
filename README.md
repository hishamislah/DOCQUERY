# DocQuery Agent

DocQuery Agent is an AI-powered tool for uploading and querying documents such as attendance sheets and invoices. It supports CSV, XLSX, PDF, and TXT files, and allows users to ask natural language questions about the uploaded documents.

## Features
- Upload multiple documents (CSV, XLSX, PDF, TXT)
- Automatic document type detection (attendance, invoice, or custom)
- Preview document content in the UI
- Ask questions about your documents using natural language
- Uses Ollama and HuggingFace models for AI-powered answers
- Fallback system for model selection and error handling
- System event and error logging (with optional email alerts)

## Example Questions
- Who is absent?
- What is the total invoice amount?
- What is the price of item 2?

## Getting Started

### 1. Install Dependencies
```zsh
pip install -r requirements.txt
```

### 2. Run the Application
```zsh
streamlit run app.py
```

### 3. (Optional) Docker Usage
```zsh
docker build -t docquery-agent .
docker run -p 8501:8501 docquery-agent
```

## Configuration
- Edit `logic/logging_config.py` to set up email alerts for system errors.
- Ollama model selection and fallback is handled automatically in the UI.

## Project Structure
- `app.py` — Main entry point
- `ui/streamlit_ui.py` — Streamlit UI logic
- `logic/` — Backend logic and document processing
- `chatbot/` — AI/ML integration and model handling
- `logs/` — System and error logs
- `sample_docs/` — Example documents for testing

## License
MIT