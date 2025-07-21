import SwiftUI
import WebKit

struct ResumePreviewView: View {
    @StateObject private var viewModel = ResumePreviewViewModel()
    
    var body: some View {
        NavigationView {
            Group {
                if viewModel.isLoading {
                    ProgressView("Loading resume...")
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if let error = viewModel.errorMessage {
                    VStack {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.largeTitle)
                            .foregroundColor(.orange)
                        Text("Error loading resume")
                            .font(.headline)
                        Text(error)
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                        Button("Retry") {
                            viewModel.refreshResume()
                        }
                        .buttonStyle(.borderedProminent)
                    }
                    .padding()
                } else if !viewModel.htmlContent.isEmpty {
                    VStack {
                        // Progress indicator
                        if let resumeData = viewModel.resumeData {
                            ResumeProgressView(completenessSummary: resumeData.completeness_summary)
                                .padding()
                        }
                        
                        WebView(htmlContent: viewModel.htmlContent)
                    }
                } else {
                    VStack(spacing: 16) {
                        Image(systemName: "doc.text")
                            .font(.largeTitle)
                            .foregroundColor(.gray)
                        Text("No resume data available")
                            .font(.headline)
                        Text("Start chatting with the AI to build your resume")
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                        
                        Button("Go to Chat") {
                            // Switch to chat tab
                            NotificationCenter.default.post(name: .switchToChat, object: nil)
                        }
                        .buttonStyle(.borderedProminent)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                }
            }
            .navigationTitle("Resume Preview")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: viewModel.refreshResume) {
                        Image(systemName: "arrow.clockwise")
                    }
                    .disabled(viewModel.isLoading)
                }
            }
        }
    }
}

struct WebView: UIViewRepresentable {
    let htmlContent: String
    
    func makeUIView(context: Context) -> WKWebView {
        let webView = WKWebView()
        webView.loadHTMLString(htmlContent, baseURL: nil)
        return webView
    }
    
    func updateUIView(_ uiView: WKWebView, context: Context) {
        uiView.loadHTMLString(htmlContent, baseURL: nil)
    }
}

#Preview {
    ResumePreviewView()
} 