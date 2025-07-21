import Foundation
import Combine

@MainActor
class TemplateSelectionViewModel: ObservableObject {
    @Published var templates: [TemplateInfo] = []
    @Published var selectedTemplate: TemplateInfo?
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var shouldNavigateToChat = false
    
    private let apiService = APIService.shared
    private var cancellables = Set<AnyCancellable>()
    
    init() {
        loadTemplates()
    }
    
    func loadTemplates() {
        isLoading = true
        errorMessage = nil
        
        Task {
            do {
                let templates = try await apiService.getTemplates()
                self.templates = templates
                self.isLoading = false
            } catch {
                self.errorMessage = error.localizedDescription
                self.isLoading = false
            }
        }
    }
    
    func selectTemplate(_ template: TemplateInfo) {
        selectedTemplate = template
        shouldNavigateToChat = true
    }
} 