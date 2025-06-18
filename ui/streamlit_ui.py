import streamlit as st
import pandas as pd

from logic.agent_controller import process_file, handle_query, handle_uploaded_file, route_query
from logic.langchain_pipeline import load_document, detect_document_type, create_vectorstore, build_qa_chain
from ui.system_info import system_info_tab
from chatbot.ollama_interface import get_available_models_with_fallback

session_key_data = "parsed_data"
session_key_chat = "chat_history"


def run_app():
    st.title("📄 DocQuery AI Agent")
    tab1, tab2 = st.tabs(["Upload Documents", "System Info"])
    with tab1:
        # Model selection with fallback and user option
        available_models = get_available_models_with_fallback()
        if 'selected_model' not in st.session_state:
            st.session_state['selected_model'] = available_models[0] if available_models else None
        selected_model = st.selectbox(
            'Select model to use (auto rollback if fails):',
            available_models,
            index=available_models.index(st.session_state['selected_model']) if st.session_state['selected_model'] in available_models else 0,
            key='selected_model_box'
        )
        st.session_state['selected_model'] = selected_model

        uploaded_files = st.file_uploader("Upload documents", type=["pdf", "csv", "txt"], accept_multiple_files=True)

        doc_infos = []  # List of (doc_type, content, filename)
        if uploaded_files:
            for uploaded_file in uploaded_files:
                try:
                    doc_type, content = handle_uploaded_file(uploaded_file)
                except Exception as e:
                    st.error(f"Error parsing {uploaded_file.name}: {e}")
                    doc_type, content = "unsupported", None
                # Empty content handler
                if (isinstance(content, pd.DataFrame) and content.empty) or (isinstance(content, str) and not content.strip()):
                    st.warning(f"{uploaded_file.name} was parsed but contains no usable content.")
                    doc_type = "empty"
                    content = None
                doc_infos.append({
                    "doc_type": doc_type,
                    "content": content,
                    "filename": uploaded_file.name
                })
            st.session_state[session_key_data] = doc_infos

            st.success(f"{len(doc_infos)} document(s) uploaded.")
            for info in doc_infos:
                st.markdown(f"**{info['filename']}** detected as: `{info['doc_type']}`")
                if info["doc_type"] == "unsupported":
                    st.error(f"{info['filename']} is an unsupported file type. Supported: PDF, CSV, TXT.")
                elif info["doc_type"] == "empty":
                    st.warning(f"{info['filename']} is empty and will be skipped.")
                elif info["content"] is None:
                    st.warning(f"Could not parse {info['filename']}. Please review or process this file manually.")
                    st.download_button(
                        label=f"Download {info['filename']}",
                        data=next((f for f in uploaded_files if f.name == info['filename']), None),
                        file_name=info['filename']
                    )
                elif info["doc_type"] == "unknown":
                    st.warning(f"{info['filename']} was not automatically detected. Please assign a type manually.")
                    manual_type_key = f"manual_type_{info['filename']}"
                    assigned_type_key = f"assigned_type_{info['filename']}"
                    custom_type_key = f"custom_type_{info['filename']}"
                    custom_type_value_key = f"custom_type_value_{info['filename']}"
                    # If already assigned, show the selected type and disable further changes
                    if assigned_type_key in st.session_state:
                        assigned = st.session_state[assigned_type_key]
                        if assigned == "other" and custom_type_value_key in st.session_state:
                            st.success(f"Type for {info['filename']} set to: {st.session_state[custom_type_value_key]} (custom)")
                        else:
                            st.success(f"Type for {info['filename']} set to {assigned}.")
                    else:
                        manual_type = st.radio(
                            f"Select document type for {info['filename']}",
                            ["attendance", "invoice", "other"],
                            key=manual_type_key,
                            horizontal=True
                        )
                        custom_type = ""
                        if manual_type == "other":
                            custom_type = st.text_input(f"Enter custom type for {info['filename']}", key=custom_type_key)
                        if st.button(f"Assign type to {info['filename']}", key=f"assign_{info['filename']}"):
                            for doc in st.session_state[session_key_data]:
                                if doc['filename'] == info['filename']:
                                    if manual_type == "other" and custom_type:
                                        doc['doc_type'] = custom_type
                                        st.session_state[custom_type_value_key] = custom_type
                                    else:
                                        doc['doc_type'] = manual_type
                            st.session_state[assigned_type_key] = manual_type
                            st.success(f"Type for {info['filename']} set to {custom_type if manual_type == 'other' and custom_type else manual_type}.")
                            st.rerun()
                elif isinstance(info["content"], pd.DataFrame):
                    with st.expander(f"🔍 Preview Table: {info['filename']}"):
                        st.dataframe(info["content"], use_container_width=True)
                elif isinstance(info["content"], str):
                    with st.expander(f"📄 Preview Text: {info['filename']}"):
                        st.text_area("Preview", value=info["content"][:1000], height=200)
                else:
                    st.info(f"No preview available for {info['filename']}.")

        # Chat Interface
        st.divider()
        st.subheader("💬 Ask Questions")

        if session_key_chat not in st.session_state:
            st.session_state[session_key_chat] = []

        # User input and clear chat button
        col1, col2 = st.columns([4, 1])
        with col1:
            user_input = st.chat_input("Type your question about the uploaded documents...")
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
            if session_key_data not in st.session_state or not st.session_state[session_key_data]:
                st.warning("⚠️ Please upload and process at least one document first.")
            else:
                st.session_state[session_key_chat].append({"role": "user", "content": user_input})
                with st.chat_message("user"):
                    st.markdown(user_input)

                # Combine all document contents (tables and text) for the chatbot
                all_contents = st.session_state[session_key_data]
                combined_context = []
                from tabulate import tabulate
                for info in all_contents:
                    if info["doc_type"] in ["empty", "unsupported"]:
                        continue
                    if isinstance(info["content"], pd.DataFrame):
                        table_md = tabulate(info["content"], headers="keys", tablefmt="pipe", showindex=False)
                        combined_context.append(f"\n--- {info['filename']} (table) ---\n{table_md}")
                    elif isinstance(info["content"], str):
                        combined_context.append(f"\n--- {info['filename']} ---\n{info['content']}")
                # Join all document contexts for the LLM
                context_for_llm = "\n".join(combined_context)
                if context_for_llm.strip():
                    try:
                        response = handle_query(user_input, context_for_llm, model=st.session_state['selected_model'])
                    except Exception as e:
                        response = f"Sorry, there was an error processing your question: {e}"
                    # Ambiguous query handler
                    if (isinstance(response, str) and ("couldn't find" in response or "generic response" in response)) or not response.strip():
                        response += "\n\nIf this answer is not helpful, please clarify your question or specify which document you are referring to."
                else:
                    response = "No valid document content to answer from."
                with st.chat_message("assistant"):
                    st.markdown(response)
                    st.session_state[session_key_chat].append({"role": "assistant", "content": response})
    with tab2:
        system_info_tab()
