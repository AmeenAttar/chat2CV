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
