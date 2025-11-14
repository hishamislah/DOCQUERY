# langchain_pipeline.py
# Integrates LangChain and HuggingFace models for document loading, type detection, vectorstore creation, and QA chain building.
# Supports advanced AI/ML features for DocQuery Agent.

import os
from langchain_community.document_loaders import PyMuPDFLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

def load_document(file):
    filename = file.name.lower()
    
    if filename.endswith('.csv'):
        file_path = f"temp_upload.csv"
        with open(file_path, "wb") as f:
            f.write(file.read())
        loader = CSVLoader(file_path=file_path, encoding="utf-8")
    elif filename.endswith('.pdf'):
        file_path = f"temp_upload.pdf"
        with open(file_path, "wb") as f:
            f.write(file.read())
        loader = PyMuPDFLoader(file_path)
    else:
        return None, "Unsupported file format"

    docs = loader.load()
    return docs, "success"

def detect_document_type(docs):
    content = " ".join([doc.page_content.lower() for doc in docs])
    if "present" in content or "absent" in content:
        return "attendance"
    elif "invoice" in content or "total" in content or "price" in content:
        return "invoice"
    return "unknown"

def create_vectorstore(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return vectorstore

def get_llm_pipeline():
    model_id = "tiiuae/falcon-7b-instruct"  # Or use your local downloaded one
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id)
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=256)
    return HuggingFacePipeline(pipeline=pipe)

def build_qa_chain(vectorstore):
    """Return a simple QA callable using retriever + HuggingFacePipeline.

    LangChain v1 favors Runnable composition; we manually format prompt and invoke the LLM.
    """
    llm = get_llm_pipeline()
    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template=(
            "Use the following context to answer the question as accurately as possible.\n"
            "If the answer is not in the context, say you don't have enough information.\n\n"
            "Context:\n{context}\n\nQuestion: {question}\nAnswer:"
        ),
    )
    retriever = vectorstore.as_retriever()

    def query_func(question: str) -> str:
        docs = retriever.get_relevant_documents(question)
        # Merge up to first 3 documents for context
        merged_context = "\n\n".join(d.page_content for d in docs[:3])
        formatted_prompt = prompt_template.format(context=merged_context, question=question)
        # HuggingFacePipeline supports __call__ returning text
        try:
            result = llm(formatted_prompt)
            # Some pipelines may return dict; normalize
            if isinstance(result, dict):
                return result.get("generated_text", str(result))
            return result
        except Exception as e:
            return f"Model execution error: {e}"

    return query_func
