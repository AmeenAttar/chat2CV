#!/bin/bash

# iOS Project Setup Script for Chat-to-CV
# This script helps set up the iOS development environment

echo "🚀 Setting up iOS development environment for Chat-to-CV..."

# Check if Xcode is installed
if ! command -v xcodebuild &> /dev/null; then
    echo "❌ Xcode is not installed. Please install Xcode from the App Store."
    exit 1
fi

echo "✅ Xcode is installed"

# Check if we're in the right directory
if [ ! -d "../backend" ]; then
    echo "❌ Please run this script from the ios/ directory"
    exit 1
fi

echo "✅ Backend directory found"

# Create necessary directories
echo "📁 Creating iOS project structure..."
mkdir -p ChatToCV/Models
mkdir -p ChatToCV/Views/TemplateSelection
mkdir -p ChatToCV/Views/Chat
mkdir -p ChatToCV/Views/ResumePreview
mkdir -p ChatToCV/Views/Common
mkdir -p ChatToCV/Services
mkdir -p ChatToCV/ViewModels
mkdir -p ChatToCV/Resources

echo "✅ Directory structure created"

# Copy API models and service
echo "📋 Copying API models and service..."
cp API_Models.swift ChatToCV/Models/
cp APIService.swift ChatToCV/Services/

echo "✅ API files copied"

# Create Info.plist for localhost access
echo "🔧 Creating Info.plist for localhost access..."
cat > ChatToCV/Info.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSAllowsArbitraryLoads</key>
        <true/>
        <key>NSExceptionDomains</key>
        <dict>
            <key>localhost</key>
            <dict>
                <key>NSExceptionAllowsInsecureHTTPLoads</key>
                <true/>
            </dict>
        </dict>
    </dict>
</dict>
</plist>
EOF

echo "✅ Info.plist created for localhost access"

# Create basic app structure
echo "📱 Creating basic app structure..."

# Main App file
cat > ChatToCV/ChatToCVApp.swift << EOF
import SwiftUI

@main
struct ChatToCVApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
EOF

# Content View
cat > ChatToCV/Views/ContentView.swift << EOF
import SwiftUI

