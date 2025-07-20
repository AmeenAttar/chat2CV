# Chat-to-CV Backend

Backend service for the Chat-to-CV iOS application, focusing on the Resume Writer AI Agent (Epic 5).

## Features

- **Resume Writer AI Agent**: Core AI service using LangChain + LlamaIndex for RAG
- **Template Management**: Resume template storage and retrieval
- **Real-time Updates**: WebSocket support for live resume building
- **API Endpoints**: RESTful API for resume generation and management

## Quick Start

1. **Clone and Setup**:
   ```bash
   git clone <repository-url>
   cd v1
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**:
   ```bash
   cp env.example .env
   # Edit .env with your actual API keys
   ```

4. **Run the Server**:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

- `POST /generate-resume-section`: Generate resume content from user input
- `GET /templates`: Get available resume templates
- `GET /resume/{user_id}`: Get current resume state
- `WS /ws/{user_id}`: WebSocket for real-time updates

## Project Structure

```
v1/
├── app/
│   ├── main.py              # FastAPI application
│   ├── models/              # Pydantic models
│   ├── services/            # Business logic
│   │   ├── ai_agent.py      # Resume Writer AI Agent
│   │   └── template_service.py
│   ├── knowledge_base/      # LlamaIndex knowledge base
│   └── templates/           # Resume templates
├── requirements.txt
├── env.example
└── README.md
```

## Development

- **Virtual Environment**: Always activate `venv` before development
- **Environment Variables**: Copy `env.example` to `.env` and configure
- **Dependencies**: Add new packages to `requirements.txt`
- **Git**: Follow conventional commit messages

## MVP Strategy

Following the MVP-first approach:
1. **Backend-first**: Focus on Resume Writer AI Agent (Epic 5)
2. **Core API**: `/generate-resume-section` endpoint
3. **Simple Templates**: Static template hosting initially
4. **Text-based Input**: Defer voice integration for later 