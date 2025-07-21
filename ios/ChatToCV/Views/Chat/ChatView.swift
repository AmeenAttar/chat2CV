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
                    TextField("Type your message...", text: .messageText)
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
