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
