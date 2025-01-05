import os
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from langchain_huggingface import HuggingFaceEmbeddings

class HybridChatbot:
    def __init__(self, context_file=None, rag_data_file=None, index_name=None, model_id="llama-3.1-70b-versatile"):
        """
        Initialize the hybrid chatbot that combines RAG and static context capabilities.
        
        Args:
            context_file (str, optional): Path to the file containing static context
            rag_data_file (str, optional): Path to the file containing documents to be added to vector storage
            index_name (str, optional): Name of the Pinecone index to use. If None, uses INDEX_NAME from environment
            model_id (str): The ID of the model to use for chat
        """
        # Load environment variables
        load_dotenv()
        
        # Get environment variables with potential override
        self.api_key = os.getenv('API_KEY')
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.index_name = index_name or os.getenv('INDEX_NAME')
        
        if not all([self.api_key, self.groq_api_key, self.index_name]):
            raise ValueError("Missing required environment variables or parameters. Please check your .env file or provided arguments.")
        
        # Load static context if provided
        self.static_context = self._load_context_file(context_file) if context_file else "No static context provided."
        
        # Initialize components
        self._setup_pinecone()
        self._setup_embedding_models()
        self._setup_llm(model_id)
        self._setup_vector_store()
        
        # Load and add new documents if provided
        if rag_data_file:
            self._load_and_add_documents(rag_data_file)
            
        # Set up the RAG chain after potentially adding new documents
        self._setup_rag_chain()

    def _load_context_file(self, filename):
        """
        Load the static context from a file.
        
        Args:
            filename (str): Path to the context file
            
        Returns:
            str: The content of the context file or an error message
        """
        try:
            if not os.path.exists(filename):
                raise FileNotFoundError(f"Context file '{filename}' not found.")
            
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                print(f"Successfully loaded static context from '{filename}'")
                return content
                
        except Exception as e:
            print(f"Error reading context file: {str(e)}")
            return f"Error loading static context: {str(e)}"

    def _setup_pinecone(self):
        """Initialize Pinecone client and index."""
        try:
            self.pc = Pinecone(api_key=self.api_key)
            self.index = self.pc.Index(self.index_name)
            self.namespace = "ns1"
            
            # Verify the index exists and is accessible
            stats = self.index.describe_index_stats()
            print(f"Successfully connected to Pinecone index '{self.index_name}'")
            print(f"Current vector count: {stats.total_vector_count}")
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Pinecone: {str(e)}")

    def _setup_embedding_models(self):
        """Initialize embedding models for both direct use and LangChain."""
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.langchain_embeddings = HuggingFaceEmbeddings(
            model_name='sentence-transformers/all-MiniLM-L6-v2'
        )

    def _setup_llm(self, model_id):
        """Initialize the language model."""
        self.llm = ChatGroq(
            temperature=0.7,
            max_tokens=500,
            groq_api_key=self.groq_api_key,
            model_name=model_id
        )

    def _setup_vector_store(self):
        """Initialize the LangChain vector store."""
        os.environ["PINECONE_API_KEY"] = self.api_key
        self.vector_store = LangchainPinecone.from_existing_index(
            index_name=self.index_name,
            embedding=self.langchain_embeddings,
            namespace=self.namespace
        )

    def _load_and_add_documents(self, filename):
        """
        Load and add documents from a file to the vector store.
        
        Args:
            filename (str): Path to the file containing documents
        """
        try:
            if not os.path.exists(filename):
                raise FileNotFoundError(f"RAG data file '{filename}' not found.")
                
            # Try to load the documents
            documents = self._load_documents_from_file(filename)
            if documents:
                # Add documents to vector store
                self.add_documents(documents)
                print(f"Successfully processed and added documents from '{filename}'")
            else:
                print(f"No documents were loaded from '{filename}'")
                
        except Exception as e:
            print(f"Error processing RAG data: {str(e)}")
            print("Continuing with existing vector storage.")

    def _load_documents_from_file(self, filename):
        """
        Load documents from a text file.
        
        Args:
            filename (str): Path to the text file to read from
            
        Returns:
            list: A list of dictionaries in the format [{"id": ..., "text": ...}, ...]
        """
        data = []
        
        with open(filename, 'r') as file:
            lines = file.readlines()
            for i, line in enumerate(lines, start=1):
                if line.strip():
                    data.append({
                        "id": f"vec{i}",
                        "text": line.strip()
                    })
        return data

    def _setup_rag_chain(self):
        """Initialize the RAG retrieval chain with a prompt that includes static context."""
        prompt_template = f"""
        Static Context Information:
        {self.static_context}
        
        Retrieved Context:
        {{context}}
        
        Question: {{question}}
        
        Based on both the static context and retrieved information above, provide a comprehensive answer.
        If the question is about data or earnings prioritize using the Static Context.
        If the question cannot be fully answered using the available context, please say so.
        Only use context that is relevant and ignore the rest. 
        Do not mention that you are using Static or Retrieved Context
        Only answer the question and do not say anything else.
        
        Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        self.chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_kwargs={"k": 5}
            ),
            chain_type_kwargs={"prompt": PROMPT}
        )

    def add_documents(self, data):
        """
        Add documents to the Pinecone index for RAG retrieval.
        
        Args:
            data (list): List of dictionaries with 'id' and 'text' keys
        """
        if not data:
            print("No documents to add.")
            return
            
        try:
            embeddings = [
                self.embedding_model.encode(d['text']).tolist() 
                for d in data
            ]
            
            vectors = [
                {
                    "id": d['id'],
                    "values": embedding,
                    "metadata": {"text": d['text']}
                }
                for d, embedding in zip(data, embeddings)
            ]
            
            self.index.upsert(vectors=vectors, namespace=self.namespace)
            print(f"Added {len(vectors)} documents to index")
            
        except Exception as e:
            print(f"Error adding documents to vector store: {str(e)}")
            raise

    def generate_response(self, query):
        """
        Generate a response using both static context and RAG retrieval.
        
        Args:
            query (str): User's input query
        
        Returns:
            str: Generated response
        
        Raises:
            Exception: If there's an error generating the response
        """
        try:
            response = self.chain({"query": query})
            return response["result"]
        except Exception as e:
            print(f"Generation error: {e}")
            raise
    def generate_basic_response(self, query):
        """
        Generate a response to the user's query.
        
        Args:
            query (str): User's input query
        
        Returns:
            str: Generated response
        
        Raises:
            Exception: If there's an error generating the response
        """
        try:
            response = self.llm.invoke(query)
            return response.content
        except Exception as e:
            print(f"Generation error: {e}")
            raise

    def chat(self):
        """Interactive chat loop with special commands."""
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() == 'exit':
                print("Goodbye!")
                break
            
            try:
                response = self.generate_response(user_input)
                print("\nChatbot:", response)
                print()
            except Exception as e:
                print(f"An error occurred: {e}")