struct ContentView: View {
    var body: some View {
        TabView {
            TemplateSelectionView()
                .tabItem {
                    Image(systemName: "doc.text")
                    Text("Templates")
                }
            
            ChatView()
                .tabItem {
                    Image(systemName: "message")
                    Text("Chat")
                }
            
            ResumePreviewView()
                .tabItem {
                    Image(systemName: "eye")
                    Text("Preview")
                }
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
EOF

# Template Selection View
cat > ChatToCV/Views/TemplateSelection/TemplateSelectionView.swift << EOF
import SwiftUI

struct TemplateSelectionView: View {
    @StateObject private var viewModel = TemplateSelectionViewModel()
    
    var body: some View {
        NavigationView {
            List(viewModel.templates) { template in
                TemplateRowView(template: template)
            }
            .navigationTitle("Choose Template")
            .onAppear {
                viewModel.loadTemplates()
            }
        }
    }
}

struct TemplateRowView: View {
    let template: TemplateInfo
    
    var body: some View {
        VStack(alignment: .leading) {
            Text(template.name)
                .font(.headline)
            Text(template.description)
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
        .padding(.vertical, 8)
    }
}

struct TemplateSelectionView_Previews: PreviewProvider {
    static var previews: some View {
        TemplateSelectionView()
    }
}
EOF

# Template Selection ViewModel
cat > ChatToCV/ViewModels/TemplateSelectionViewModel.swift << EOF
import Foundation
import Combine

class TemplateSelectionViewModel: ObservableObject {
    @Published var templates: [TemplateInfo] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let apiService = APIService.shared
    private var cancellables = Set<AnyCancellable>()
    
    func loadTemplates() {
        isLoading = true
        errorMessage = nil
        
        apiService.fetchTemplates()
            .sink(
                receiveCompletion: { [weak self] completion in
                    self?.isLoading = false
                    if case .failure(let error) = completion {
                        self?.errorMessage = error.localizedDescription
                    }
                },
                receiveValue: { [weak self] templates in
                    self?.templates = templates
                }
            )
            .store(in: &cancellables)
    }
}
EOF

# Chat View
cat > ChatToCV/Views/Chat/ChatView.swift << EOF
import SwiftUI

struct ChatView: View {
    @StateObject private var viewModel = ChatViewModel()
    
    var body: some View {
        NavigationView {
            VStack {
                ScrollView {
                    LazyVStack {
                        ForEach(viewModel.messages, id: \.id) { message in
                            MessageBubble(message: message)
                        }
                    }
                    .padding()
                }
                
                HStack {
                    TextField("Type your message...", text: $viewModel.messageText)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                    
                    Button("Send") {
                        viewModel.sendMessage()
                    }
                    .disabled(viewModel.messageText.isEmpty)
                }
                .padding()
            }
            .navigationTitle("Chat with AI")
        }
    }
}

struct MessageBubble: View {
    let message: ChatMessage
    
    var body: some View {
        HStack {
            if message.isFromUser {
                Spacer()
            }
            
            Text(message.content)
                .padding()
                .background(message.isFromUser ? Color.blue : Color.gray.opacity(0.2))
                .foregroundColor(message.isFromUser ? .white : .primary)
                .cornerRadius(12)
            
            if !message.isFromUser {
                Spacer()
            }
        }
    }
}

struct ChatView_Previews: PreviewProvider {
    static var previews: some View {
        ChatView()
    }
}
EOF

# Chat ViewModel
cat > ChatToCV/ViewModels/ChatViewModel.swift << EOF
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
EOF

# Resume Preview View
cat > ChatToCV/Views/ResumePreview/ResumePreviewView.swift << EOF
import SwiftUI

struct ResumePreviewView: View {
    @StateObject private var viewModel = ResumePreviewViewModel()
    
    var body: some View {
        NavigationView {
            VStack {
                if viewModel.isLoading {
                    ProgressView("Loading resume...")
                } else if let htmlContent = viewModel.htmlContent {
                    WebView(htmlContent: htmlContent)
                } else {
                    VStack {
                        Image(systemName: "doc.text")
                            .font(.system(size: 60))
                            .foregroundColor(.gray)
                        Text("No resume preview available")
                            .font(.headline)
                            .foregroundColor(.gray)
                        Text("Start building your resume in the Chat tab")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                }
            }
            .navigationTitle("Resume Preview")
        }
    }
}

struct WebView: UIViewRepresentable {
    let htmlContent: String
    
    func makeUIView(context: Context) -> UIWebView {
        let webView = UIWebView()
        webView.loadHTMLString(htmlContent, baseURL: nil)
        return webView
    }
    
    func updateUIView(_ uiView: UIWebView, context: Context) {
        uiView.loadHTMLString(htmlContent, baseURL: nil)
    }
}

struct ResumePreviewView_Previews: PreviewProvider {
    static var previews: some View {
        ResumePreviewView()
    }
}
EOF

# Resume Preview ViewModel
cat > ChatToCV/ViewModels/ResumePreviewViewModel.swift << EOF
import Foundation
import Combine

class ResumePreviewViewModel: ObservableObject {
    @Published var htmlContent: String?
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let apiService = APIService.shared
    private var cancellables = Set<AnyCancellable>()
    
    func loadResumePreview(userId: String = "test-user") {
        isLoading = true
        errorMessage = nil
        
        apiService.getResumeHTML(userId: userId)
            .sink(
                receiveCompletion: { [weak self] completion in
                    self?.isLoading = false
                    if case .failure(let error) = completion {
                        self?.errorMessage = error.localizedDescription
                    }
                },
                receiveValue: { [weak self] html in
                    self?.htmlContent = html
                }
            )
            .store(in: &cancellables)
    }
}
EOF

echo "✅ Basic app structure created"

echo ""
echo "🎉 iOS project setup complete!"
echo ""
echo "Next steps:"
echo "1. Open Xcode"
echo "2. Create new iOS project: File → New → Project"
echo "3. Choose iOS → App template"
echo "4. Set Product Name: ChatToCV"
echo "5. Choose your team and organization identifier"
echo "6. Select SwiftUI interface"
echo "7. Copy the generated files from ChatToCV/ to your Xcode project"
echo "8. Add Info.plist settings for localhost access"
echo "9. Build and run!"
echo ""
echo "📱 Your iOS app is ready for development!" 