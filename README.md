# Recruiter Chatbot

A RAG-based chatbot designed to help recruiters learn about my professional experience through interactive conversations.

## Features

- 🤖 Interactive chatbot interface built with Streamlit
- 📚 RAG (Retrieval-Augmented Generation) system for accurate responses
- 🔍 Vector similarity search using ChromaDB
- 📄 Document processing for career stories and experiences
- 🤗 HuggingFace integration for LLM and embeddings

## Project Structure

```
recruiter-chatbot/
├── src/                    # Source code
│   ├── main.py            # Main application entry point
│   ├── rag_system.py      # RAG system implementation
│   ├── vector_store.py    # ChromaDB vector store
│   ├── document_processor.py  # Document loading and chunking
│   ├── llm_interface.py   # HuggingFace LLM interface
│   └── streamlit_app.py   # Streamlit web app
├── data/
│   ├── documents/         # Career stories and documents
│   └── processed/         # Processed data
├── configs/
│   └── config.yaml        # Configuration file
├── tests/                 # Unit tests
├── docs/                  # Documentation
└── environment.yml        # Conda environment
```

## Setup

1. Clone the repository
2. Create conda environment: `conda env create -f environment.yml`
3. Activate environment: `conda activate recruiter-chatbot-env`
4. Add your career stories to `data/documents/career_stories/`
5. Run the app: `streamlit run src/streamlit_app.py`

## Deployment

This app is designed to be deployed on Streamlit Community Cloud for free hosting.

## TODO

- [ ] Implement RAG system logic
- [ ] Set up ChromaDB vector store
- [ ] Integrate HuggingFace models
- [ ] Add comprehensive error handling
- [ ] Write unit tests
- [ ] Add more career stories
- [ ] Optimize for deployment
