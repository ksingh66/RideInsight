import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

class ContextChatbot:
    def __init__(self, context_file="data_summary.txt", model_id="llama-3.1-70b-versatile"):
        """
        Initialize the chatbot with context loading capabilities.
        The chatbot will look for a context file in the same directory as the script.
        
        Args:
            context_file (str): Name of the context file to load
            model_id (str): The ID of the model to use for chat
        """
        # Load environment variables
        load_dotenv()
        
        # Store the context
        self.context = self._load_context_file(context_file)
        
        # Get the API key from environment variables
        groq_api_key = os.getenv('GROQ_API_KEY')
        
        if not groq_api_key:
            raise ValueError("Missing GROQ_API_KEY in environment variables. Please check your .env file.")
        
        # Initialize the language model with Groq
        self.llm = ChatGroq(
            temperature=0.7,
            max_tokens=500,
            groq_api_key=groq_api_key,
            model_name=model_id
        )
        
        # Create a template that includes the loaded context
        self.prompt_template = PromptTemplate(
            template="""
            Context Information:
            {context}

            Question: {question}
            
            Using the context provided above, please give a helpful and informative response.
            If the question cannot be answered using the context, please say so and provide
            a general response based on your knowledge.
            
            Answer:""",
            input_variables=["context", "question"]
        )

    def _load_context_file(self, filename):
        """
        Load context from a file in the same directory as the script.
        
        Args:
            filename (str): Name of the context file to load
            
        Returns:
            str: The content of the context file, or a message if file not found
        """
        try:
            # Get the directory where this script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Create the full path to the context file
            file_path = os.path.join(script_dir, filename)
            
            # Check if the file exists
            if not os.path.exists(file_path):
                print(f"Context file '{filename}' not found in the script directory.")
                print(f"Expected location: {file_path}")
                print("The chatbot will continue without context information.\n")
                return "No context file was found."
            
            # Read and return the file contents
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                print(f"Successfully loaded context from '{filename}'")
                # Show a preview of the loaded context
                preview = content[:100] + "..." if len(content) > 100 else content
                print(f"Context preview: {preview}\n")
                return content
                
        except Exception as e:
            print(f"Error reading context file: {str(e)}")
            return "Error loading context file."

    def generate_response(self, user_input):
        """
        Generate a response to the user's input using the loaded context.
        
        Args:
            user_input (str): The user's question or message
            
        Returns:
            str: The chatbot's response
        """
        try:
            # Format the prompt with both context and user input
            prompt = self.prompt_template.format(
                context=self.context,
                question=user_input
            )
            
            # Generate a response using the language model
            response = self.llm.invoke(prompt)
            
            return response.content
            
        except Exception as e:
            return f"An error occurred: {str(e)}"

    def chat(self):
        """
        Start an interactive chat session with the user.
        """
        print("Chatbot is ready! Type 'exit' to quit.")
        print("Type 'show context' to see the current context information.\n")
        
        while True:
            # Get user input
            user_input = input("You: ").strip()
            
            # Check for special commands
            if user_input.lower() == 'exit':
                print("Goodbye!")
                break
            
            if user_input.lower() == 'show context':
                print("\nCurrent Context:")
                print(self.context)
                print()
                continue
            
            # Generate and print response
            response = self.generate_response(user_input)
            print("\nChatbot:", response)
            print()  # Add a blank line for readability

def main():
    try:
        # Create and start the chatbot
        chatbot = ContextChatbot()
        chatbot.chat()
        
    except Exception as e:
        print(f"Error starting chatbot: {str(e)}")

if __name__ == "__main__":
    main()