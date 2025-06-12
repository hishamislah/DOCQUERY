import streamlit as st
import pandas as pd

from logic.agent_controller import process_file, handle_query, handle_uploaded_file, route_query
from logic.langchain_pipeline import load_document, detect_document_type, create_vectorstore, build_qa_chain


session_key_data = "parsed_data"
session_key_chat = "chat_history"


def run_app():
    st.title("📄 DocQuery AI Agent")
    uploaded_file = st.file_uploader("Upload a document", type=["pdf", "csv", "txt"])

    doc_type, content = None, None
    if uploaded_file:
        doc_type, content = handle_uploaded_file(uploaded_file)
        st.success(f"Document detected as: {doc_type}")
        if isinstance(content, pd.DataFrame):
            with st.expander("🔍 Preview Table"):
                st.dataframe(content, use_container_width=True)
        elif isinstance(content, str):
            st.text_area("📄 Preview Document", value=content[:1000], height=200)
        else:
            st.info("No preview available for this file type.")

        st.session_state[session_key_data] = content

    # Chat Interface
    st.divider()
    st.subheader("💬 Ask Questions")

    if session_key_chat not in st.session_state:
        st.session_state[session_key_chat] = []

    # User input and clear chat button
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.chat_input("Type your question about the document...")
    with col2:
        clear_clicked = st.button("🧹 Clear Chat", use_container_width=True)
        if clear_clicked:
            st.session_state[session_key_chat] = []
            st.success("Chat cleared!")
            st.rerun()

    # Display chat history (after clear logic)
    for i, chat in enumerate(st.session_state[session_key_chat]):
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])

    if user_input:
        if session_key_data not in st.session_state:
            st.warning("⚠️ Please upload and process a document first.")
        else:
            # Add user question to chat
            st.session_state[session_key_chat].append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # Get answer from Ollama-backed agent
            with st.chat_message("assistant"):
                response = handle_query(user_input, st.session_state[session_key_data])
                st.markdown(response)
                st.session_state[session_key_chat].append({"role": "assistant", "content": response})
