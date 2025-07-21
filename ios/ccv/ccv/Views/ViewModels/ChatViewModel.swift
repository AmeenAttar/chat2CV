import Foundation
import Combine

@MainActor
class ChatViewModel: ObservableObject {
    @Published var messages: [ChatMessage] = []
    @Published var inputText = ""
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var selectedTemplate: TemplateInfo?
    
    private let apiService = APIService.shared
    private var cancellables = Set<AnyCancellable>()
    
    // Sample user ID for development
    private let userId = "test@example.com"
    private var currentResumeId: Int?
    private var selectedTemplateId: Int = 1 // Default to template 1
    
    init() {
        // Add welcome message
        messages.append(ChatMessage(
            id: UUID(),
            content: "Hello! I'm your AI resume assistant. Let's start building your resume. What would you like to add first?",
            isUser: false,
            timestamp: Date()
        ))
    }
    
    func setTemplate(_ template: TemplateInfo) {
        selectedTemplate = template
        selectedTemplateId = apiService.getTemplateIdAsInt(template.id)
        
        // Update welcome message with template context
        if messages.count == 1 {
            messages[0] = ChatMessage(
                id: UUID(),
                content: "Hello! I'm your AI resume assistant. I'll help you build your resume using the \(template.name) template. This template is perfect for \(template.description.lowercased()). What would you like to add first?",
                isUser: false,
                timestamp: Date()
            )
        }
    }
    
    func sendMessage() {
        guard !inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }
        
        let userMessage = ChatMessage(
            id: UUID(),
            content: inputText,
            isUser: true,
            timestamp: Date()
        )
        
        messages.append(userMessage)
        let messageText = inputText
        inputText = ""
        
        // Send to AI
        generateResumeSection(messageText)
    }
    
    private func generateResumeSection(_ input: String) {
        isLoading = true
        errorMessage = nil
        
        Task {
            do {
                // Determine the appropriate section based on input content
                let sectionName = determineSectionFromInput(input)
                
                let request = GenerateResumeSectionRequest(
                    template_id: selectedTemplateId,
                    section_name: sectionName,
                    raw_input: input,
                    user_id: userId,
                    resume_id: currentResumeId
                )
                
                let response = try await apiService.generateResumeSection(request)
                
                // Create AI response message
                var aiContent = response.rephrased_content
                
                // Add helpful context from completeness summary
                if let nextTopic = response.resume_completeness_summary.suggested_topics.first {
                    aiContent += "\n\n💡 **Next suggestion:** \(nextTopic)"
                }
                
                let aiMessage = ChatMessage(
                    id: UUID(),
                    content: aiContent,
                    isUser: false,
                    timestamp: Date()
                )
                
                messages.append(aiMessage)
                isLoading = false
                
                // Update resume ID if this is the first successful generation
                if currentResumeId == nil {
                    // In a real app, you'd get the resume ID from the response
                    // For now, we'll use a placeholder
                    currentResumeId = 1
                }
                
                // Notify that resume data has been updated
                NotificationCenter.default.post(name: .resumeUpdated, object: nil)
                
            } catch {
                errorMessage = error.localizedDescription
                isLoading = false
            }
        }
    }
    
    private func determineSectionFromInput(_ input: String) -> String {
        let lowercased = input.lowercased()
        
        if lowercased.contains("work") || lowercased.contains("job") || lowercased.contains("experience") || lowercased.contains("employed") {
            return "work_experience"
        } else if lowercased.contains("education") || lowercased.contains("degree") || lowercased.contains("university") || lowercased.contains("college") || lowercased.contains("school") {
            return "education"
        } else if lowercased.contains("skill") || lowercased.contains("technology") || lowercased.contains("programming") || lowercased.contains("language") {
            return "skills"
        } else if lowercased.contains("project") || lowercased.contains("build") || lowercased.contains("develop") {
            return "projects"
        } else if lowercased.contains("name") || lowercased.contains("email") || lowercased.contains("phone") || lowercased.contains("contact") || lowercased.contains("personal") {
            return "personal_details"
        } else {
            // Default to work experience for general input
            return "work_experience"
        }
    }
}

struct ChatMessage: Identifiable {
    let id: UUID
    let content: String
    let isUser: Bool
    let timestamp: Date
} 