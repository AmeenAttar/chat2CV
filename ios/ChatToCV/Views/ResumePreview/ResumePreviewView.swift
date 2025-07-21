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
