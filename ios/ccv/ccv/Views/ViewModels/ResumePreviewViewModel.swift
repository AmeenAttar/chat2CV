import Foundation
import Combine

@MainActor
class ResumePreviewViewModel: ObservableObject {
    @Published var resumeData: ResumeData?
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var htmlContent: String = ""
    
    private let apiService = APIService.shared
    private var cancellables = Set<AnyCancellable>()
    
    // Sample user ID for development
    private let userId = "test@example.com"
    
    init() {
        loadResumeData()
        
        // Listen for resume updates
        NotificationCenter.default.addObserver(
            forName: .resumeUpdated,
            object: nil,
            queue: .main
        ) { _ in
            Task { @MainActor in
                self.loadResumeData()
            }
        }
    }
    
    func loadResumeData() {
        isLoading = true
        errorMessage = nil
        
        Task {
            do {
                let data = try await apiService.getResume(userId: userId)
                self.resumeData = data
                self.isLoading = false
                
                // Load HTML preview
                await loadHTMLPreview()
                
            } catch {
                // If it's a 404, that means no resume exists yet - this is normal
                if let apiError = error as? APIError, apiError.status_code == 404 {
                    self.errorMessage = nil
                    self.htmlContent = ""
                } else {
                    self.errorMessage = error.localizedDescription
                }
                self.isLoading = false
            }
        }
    }
    
    private func loadHTMLPreview() async {
        do {
            let html = try await apiService.getResumeHTML(userId: userId, theme: "professional")
            self.htmlContent = html
        } catch {
            self.errorMessage = "Failed to load preview: \(error.localizedDescription)"
        }
    }
    
    func refreshResume() {
        loadResumeData()
    }
} 