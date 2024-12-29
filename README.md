# RAG Chatbot for Ride Records Analytics

This project builds a **Retrieval-Augmented Generation (RAG) chatbot** that allows users to query ride records from a CSV (or text) file. The chatbot utilizes advanced natural language processing (NLP) and retrieval techniques to provide analytical insights based on the ride data, such as identifying top-performing chauffeurs, analyzing earnings over time, and answering other business-related questions.

The chatbot integrates **Pinecone** for vector storage and retrieval, **LangChain** for RAG workflows, and **Groq** for AI-based query processing.

The goal is to enable users to ask complex questions related to the ride data and receive insightful answers, including visualizations like graphs, trend analysis, and more.
## To use
- add 'rag_text.txt' in the same directory as main.py to add files to your vector storage.
- add 'bookings.csv' in the same directory as main.py to analyze csv files and ask the chatbot questions about your csv.
## Features

### Current Features
- **CSV/Text Parsing and Querying**: The chatbot can load and process ride data from `.txt` files, containing details such as `Booking#`, `Chauffeur`, `Price`, `Date`, etc.
- **RAG-based Query Responses**: The chatbot uses **LangChain** and **Pinecone** for context retrieval and to answer user queries dynamically.
  - Examples include:
    - "Who made the most money in July?"
    - "How many rides did Chauffeur X complete last month?"
    - "What is the total earnings for a specific date range?"
- **Data Retrieval**: The chatbot uses **Pinecone**'s vector search to retrieve relevant context from the ride data and then generates answers using a **Groq** model through **LangChain**.
- **Flexible Data Input**: Ability to load ride records in text format and index them for later querying.

### Planned Improvements
- **Dynamic Graphing and Visualizations**: Integrating libraries like **Plotly** or **Matplotlib** to visualize ride trends, chauffeur earnings, and other key metrics.
- **Real-Time Querying**: Provide live querying capabilities to allow users to ask questions about new, incoming ride records.
- **Advanced Query Handling**: Add support for more sophisticated queries, such as:
  - Identifying peak ride times.
  - Calculating earnings trends (percentage increases, month-over-month comparisons).
  - Analyzing patterns in customer bookings and chauffeur performance.

### Technologies Used
- **Python**: Primary language for backend logic.
- **LangChain**: Framework for building RAG (Retrieval-Augmented Generation) workflows.
- **Pinecone**: Vector database for efficient document search and retrieval.
- **Groq (via LangChain)**: AI model for processing queries and generating responses.
- **Sentence-Transformers**: Used to generate embeddings for the ride records to store in Pinecone.
- **HuggingFaceEmbeddings**: For creating embeddings with HuggingFace models.
- **Plotly / Matplotlib** (future): For generating dynamic trend graphs and charts.
