import Foundation
import Combine

@MainActor
class TemplateSelectionViewModel: ObservableObject {
    @Published var templates: [TemplateInfo] = []
    @Published var selectedTemplate: TemplateInfo?
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var shouldNavigateToChat = false
    @Published var sessionId: String?
    @Published var voiceflowWelcomeMessage: String?
    @Published var resumeId: Int?
    
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
                self.templates = templates.map { template in
                    if let url = template.preview_url, !url.isEmpty {
                        return template
                    } else {
                        // Fallback mapping for 16 known templates
                        let fallbackPreviews: [String: String] = [
                            "jsonresume-theme-standard": "https://raw.githubusercontent.com/jsonresume/jsonresume-theme-standard/master/screenshot.png",
                            "jsonresume-theme-even": "https://raw.githubusercontent.com/rraallvv/jsonresume-theme-even/master/screenshot.png",
                            "jsonresume-theme-stackoverflow": "https://raw.githubusercontent.com/kelyvin/jsonresume-theme-stackoverflow/master/screenshot.png",
                            "jsonresume-theme-cv": "https://raw.githubusercontent.com/eddiejaoude/jsonresume-theme-cv/master/screenshot.png",
                            "jsonresume-theme-slick": "https://raw.githubusercontent.com/SpencerCDixon/jsonresume-theme-slick/master/screenshot.png",
                            "jsonresume-theme-eloquent": "https://raw.githubusercontent.com/saadq/jsonresume-theme-eloquent/master/screenshot.png",
                            "jsonresume-theme-kendall": "https://raw.githubusercontent.com/saadq/jsonresume-theme-kendall/master/screenshot.png",
                            "jsonresume-theme-flat": "https://raw.githubusercontent.com/ahmadabdolsaheb/jsonresume-theme-flat/master/screenshot.png",
                            "jsonresume-theme-onepage": "https://raw.githubusercontent.com/fraserxu/jsonresume-theme-onepage/master/screenshot.png",
                            "jsonresume-theme-spartacus": "https://raw.githubusercontent.com/saadq/jsonresume-theme-spartacus/master/screenshot.png",
                            "jsonresume-theme-boilerplate": "https://raw.githubusercontent.com/jsonresume/jsonresume-theme-boilerplate/master/screenshot.png",
                            "jsonresume-theme-classic": "https://raw.githubusercontent.com/FlavioFalcao/jsonresume-theme-classic/master/screenshot.png",
                            "jsonresume-theme-modern": "https://raw.githubusercontent.com/Mehdi-Hp/jsonresume-theme-modern/master/screenshot.png",
                            "jsonresume-theme-actual": "https://raw.githubusercontent.com/FlavioFalcao/jsonresume-theme-actual/master/screenshot.png",
                            "jsonresume-theme-caffeine": "https://raw.githubusercontent.com/kelyvin/jsonresume-theme-caffeine/master/screenshot.png",
                            "jsonresume-theme-simplistic": "https://raw.githubusercontent.com/saadq/jsonresume-theme-simplistic/master/screenshot.png"
                        ]
                        let fallbackUrl = fallbackPreviews[template.id] ?? fallbackPreviews[template.npm_package ?? ""]
                        return TemplateInfo(
                            id: template.id,
                            name: template.name,
                            description: template.description,
                            preview_url: fallbackUrl,
                            npm_package: template.npm_package,
                            version: template.version,
                            author: template.author,
                            category: template.category
                        )
                    }
                }
                self.isLoading = false
            } catch {
                self.errorMessage = error.localizedDescription
                self.isLoading = false
            }
        }
    }
    
    func sendVoiceflowLaunch() async {
        guard let sessionId = self.sessionId else { return }
        let versionId = ProcessInfo.processInfo.environment["VOICEFLOW_VERSION_ID"] ?? "687e98b78c172f00083ea98f"
        let urlString = "https://general-runtime.voiceflow.com/state/\(versionId)/user/\(sessionId)/interact"
        guard let url = URL(string: urlString) else { return }
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        let body: [String: Any] = [
            "request": ["type": "launch"],
            "state": [
                "variables": [
                    "resume_id": resumeId ?? 0
                ]
            ]
        ]
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        do {
            let (data, _) = try await URLSession.shared.data(for: request)
            if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
               let trace = json["trace"] as? [[String: Any]],
               let first = trace.first,
               let payload = first["payload"] as? String {
                await MainActor.run {
                    self.voiceflowWelcomeMessage = payload
                }
            }
        } catch {
            // Optionally handle error
        }
    }
    
    func selectTemplate(_ template: TemplateInfo) {
        selectedTemplate = template
        isLoading = true
        errorMessage = nil
        Task {
            do {
                let response = try await apiService.createSession(templateId: Int(template.id) ?? 1)
                self.sessionId = response.session_id
                self.resumeId = response.resume_id
                self.isLoading = false
                self.shouldNavigateToChat = true
                await sendVoiceflowLaunch()
            } catch {
                self.errorMessage = error.localizedDescription
                self.isLoading = false
            }
        }
    }
} 