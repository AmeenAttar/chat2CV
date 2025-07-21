// API Service for Chat-to-CV iOS App
// Handles all communication with the backend

import Foundation

class APIService: ObservableObject {
    static let shared = APIService()
    
    // MARK: - Configuration
    private let baseURL = "http://localhost:8000"
    private let session = URLSession.shared
    
    init() {}
    
    // MARK: - Generic Request Helper
    private func makeRequest<T: Codable>(_ request: URLRequest) async throws -> T {
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError(detail: "Invalid response", status_code: nil)
        }
        
        guard httpResponse.statusCode == 200 else {
            throw APIError(detail: "HTTP \(httpResponse.statusCode)", status_code: httpResponse.statusCode)
        }
        
        return try JSONDecoder().decode(T.self, from: data)
    }
    
    // MARK: - Template Endpoints
    func getTemplates() async throws -> [TemplateInfo] {
        guard let url = URL(string: "\(baseURL)/templates") else {
            throw APIError(detail: "Invalid URL", status_code: nil)
        }
        
        let request = URLRequest(url: url)
        let templates: [TemplateInfo] = try await makeRequest(request)
        
        // Convert relative preview URLs to absolute URLs
        return templates.map { template in
            if let relativeUrl = template.preview_url {
                return TemplateInfo(
                    id: template.id,
                    name: template.name,
                    description: template.description,
                    preview_url: "\(baseURL)\(relativeUrl)",
                    npm_package: template.npm_package,
                    version: template.version,
                    author: template.author,
                    category: template.category
                )
            } else {
                return template
            }
        }
    }
    
    // MARK: - Resume Generation Endpoints
    func generateResumeSection(_ request: GenerateResumeSectionRequest) async throws -> GenerateResumeSectionResponse {
        guard let url = URL(string: "\(baseURL)/generate-resume-section") else {
            throw APIError(detail: "Invalid URL", status_code: nil)
        }
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            urlRequest.httpBody = try JSONEncoder().encode(request)
        } catch {
            throw APIError(detail: "Failed to encode request", status_code: nil)
        }
        
        return try await makeRequest(urlRequest)
    }
    
    // MARK: - Resume Data Endpoints
    func getResume(userId: String) async throws -> ResumeData {
        guard let url = URL(string: "\(baseURL)/resume/\(userId)") else {
            throw APIError(detail: "Invalid URL", status_code: nil)
        }
        
        let request = URLRequest(url: url)
        return try await makeRequest(request)
    }
    
    func getResumeHTML(userId: String, theme: String = "professional") async throws -> String {
        guard let url = URL(string: "\(baseURL)/resume/\(userId)/html?theme=\(theme)") else {
            throw APIError(detail: "Invalid URL", status_code: nil)
        }
        
        let request = URLRequest(url: url)
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError(detail: "Invalid response", status_code: nil)
        }
        
        guard httpResponse.statusCode == 200 else {
            throw APIError(detail: "HTTP \(httpResponse.statusCode)", status_code: httpResponse.statusCode)
        }
        
        return String(data: data, encoding: .utf8) ?? ""
    }
    
    // MARK: - Resume Management Endpoints
    func createResume(_ request: CreateResumeRequest) async throws -> ResumeData {
        guard let url = URL(string: "\(baseURL)/resumes") else {
            throw APIError(detail: "Invalid URL", status_code: nil)
        }
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            urlRequest.httpBody = try JSONEncoder().encode(request)
        } catch {
            throw APIError(detail: "Failed to encode request", status_code: nil)
        }
        
        return try await makeRequest(urlRequest)
    }
    
    func getUserResumes(email: String) async throws -> [ResumeData] {
        guard let url = URL(string: "\(baseURL)/resumes/\(email)") else {
            throw APIError(detail: "Invalid URL", status_code: nil)
        }
        
        let request = URLRequest(url: url)
        return try await makeRequest(request)
    }
    
    // MARK: - Health Check
    func healthCheck() async throws -> HealthResponse {
        guard let url = URL(string: "\(baseURL)/health") else {
            throw APIError(detail: "Invalid URL", status_code: nil)
        }
        
        let request = URLRequest(url: url)
        return try await makeRequest(request)
    }
    
    func getHealth() async throws -> HealthResponse {
        return try await healthCheck()
    }
    
    // MARK: - Helper Methods
    func getTemplateIdAsInt(_ templateId: String) -> Int {
        return Int(templateId) ?? 1
    }
}

// MARK: - Error Types
struct APIError: Error, LocalizedError {
    let detail: String
    let status_code: Int?
    
    var errorDescription: String? {
        return detail
    }
}

struct HealthResponse: Codable {
    let status: String
    let timestamp: String
    let version: String?
    
    enum CodingKeys: String, CodingKey {
        case status, timestamp, version
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        status = try container.decode(String.self, forKey: .status)
        timestamp = try container.decode(String.self, forKey: .timestamp)
        version = try container.decodeIfPresent(String.self, forKey: .version)
    }
    
    init(status: String, timestamp: String) {
        self.status = status
        self.timestamp = timestamp
        self.version = nil
    }
} 