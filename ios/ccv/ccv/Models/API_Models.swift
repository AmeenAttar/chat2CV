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
struct ResumeData: Codable {
    let user_id: String
    let template_id: Int
    let json_resume: JSONResume
    let sections: [String: ResumeSection]
    let completeness_summary: ResumeCompletenessSummary
    let created_at: String?
    let updated_at: String?
}

struct ResumeSection: Codable {
    let name: String
    let content: [String]
    let status: String
    let last_updated: String?
}

struct ResumeCompletenessSummary: Codable {
    let personal_details: String
    let work_experience: String
    let education: String
    let skills: String
    let projects: String
    let certifications: String
    let languages: String
    let interests: String
    
    let conversation_context: [String: String]
    let suggested_topics: [String]
    let missing_critical_info: [String]
    let conversation_flow_hints: [String]
    let user_progress_insights: [String: String]
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

// MARK: - Resume Management Models
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