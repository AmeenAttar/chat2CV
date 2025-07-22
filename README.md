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
- `GET /resumes/{resume_id}/voiceflow-guidance`: Get next questions, context, and progress for Voiceflow
- `POST /create-session`: Create a new session and resume for a user

## Voiceflow Integration

- When a user selects a template in the iOS app, the app calls `/create-session` to get a `session_id` and `resume_id`.
- The app sends a `launch` request to Voiceflow, passing `resume_id` as a variable.
- The first Voiceflow API block calls `/resumes/{resume_id}/voiceflow-guidance` and maps these variables:
  - `resume_id`, `template_id`, `completeness_summary`, `conversation_context`, `suggested_topics`, `missing_critical_info`, `conversation_flow_hints`, `user_progress_insights`, `conversation_priority`, `next_questions`, `resume_stage`, `completion_percentage`
- The agent prompt is optimized for voice: concise, context-aware, and only repeats/clarifies when the backend flags a validation issue. It always uses `{next_questions[0]}` to drive the conversation and adapts based on template and progress.
- When the user answers, the app sends the answer to `/generate-resume-section` with all relevant variables. The backend updates the resume and returns new context for the next turn.
- The Agent block is used for help, fallback, or advice. It receives full context (e.g., `{template_id}`, `{resume_stage}`, `{next_questions[0]}`, `{user_input}`) and uses the knowledge base or backend to provide actionable, voice-friendly guidance.
- The agent is stateless: all session and resume data is managed by the backend. Privacy is maintained—no user data is stored in Voiceflow or the agent.
- Best practices: Always use backend-driven context, keep agent responses short and natural, and only confirm/repeat when necessary.

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