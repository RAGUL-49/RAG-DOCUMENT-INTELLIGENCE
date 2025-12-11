import streamlit as st
from pathlib import Path
import sys

# Add project root to the Python path to resolve module imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ingestion.ingest_pipeline import IngestionPipeline
from src.embedding.vector_store import VectorStore
from src.retrieval.retriever import Retriever
from src.retrieval.reranker import Reranker
from src.retrieval.multimodal_merger import MultiModalMerger
from src.generation.perplexity_llm import PerplexityLLM
from src.generation.prompt_template import PromptTemplate
from src.generation.answer_formatter import AnswerFormatter
from src.utils.config import config

st.set_page_config(page_title="MultiDoc-IntelliAgent", layout="wide")

st.title("🤖 MultiDoc-IntelliAgent")
st.markdown("*Advanced Multi-Modal Document Intelligence System*")

# Initialize components
@st.cache_resource
def init_components():
    return {
        'pipeline': IngestionPipeline(),
        'vector_store': VectorStore(),
        'retriever': Retriever(),
        'reranker': Reranker(),
        'merger': MultiModalMerger(),
        'llm': PerplexityLLM(),
        'formatter': AnswerFormatter()
    }

components = init_components()

# Initialize session state for chat history and document processing status
if 'messages' not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant", 
        "content": "Hello! Please upload a PDF document, and I'll help you answer questions about it."
    }]
if 'doc_processed' not in st.session_state:
    st.session_state.doc_processed = False

# Sidebar
with st.sidebar:
    st.header("📁 Document Upload")
    uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])
    
    if uploaded_file and st.button("Process Document"):
        with st.spinner("Processing..."):
            # Save uploaded file
            save_path = Path("data/raw_documents") / uploaded_file.name
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            # Process
            chunks = components['pipeline'].process_document(str(save_path))

            # Store in vector database
            components['vector_store'].add_chunks(chunks)

            st.success(f"✅ Document processed! Generated {len(chunks)} chunks.")
            st.session_state.doc_processed = True
            # Reset chat for new document
            st.session_state.messages = [{
                "role": "assistant",
                "content": f"I've processed '{uploaded_file.name}'. What would you like to know?"
            }]
            st.rerun()

# Main content area
st.header("🔍 Ask Questions")

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if query := st.chat_input("What is your question?", disabled=not st.session_state.doc_processed):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Thinking..."):
            try:
                # Retrieve relevant chunks
                retrieved_chunks = components['retriever'].retrieve(query)

                # Rerank if we have results
                if retrieved_chunks:
                    retrieved_chunks = components['reranker'].rerank(query, retrieved_chunks)

                # Create context from retrieved chunks
                context = components['merger'].create_context(retrieved_chunks)

                # Generate answer
                prompt = PromptTemplate.create_query_prompt(context, query)
                raw_response = components['llm'].generate(prompt, PromptTemplate.SYSTEM_PROMPT)

                # Format response
                parsed_response = components['formatter'].parse_response(raw_response)
                
                confidence_color = {
                    "High": "🟢",
                    "Medium": "🟡",
                    "Low": "🔴"
                }.get(parsed_response.get('confidence', 'Unknown'), "⚪")

                # Construct the full response with citations and confidence
                full_response = (
                    f"{parsed_response.get('answer', 'No answer found.')}\n\n"
                    f"**Confidence:** {confidence_color} {parsed_response.get('confidence', 'Unknown')}\n\n"
                    f"**Citations:** {parsed_response.get('citations', 'None')}"
                )
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                error_message = f"An error occurred: {e}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})

# Footer
st.markdown("---")
st.markdown("*Built with Rag-ul*")