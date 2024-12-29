from data_processor import DataSummarizer
from HybridBot import HybridChatbot
import os

def main():
    """
    Main function to coordinate data processing and chatbot initialization.
    """
    try:
        # Get the directory where main.py is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Construct absolute paths for all files
        csv_filename = os.path.join(current_dir, 'bookings.csv')
        summary_filename = os.path.join(current_dir, 'data_summary.txt')
        rag_data = os.path.join(current_dir, 'rag_text.txt')
        
        print(f"Looking for CSV file at: {csv_filename}")
        print(f"Summary will be saved to: {summary_filename}")
        
        print("Starting data analysis...")
        summarizer = DataSummarizer(csv_filename)
        summarizer.generate_summary(summary_filename)
        print("Data analysis complete!")
        
        print("\nStarting chatbot with generated summary...")
        chatbot = HybridChatbot(context_file=summary_filename, rag_data_file=rag_data)
        chatbot.chat()
        
    except FileNotFoundError as e:
        print(f"Error: Could not find file. Details: {str(e)}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()