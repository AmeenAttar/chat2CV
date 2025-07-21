# Chat-to-CV iOS App

SwiftUI-based iOS application for the Chat-to-CV project.

## Project Setup

1. **Open Xcode**
2. **Create New Project**: File → New → Project
3. **Choose Template**: iOS → App
4. **Project Settings**:
   - Product Name: `ChatToCV`
   - Team: Your Apple Developer Team
   - Organization Identifier: `com.yourcompany.chattocv`
   - Interface: `SwiftUI`
   - Language: `Swift`
   - Use Core Data: `No` (we'll use our backend)
   - Include Tests: `Yes`

## Project Structure

```
ChatToCV/
├── ChatToCV/
│   ├── ChatToCVApp.swift          # App entry point
│   ├── Models/                    # Data models
│   ├── Views/                     # SwiftUI views
│   │   ├── TemplateSelection/     # Epic 2: Template selection
│   │   ├── Chat/                  # Epic 3: Voice AI Assistant UI
│   │   ├── ResumePreview/         # Epic 6: Live resume building
│   │   └── Common/                # Shared components
│   ├── Services/                  # API services
│   ├── ViewModels/                # MVVM view models
│   └── Resources/                 # Assets, fonts, etc.
├── ChatToCVTests/                 # Unit tests
└── ChatToCVUITests/               # UI tests
```

## Backend Integration

- **Base URL**: `http://localhost:8000` (development)
- **Key Endpoints**:
  - `GET /templates` - Template catalog
  - `POST /generate-resume-section` - AI resume generation
  - `GET /resume/{user_id}` - Get resume data

## Development Phases

1. **Phase 1**: Template Selection UI (Epic 2)
2. **Phase 2**: Text Chat Interface (Epic 3 - simplified)
3. **Phase 3**: Resume Preview (Epic 6)
4. **Phase 4**: Voiceflow Integration (Epic 4)

## Dependencies

- **SwiftUI**: Native UI framework
- **Combine**: Reactive programming
- **URLSession**: Network requests
- **Core Data**: Local caching (optional) 