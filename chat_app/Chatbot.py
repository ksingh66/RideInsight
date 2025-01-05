from groq import Groq
import os 
from dotenv import load_dotenv

class Chatbot:
    def __init__(self, context_file=None, model="llama-3.3-70b-versatile"):
        """
        Initialize the chatbot with optional static context and a model to use for responses.

        Args:
            context_file (str, optional): Path to the file containing static context
            model (str): The ID of the model to use for chat (default: "llama-3.3-70b-versatile")
        """
        # Initialize Groq client
        load_dotenv()
        self.client = Groq(api_key= os.getenv('GROQ_API_KEY'))
        self.model = model
        
        # Load static context from file if provided
        self.context = self._load_context_file(context_file) if context_file else "You are a helpful assistant."

        # Initialize conversation history with context
        self.messages = [
            {"role": "system", "content": self.context}
        ]

    def _load_context_file(self, filename):
        """Load static context from a file."""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read().strip()
            return content
        except Exception as e:
            print(f"Error reading context file: {str(e)}")
            return "Error loading static context."

    def generate_response(self, user_input):
        """
        Generate a response based on the user's input and conversation history.

        Args:
            user_input (str): The user's message.
        
        Returns:
            str: The assistant's response.
        """
        # Add user input to the conversation history
        self.messages.append({"role": "user", "content": user_input})

        try:
            # Send the conversation to the Groq API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=True,
                stop=None,
            )

            # Collect and return the response from Groq API
            response = ""
            for chunk in completion:
                response += chunk.choices[0].delta.content or ""

            # Add assistant's response to conversation history
            self.messages.append({"role": "assistant", "content": response})
            return response

        except Exception as e:
            return f"Error: {str(e)}"
