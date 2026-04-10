from dotenv import load_dotenv
import os
import logging
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VECTOR_DB_PATH = os.path.join(BASE_DIR, 'data', 'vector_store')

class RAGEngine:
    def __init__(self):
        # We use Google Embeddings for consistency
        api_key = os.getenv("GOOGLE_API_KEY", "").strip()
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
            
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            api_key=api_key if api_key else None,
            google_api_key=api_key if api_key else None
        )
        self.vector_store = None
        
        # Load existing vector store if it exists
        if os.path.exists(VECTOR_DB_PATH):
            try:
                self.vector_store = FAISS.load_local(VECTOR_DB_PATH, self.embeddings, allow_dangerous_deserialization=True)
                logger.info("Existing Vector Store loaded successfully")
            except Exception as e:
                logger.error(f"Error loading FAISS: {e}")
                
    def process_pdf(self, pdf_path: str) -> bool:
        """Reads a PDF, splits it, creates embeddings, and saves them to FAISS."""
        try:
            logger.info(f"Processing document: {pdf_path}")
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            
            # Split into chunks so the IA can search for relevance and fit in context
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.split_documents(documents)
            
            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(splits, self.embeddings)
            else:
                self.vector_store.add_documents(splits)
                
            # Persist
            self.vector_store.save_local(VECTOR_DB_PATH)
            return True
        except Exception as e:
            logger.error(f"Error processing PDF document: {e}")
            return False
            
    def similarity_search(self, query: str, k: int = 3) -> str:
        """Searches for relevant information in the documentation (e.g., investment criteria)."""
        if self.vector_store is None:
            return "No previous knowledge base document has been configured."
            
        docs = self.vector_store.similarity_search(query, k=k)
        text_context = "\n\n".join([d.page_content for d in docs])
        return text_context
