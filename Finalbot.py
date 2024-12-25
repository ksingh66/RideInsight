import os
from dotenv import load_dotenv
from pinecone import Pinecone  # Note: only importing Pinecone class
from sentence_transformers import SentenceTransformer
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

def load_data_from_txt(filename):
    """
    Loads data from a .txt file and converts it into a list of dictionaries.

    Args:
        filename (str): The name of the text file to read from.

    Returns:
        list: A list of dictionaries in the format [{"id": ..., "text": ...}, ...]
    """
    file_path = os.path.join(os.path.dirname(__file__), filename)
    data = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for i, line in enumerate(lines, start=1):
            if line.strip():  # Skip empty lines
                data.append({
                    "id": f"vec{i}",
                    "text": line.strip()
                })
    return data

class RAGChatbot:
    def __init__(self, model_id="llama-3.1-70b-versatile"):
        # Get environment variables
        api_key = os.getenv('API_KEY')
        groq_api_key = os.getenv('GROQ_API_KEY')
        self.index_name = os.getenv('INDEX_NAME')
        
        if not all([api_key, groq_api_key, self.index_name]):
            raise ValueError("Missing required environment variables. Please check your .env file.")
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=api_key)
        
        # Embedding Model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.langchain_embeddings = HuggingFaceEmbeddings(
            model_name='sentence-transformers/all-MiniLM-L6-v2'
        )
        
        # Initialize Groq through LangChain
        self.llm = ChatGroq(
            temperature=0.7,
            max_tokens=500,
            groq_api_key=groq_api_key,
            model_name=model_id
        )
        
        # Pinecone Index Setup
        self.index = self.pc.Index(self.index_name)
        self.namespace = "ns1"
        
        # Initialize LangChain vector store
        os.environ["PINECONE_API_KEY"] = api_key
        
        self.vector_store = LangchainPinecone.from_existing_index(
            index_name=self.index_name,
            embedding=self.langchain_embeddings,
            namespace=self.namespace
        )
        
        # Set up the RAG chain
        self._setup_rag_chain()

    def _setup_rag_chain(self):
        """Initialize the LangChain RAG retrieval chain"""
        prompt_template = """
        Context: {context}
        
        Question: {question}
        
        Based on the above context, provide a comprehensive and helpful answer.
        Only use context that is nessessary and ignore the rest.
        If you cannot provide a good answer just say so.
        Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        self.chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_kwargs={"k": 5} #k = number of most relevent contexts 
            ),
            chain_type_kwargs={"prompt": PROMPT}
        )

    def add_documents(self, data):
        """
        Add documents to the Pinecone index
        
        Args:
            data (list): List of dictionaries with 'id' and 'text' keys
        """
        # Generate embeddings
        embeddings = [
            self.embedding_model.encode(d['text']).tolist() 
            for d in data
        ]
        
        # Create vectors for Pinecone
        vectors = [
            {
                "id": d['id'],
                "values": embedding,
                "metadata": {"text": d['text']}
            }
            for d, embedding in zip(data, embeddings)
        ]
        
        # Upsert to Pinecone using new pattern
        self.index.upsert(vectors=vectors, namespace=self.namespace)
        print(f"Added {len(vectors)} documents to index")

    # ... rest of the methods remain the same ...


    def generate_response(self, query):
        """
        Generate a response using LangChain's RAG chain
        
        Args:
            query (str): User's input query
        
        Returns:
            str: Generated response
        """
        try:
            # Use LangChain's chain for retrieval and response generation
            response = self.chain({"query": query})
            return response["result"]
        except Exception as e:
            print(f"Generation error: {e}")
            return f"An error occurred: {e}"

    def chat(self):
        """
        Interactive chat loop
        """
        print("RAG Chatbot is ready! Type 'exit' to quit.")
        while True:
            user_input = input("You: ")
            
            if user_input.lower() == 'exit':
                break
            
            try:
                response = self.generate_response(user_input)
                print("Chatbot:", response)
            except Exception as e:
                print(f"An error occurred: {e}")

def main():
    try:
        # Initialize Chatbot
        chatbot = RAGChatbot()
        
        # Load data from text file
        sample_data = load_data_from_txt("sample_data.txt")
        
        # Add documents to index
        chatbot.add_documents(sample_data)

        # Start chatting
        chatbot.chat()
    except Exception as e:
        print(f"Error initializing chatbot: {e}")


if __name__ == "__main__":
    main()