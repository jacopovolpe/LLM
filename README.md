# RAG-based AI Assistant with Flask and Mistral-7B

This project implements a Retrieval-Augmented Generation (RAG) based AI assistant using Flask as the web framework and Mistral-7B as the language model. The assistant is capable of answering user questions by retrieving relevant information from a pre-processed knowledge base and generating natural language responses.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Project Structure](#project-structure)
6. [Dependencies](#dependencies)
7. [API Endpoints](#api-endpoints)
8. [FAISS Vector Store](#faiss-vector-store)
9. [Preprocessing](#preprocessing)
10. [Contributing](#contributing)
11. [License](#license)

## Project Overview

The project consists of a Flask-based web application that serves as an AI assistant. The assistant uses a RAG approach to answer user questions by retrieving relevant information from a FAISS vector store and generating responses using the Mistral-7B language model. The project also includes a preprocessing step where text data is extracted from PDFs, processed, and indexed into a FAISS vector store for efficient retrieval.

## Features

- **Retrieval-Augmented Generation (RAG):** Combines retrieval of relevant documents with generative language models to provide accurate and context-aware responses.
- **FAISS Vector Store:** Efficiently stores and retrieves document embeddings for quick similarity search.
- **Mistral-7B Language Model:** Generates natural language responses based on retrieved context.
- **Flask Web Framework:** Provides a simple and scalable web interface for interacting with the AI assistant.
- **Preprocessing Pipeline:** Extracts text from PDFs, processes it, and indexes it into the FAISS vector store.

## Installation

To set up the project, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/rag-ai-assistant.git
   cd rag-ai-assistant
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory and add your Hugging Face API token:
   ```bash
   HUGGING_FACE_TOKEN=your_hugging_face_token_here
   ```

## Usage

1. **Run the Flask application:**
   ```bash
   python app.py
   ```

2. **Access the web interface:**
   Open your browser and navigate to `http://localhost:5000` to interact with the AI assistant.

3. **Ask questions:**
   Use the web interface to ask questions, and the assistant will generate responses based on the retrieved context.

## Project Structure

```
rag-ai-assistant/
│
├── app.py                  # Flask application and API endpoints
├── Assistant.py            # Assistant class with RAG logic
├── Preparation.ipynb       # Jupyter notebook for preprocessing and FAISS setup
├── requirements.txt        # List of dependencies
├── data/                   # Directory for storing data files
│   ├── book.pdf            # Example PDF file for text extraction
│   ├── book.txt            # Extracted text from PDF
│   ├── faiss_index/        # Directory for FAISS index files
│   └── slides/             # Directory for slide PDFs
├── templates/              # HTML templates for the web interface
│   └── index.html          # Main HTML template
└── README.md               # Project documentation
```

## Dependencies

The project requires the following Python packages:

- Flask
- requests
- langchain
- huggingface_hub
- sentence-transformers
- pypdf
- numpy
- tensorflow

You can install all dependencies using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## API Endpoints

- **GET `/`**: Serves the main HTML page.
- **POST `/ask`**: Accepts a user question and returns a generated response.
- **GET `/get_history`**: Returns the conversation history.
- **GET `/reset`**: Clears the conversation history.

## FAISS Vector Store

The project uses FAISS (Facebook AI Similarity Search) to store and retrieve document embeddings. The FAISS index is created from preprocessed text data and allows for efficient similarity search.

### Creating the FAISS Index

1. Extract text from PDFs using `Preparation.ipynb`.
2. Split the text into chunks using `RecursiveCharacterTextSplitter`.
3. Generate embeddings using `HuggingFaceEmbeddings`.
4. Create and save the FAISS index.

## Preprocessing

The preprocessing pipeline involves:

1. **Text Extraction:** Extract text from PDFs using `PyPDF2`.
2. **Text Splitting:** Split the text into manageable chunks.
3. **Embedding Generation:** Generate embeddings for each text chunk using `sentence-transformers/all-MiniLM-L6-v2`.
4. **FAISS Indexing:** Index the embeddings into a FAISS vector store for efficient retrieval.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.