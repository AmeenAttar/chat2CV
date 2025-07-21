# Chat-to-CV iOS App

A SwiftUI-based iOS application that allows users to build professional resumes through conversational AI.

## Features

### ✅ **Working Features**
- **Template Selection**: Browse and select from 16 professional resume templates
- **AI Chat Interface**: Conversational AI assistant for building resume content
- **Live Resume Preview**: Real-time HTML preview of the generated resume
- **Progress Tracking**: Visual progress indicator showing resume completion status
- **Smart Section Detection**: AI automatically determines which resume section to update based on user input

### 🚧 **In Development**
- Voice AI integration (Voiceflow)
- User authentication
- Payment processing
- PDF/Word export

## Getting Started

### Prerequisites
- Xcode 15.0 or later
- iOS 18.0 or later
- Backend server running on `http://localhost:8000`

### Installation
1. Open `ccv.xcodeproj` in Xcode
2. Select your development team in project settings
3. Build and run the app on iOS Simulator or device

### Backend Setup
Make sure the backend server is running:
```bash
cd backend
source ../venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Usage

### 1. Template Selection
- Browse available resume templates with preview images
- Each template has different styling and layout options
- Select a template to start building your resume

### 2. AI Chat Interface
- Chat naturally with the AI assistant
- Describe your experience, education, skills, etc.
- The AI will automatically:
  - Determine the appropriate resume section
  - Format and structure your content
  - Provide professional phrasing
  - Suggest next steps

### 3. Resume Preview
- View your resume in real-time as you chat
- See progress indicators for each section
- Preview how your resume will look in the selected template

## Architecture

### MVVM Pattern
- **Models**: API data structures and business logic
- **Views**: SwiftUI user interface components
- **ViewModels**: Business logic and state management

### Key Components
- `TemplateSelectionView`: Template browsing and selection
- `ChatView`: AI conversation interface
- `ResumePreviewView`: Live resume preview with progress tracking
- `APIService`: Backend communication layer

### Data Flow
1. User selects template → Template ID stored
2. User chats with AI → Content sent to backend
3. Backend processes content → Returns structured data
4. Resume preview updates automatically
5. Progress indicators reflect completion status

## API Integration

The app communicates with the backend through these endpoints:
- `GET /templates` - Get available templates
- `POST /generate-resume-section` - Generate resume content
- `GET /resume/{user_id}` - Get resume data
- `GET /resume/{user_id}/html` - Get HTML preview

## Development Notes

### Current Status
- ✅ Backend integration working
- ✅ Template system functional
- ✅ AI chat interface operational
- ✅ Resume preview with progress tracking
- ✅ Real-time updates between chat and preview

### Known Issues
- Minor deprecation warnings (non-critical)
- User ID validation requires email format
- Resume data persistence needs improvement

### Next Steps
1. Implement user authentication
2. Add voice AI integration
3. Improve resume data persistence
4. Add export functionality
5. Polish UI/UX

## Testing

The app has been tested with:
- iOS Simulator (iPhone 16)
- Backend API endpoints
- Template selection and preview
- AI chat functionality
- Resume generation and display

## Contributing

This is a single-person project focused on MVP development. The current priority is getting core functionality working before adding advanced features. 