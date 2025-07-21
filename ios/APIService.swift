// API Service for Chat-to-CV iOS App
// Handles all communication with the backend

import Foundation
import Combine

class APIService: ObservableObject {
    static let shared = APIService()
    
    // MARK: - Configuration
    private let baseURL = "http://localhost:8000"
    private let session = URLSession.shared
    
    private init() {}
    
    // MARK: - Generic Request Helper
    private func makeRequest<T: Codable>(_ request: URLRequest) -> AnyPublisher<T, Error> {
        return session.dataTaskPublisher(for: request)
            .map(\.data)
            .decode(type: T.self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
    
    // MARK: - Template Endpoints
    func fetchTemplates() -> AnyPublisher<[TemplateInfo], Error> {
        guard let url = URL(string: "\(baseURL)/templates") else {
            return Fail(error: APIError(detail: "Invalid URL", status_code: nil))
                .eraseToAnyPublisher()
        }
        
        let request = URLRequest(url: url)
        return makeRequest(request)
    }
    
    // MARK: - Resume Generation Endpoints
    func generateResumeSection(request: GenerateResumeSectionRequest) -> AnyPublisher<GenerateResumeSectionResponse, Error> {
        guard let url = URL(string: "\(baseURL)/generate-resume-section") else {
            return Fail(error: APIError(detail: "Invalid URL", status_code: nil))
                .eraseToAnyPublisher()
        }
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            urlRequest.httpBody = try JSONEncoder().encode(request)
        } catch {
            return Fail(error: error).eraseToAnyPublisher()
        }
        
        return makeRequest(urlRequest)
    }
    
    // MARK: - Resume Data Endpoints
    func getResumeData(userId: String) -> AnyPublisher<JSONResume, Error> {
        guard let url = URL(string: "\(baseURL)/resume/\(userId)/json") else {
            return Fail(error: APIError(detail: "Invalid URL", status_code: nil))
                .eraseToAnyPublisher()
        }
        
        let request = URLRequest(url: url)
        return makeRequest(request)
    }
    
    func getResumeHTML(userId: String, theme: String = "professional") -> AnyPublisher<String, Error> {
        guard let url = URL(string: "\(baseURL)/resume/\(userId)/html?theme=\(theme)") else {
            return Fail(error: APIError(detail: "Invalid URL", status_code: nil))
                .eraseToAnyPublisher()
        }
        
        let request = URLRequest(url: url)
        return session.dataTaskPublisher(for: request)
            .map { String(data: $0.data, encoding: .utf8) ?? "" }
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
    
    // MARK: - Resume Management Endpoints
    func createResume(request: CreateResumeRequest) -> AnyPublisher<JSONResume, Error> {
        guard let url = URL(string: "\(baseURL)/resumes") else {
            return Fail(error: APIError(detail: "Invalid URL", status_code: nil))
                .eraseToAnyPublisher()
        }
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            urlRequest.httpBody = try JSONEncoder().encode(request)
        } catch {
            return Fail(error: error).eraseToAnyPublisher()
        }
        
        return makeRequest(urlRequest)
    }
    
    func getUserResumes(email: String) -> AnyPublisher<[JSONResume], Error> {
        guard let url = URL(string: "\(baseURL)/resumes/\(email)") else {
            return Fail(error: APIError(detail: "Invalid URL", status_code: nil))
                .eraseToAnyPublisher()
        }
        
        let request = URLRequest(url: url)
        return makeRequest(request)
    }
    
    // MARK: - Health Check
    func healthCheck() -> AnyPublisher<String, Error> {
        guard let url = URL(string: "\(baseURL)/health") else {
            return Fail(error: APIError(detail: "Invalid URL", status_code: nil))
                .eraseToAnyPublisher()
        }
        
        let request = URLRequest(url: url)
        return session.dataTaskPublisher(for: request)
            .map { String(data: $0.data, encoding: .utf8) ?? "" }
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
    
    // MARK: - Error Handling
    func handleError(_ error: Error) -> String {
        if let apiError = error as? APIError {
            return apiError.detail
        }
        return error.localizedDescription
    }
}

// MARK: - Mock Data for Development
extension APIService {
    static func mockTemplates() -> [TemplateInfo] {
        return [
            TemplateInfo(
                id: "1",
                name: "Professional",
                description: "Clean and traditional resume template",
                preview_url: "https://example.com/professional.png",
                npm_package: "jsonresume-theme-professional",
                version: "1.0.0",
                author: "JSON Resume",
                category: "Professional"
            ),
            TemplateInfo(
                id: "2",
                name: "Modern",
                description: "Contemporary design with modern typography",
                preview_url: "https://example.com/modern.png",
                npm_package: "jsonresume-theme-modern",
                version: "1.0.0",
                author: "JSON Resume",
                category: "Modern"
            ),
            TemplateInfo(
                id: "3",
                name: "Creative",
                description: "Bold and creative template for creative professionals",
                preview_url: "https://example.com/creative.png",
                npm_package: "jsonresume-theme-creative",
                version: "1.0.0",
                author: "JSON Resume",
                category: "Creative"
            )
        ]
    }
    
    static func mockResumeCompleteness() -> ResumeCompletenessSummary {
        return ResumeCompletenessSummary(
            personal_details: "complete",
            work_experience: "incomplete",
            education: "complete",
            skills: "partial",
            projects: "not_started",
            certifications: "not_started",
            languages: "not_started",
            interests: "not_started",
            conversation_context: [:],
            suggested_topics: ["Tell me about your work experience", "What skills do you have?"],
            missing_critical_info: ["Work experience details"],
            conversation_flow_hints: ["Ask about specific job responsibilities"],
            user_progress_insights: [:]
        )
    }
} 