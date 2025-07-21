import SwiftUI

struct ChatView: View {
    let selectedTemplate: TemplateInfo?
    @StateObject private var viewModel = ChatViewModel()
    
    init(selectedTemplate: TemplateInfo? = nil) {
        self.selectedTemplate = selectedTemplate
    }
    
    var body: some View {
        NavigationView {
            VStack {
                // Template indicator
                if let template = selectedTemplate {
                    HStack {
                        Image(systemName: "doc.text")
                            .foregroundColor(.blue)
                        Text("Template: \(template.name)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Spacer()
                    }
                    .padding(.horizontal)
                    .padding(.vertical, 8)
                    .background(Color(.systemGray6))
                }
                
                // Messages
                ScrollViewReader { proxy in
                    ScrollView {
                        LazyVStack(spacing: 12) {
                            ForEach(viewModel.messages) { message in
                                MessageBubble(message: message)
                                    .id(message.id)
                            }
                            
                            if viewModel.isLoading {
                                HStack {
                                    ProgressView()
                                        .scaleEffect(0.8)
                                    Text("AI is thinking...")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                }
                                .padding(.horizontal)
                                .padding(.vertical, 8)
                            }
                        }
                        .padding()
                    }
                    .onChange(of: viewModel.messages.count) { _, _ in
                        if let lastMessage = viewModel.messages.last {
                            withAnimation(.easeInOut(duration: 0.3)) {
                                proxy.scrollTo(lastMessage.id, anchor: .bottom)
                            }
                        }
                    }
                }
                
                // Input area
                VStack(spacing: 0) {
                    Divider()
                    
                    HStack {
                        TextField("Type your message...", text: $viewModel.inputText, axis: .vertical)
                            .textFieldStyle(.roundedBorder)
                            .lineLimit(1...4)
                        
                        Button(action: viewModel.sendMessage) {
                            Image(systemName: "arrow.up.circle.fill")
                                .font(.title2)
                                .foregroundColor(.blue)
                        }
                        .disabled(viewModel.inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || viewModel.isLoading)
                    }
                    .padding()
                }
            }
            .navigationTitle("Chat with AI")
            .navigationBarTitleDisplayMode(.large)
        }
        .onAppear {
            if let template = selectedTemplate {
                viewModel.setTemplate(template)
            }
        }
        .alert("Error", isPresented: .constant(viewModel.errorMessage != nil)) {
            Button("OK") {
                viewModel.errorMessage = nil
            }
        } message: {
            if let error = viewModel.errorMessage {
                Text(error)
            }
        }
    }
}

struct MessageBubble: View {
    let message: ChatMessage
    
    var body: some View {
        HStack {
            if message.isUser {
                Spacer()
                Text(message.content)
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(16)
                    .frame(maxWidth: UIScreen.main.bounds.width * 0.7, alignment: .trailing)
            } else {
                VStack(alignment: .leading, spacing: 8) {
                    Text(message.content)
                        .padding()
                        .background(Color(.systemGray5))
                        .foregroundColor(.primary)
                        .cornerRadius(16)
                        .frame(maxWidth: UIScreen.main.bounds.width * 0.7, alignment: .leading)
                    
                    // Show timestamp for AI messages
                    Text(message.timestamp, style: .time)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                        .padding(.leading, 8)
                }
                Spacer()
            }
        }
    }
}

#Preview {
    ChatView()
} 