# HR Policy FAQ Chatbot

A Retrieval-Augmented Generation (RAG) chatbot that answers HR policy questions using a fictional company knowledge base, with confidence-based human handoff, role-based access, and full interaction logging.

## Features

- Answers HR/policy FAQs using a knowledge base
- Cites the exact policy section and policy ID used for every answer
- Shows the relevant HR form, when applicable
- Uses similarity-based confidence thresholds
- Hands off low-confidence questions to HR instead of guessing
- Role-based views: Employee / HR Staff / HR Admin
- Logs every interaction to SQLite

## Tech Stack

- Python
- Streamlit — user interface
- Pandas — policy data handling
- Sentence Transformers (`all-MiniLM-L6-v2`) — text embeddings
- Scikit-learn — cosine similarity retrieval
- Ollama (`llama3.2:1b`) — local answer generation
- SQLite — interaction logging

## Architecture

User Question
↓
Convert question into embedding
↓
Retrieve the most similar HR policy
↓
Calculate confidence score
↓
Confidence Check
├── High → Generate answer
├── Medium → Generate answer + uncertainty note
└── Low → Human handoff to HR
↓
Display answer
↓
Show policy source + related form
↓
Log interaction in SQLite

## Confidence Thresholds

- High confidence: score >= 0.55
- Medium confidence: 0.35 <= score < 0.55
- Low confidence: score < 0.35

Low-confidence questions are not sent to the LLM. Instead, the chatbot asks the employee to contact HR.

## Role-Based Access

### Employee
- Ask HR policy questions
- View answers
- View policy source and related forms

### HR Staff
- All Employee features
- View confidence level and similarity score

### HR Admin
- All HR Staff features
- View interaction statistics
- View logged conversations

## Project Structure

```text
hr-faq-chatbot/
│
├── data/
│   └── hr_policies.csv
│
├── logs/
│   └── chatbot_logs.db
│
├── app.py
├── retrieval.py
├── confidence.py
├── generation.py
├── logger.py
├── requirements.txt
├── README.md
└── .gitignore


Project Status
The current version includes:
Policy knowledge base
Semantic retrieval
Confidence-based handoff
Local LLM generation
Streamlit chatbot UI
Role-based access
SQLite interaction logging
Edge-case handling
Clear chat functionality


Future Improvements
Add real employee authentication
Add more HR policies
Support multi-policy retrieval
Add multi-turn conversation memory
Allow HR Admins to update the knowledge base
Add CSV export for interaction logs
Improve answer evaluation and grounding checks
Deploy the chatbot for organizational use
