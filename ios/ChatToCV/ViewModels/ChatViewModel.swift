import Foundation
import Combine

struct ChatMessage: Identifiable {
    let id = UUID()
    let content: String
    let isFromUser: Bool
    let timestamp: Date
}

class ChatViewModel: ObservableObject {
    @Published var messages: [ChatMessage] = []
    @Published var messageText = ""
    @Published var isLoading = false
    
    private let apiService = APIService.shared
    private var cancellables = Set<AnyCancellable>()
    
    init() {
        // Add welcome message
        messages.append(ChatMessage(
            content: "Hello! I'm your AI assistant. Let's build your resume together. What would you like to start with?",
            isFromUser: false,
            timestamp: Date()
        ))
    }
    
    func sendMessage() {
        guard !messageText.isEmpty else { return }
        
        let userMessage = ChatMessage(
            content: messageText,
            isFromUser: true,
            timestamp: Date()
        )
        messages.append(userMessage)
        
        let userInput = messageText
        messageText = ""
        isLoading = true
        
        // TODO: Implement actual AI integration
        // For now, just echo back
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            self.messages.append(ChatMessage(
                content: "I received: \(userInput). This will be integrated with the backend AI service.",
                isFromUser: false,
                timestamp: Date()
            ))
            self.isLoading = false
        }
    }
}
