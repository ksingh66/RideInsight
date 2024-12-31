# Media Directory

This directory temporarily stores files uploaded and processed by the CSV Chatbot application.

## Structure


## Purpose

- **csv_files/**: Temporarily stores user-uploaded CSV files during chat sessions
- **summaries/**: Stores text summaries generated from the CSV files that provide context for the chatbot

## Important Notes

- Files in these directories are temporary and are deleted when:
  - User ends their chat session
  - User closes their browser tab
  - Application cleans up old files
- These directories should not be committed to version control
- The application will automatically create these directories if they don't exist
- Files are linked to specific user sessions and are not shared between users

## File Naming Convention

- CSV files: Original filename stored in `csv_files/`
- Summaries: `summary_{id}.txt` stored in `summaries/`

## Security

- Only authenticated users can upload files
- Files are isolated per user session
- Files are automatically cleaned up after use