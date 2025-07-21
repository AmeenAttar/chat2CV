# Chat-to-CV Project

A comprehensive iOS application that allows users to chat with an AI assistant to build and refine their resume.

## Project Structure

```
v1/
├── backend/                 # Python FastAPI backend
│   ├── app/                # Main application code
│   ├── alembic/            # Database migrations
│   ├── static/             # Template previews and assets
│   ├── requirements.txt    # Python dependencies
│   └── env.example         # Environment variables template
├── tests/                  # All test files
│   ├── test_*.py          # Individual test modules
│   ├── run_tests.py       # Test runner
│   └── pytest.ini         # Pytest configuration
├── docs/                   # Documentation and project details
├── scripts/                # Utility scripts
├── archive/                # Archived/unused files (gitignored)
├── ios/                    # iOS app (ready for development)
└── README.md
```

## Current Status

✅ **Epic 5: Resume Writer AI Agent - WORKING**
- SimpleResumeAgent with direct LLM calls
- Multiple provider fallback system
- JSON Resume format compliance
- 84.6% test success rate

## Quick Start

1. **Setup Backend**:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp env.example .env
   # Edit .env with your API keys
   ```

2. **Run Backend**:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

3. **Run Tests**:
   ```bash
   ./run_tests.sh
   ```

## API Endpoints

- `POST /generate-resume-section`: Generate resume content from user input
- `GET /templates`: Get available resume templates
- `GET /resume/{user_id}`: Get current resume state

## Development Strategy

**MVP-First Approach:**
1. ✅ **Backend Complete**: Resume Writer AI Agent working
2. 🎯 **iOS Development**: Ready to start - Template selection UI prepared
3. 📋 **Voiceflow Integration**: Text-based chat first, then voice
4. 💳 **Payment & Polish**: Final features

## Technology Stack

- **Backend**: Python, FastAPI, SQLAlchemy, PostgreSQL
- **AI**: Direct LLM calls (Gemini/OpenAI) with fallbacks
- **iOS**: SwiftUI (coming soon)
- **Templates**: JSON Resume standard

## Contributing

- Follow MVP strategy
- Test all changes: `./run_tests.sh`
- Keep backend-first approach
- Focus on iOS development next 