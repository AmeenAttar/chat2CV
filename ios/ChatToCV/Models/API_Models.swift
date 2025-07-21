// API Models for Chat-to-CV iOS App
// These models match the backend API responses

import Foundation

// MARK: - Template Models
struct TemplateInfo: Codable, Identifiable {
    let id: String
    let name: String
    let description: String
    let preview_url: String?
    let npm_package: String?
    let version: String?
    let author: String?
    let category: String?
}

// MARK: - Resume Generation Models
struct GenerateResumeSectionRequest: Codable {
    let template_id: Int
    let section_name: String
    let raw_input: String
    let user_id: String
    let resume_id: Int?
}

struct GenerateResumeSectionResponse: Codable {
    let status: String
    let updated_section: String
    let rephrased_content: String
    let resume_completeness_summary: ResumeCompletenessSummary
    let validation_issues: [String]?
}

// MARK: - Resume Data Models
struct ResumeCompletenessSummary: Codable {
    let personal_details: String
    let work_experience: String
    let education: String
    let skills: String
    let projects: String
    let certifications: String
    let languages: String
    let interests: String
    
    let conversation_context: [String: Any]
    let suggested_topics: [String]
    let missing_critical_info: [String]
    let conversation_flow_hints: [String]
    let user_progress_insights: [String: Any]
    
    enum CodingKeys: String, CodingKey {
        case personal_details, work_experience, education, skills, projects
        case certifications, languages, interests, conversation_context
        case suggested_topics, missing_critical_info, conversation_flow_hints
        case user_progress_insights
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        personal_details = try container.decode(String.self, forKey: .personal_details)
        work_experience = try container.decode(String.self, forKey: .work_experience)
        education = try container.decode(String.self, forKey: .education)
        skills = try container.decode(String.self, forKey: .skills)
        projects = try container.decode(String.self, forKey: .projects)
        certifications = try container.decode(String.self, forKey: .certifications)
        languages = try container.decode(String.self, forKey: .languages)
        interests = try container.decode(String.self, forKey: .interests)
        
        conversation_context = try container.decode([String: Any].self, forKey: .conversation_context)
        suggested_topics = try container.decode([String].self, forKey: .suggested_topics)
        missing_critical_info = try container.decode([String].self, forKey: .missing_critical_info)
        conversation_flow_hints = try container.decode([String].self, forKey: .conversation_flow_hints)
        user_progress_insights = try container.decode([String: Any].self, forKey: .user_progress_insights)
    }
}

// MARK: - JSON Resume Models
struct JSONResume: Codable {
    let schema: String?
    let basics: Basics?
    let work: [WorkExperience]?
    let volunteer: [Volunteer]?
    let education: [Education]?
    let awards: [Award]?
    let publications: [Publication]?
    let skills: [Skill]?
    let languages: [Language]?
    let interests: [Interest]?
    let references: [Reference]?
    let projects: [Project]?
    let meta: Meta?
}

struct Basics: Codable {
    let name: String?
    let label: String?
    let image: String?
    let email: String?
    let phone: String?
    let url: String?
    let summary: String?
    let location: Location?
    let profiles: [Profile]?
}

struct Location: Codable {
    let address: String?
    let postalCode: String?
    let city: String?
    let countryCode: String?
    let region: String?
}

struct Profile: Codable {
    let network: String
    let username: String
    let url: String?
}

struct WorkExperience: Codable {
    let name: String
    let position: String
    let url: String?
    let startDate: String?
    let endDate: String?
    let summary: String?
    let highlights: [String]?
    let location: String?
    let description: String?
}

struct Education: Codable {
    let institution: String
    let url: String?
    let area: String?
    let studyType: String?
    let startDate: String?
    let endDate: String?
    let score: String?
    let courses: [String]?
}

struct Skill: Codable {
    let name: String
    let level: String?
    let keywords: [String]?
}

struct Language: Codable {
    let language: String
    let fluency: String?
}

struct Interest: Codable {
    let name: String
    let keywords: [String]?
}

struct Project: Codable {
    let name: String
    let description: String?
    let highlights: [String]?
    let keywords: [String]?
    let startDate: String?
    let endDate: String?
    let url: String?
    let roles: [String]?
    let entity: String?
    let type: String?
}

struct Award: Codable {
    let title: String
    let date: String?
    let awarder: String?
    let summary: String?
}

struct Publication: Codable {
    let name: String
    let publisher: String?
    let releaseDate: String?
    let url: String?
    let summary: String?
}

struct Volunteer: Codable {
    let organization: String
    let position: String
    let url: String?
    let startDate: String?
    let endDate: String?
    let summary: String?
    let highlights: [String]?
}

struct Reference: Codable {
    let name: String
    let reference: String
}

struct Meta: Codable {
    let canonical: String?
    let version: String?
    let lastModified: String?
}

// MARK: - API Error Models
struct APIError: Codable, Error {
    let detail: String
    let status_code: Int?
}

// MARK: - User Models
struct User: Codable, Identifiable {
    let id: Int
    let email: String
    let name: String?
    let is_active: Bool
    let created_at: String
    let updated_at: String
}

struct CreateResumeRequest: Codable {
    let template_id: Int
    let title: String?
    let user_email: String
}

// MARK: - Extensions for convenience
extension ResumeCompletenessSummary {
    var completionPercentage: Double {
        let sections = [personal_details, work_experience, education, skills, projects, certifications, languages, interests]
        let completed = sections.filter { $0 == "complete" }.count
        return Double(completed) / Double(sections.count) * 100
    }
    
    var nextSuggestedTopic: String? {
        return suggested_topics.first
    }
    
    var hasCriticalMissingInfo: Bool {
        return !missing_critical_info.isEmpty
    }
} 