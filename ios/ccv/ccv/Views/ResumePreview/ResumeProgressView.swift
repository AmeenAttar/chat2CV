import SwiftUI

struct ResumeProgressView: View {
    let completenessSummary: ResumeCompletenessSummary
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Resume Progress")
                    .font(.headline)
                Spacer()
                Text("\(Int(completenessSummary.completionPercentage))%")
                    .font(.subheadline)
                    .foregroundColor(.blue)
            }
            
            ProgressView(value: completenessSummary.completionPercentage, total: 100)
                .progressViewStyle(LinearProgressViewStyle(tint: .blue))
            
            // Section status
            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: 8) {
                SectionStatusRow(title: "Personal Details", status: completenessSummary.personal_details)
                SectionStatusRow(title: "Work Experience", status: completenessSummary.work_experience)
                SectionStatusRow(title: "Education", status: completenessSummary.education)
                SectionStatusRow(title: "Skills", status: completenessSummary.skills)
                SectionStatusRow(title: "Projects", status: completenessSummary.projects)
                SectionStatusRow(title: "Certifications", status: completenessSummary.certifications)
            }
            
            // Next suggestion
            if let nextTopic = completenessSummary.nextSuggestedTopic {
                HStack {
                    Image(systemName: "lightbulb.fill")
                        .foregroundColor(.yellow)
                    Text("Next: \(nextTopic)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding(.top, 4)
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
}

struct SectionStatusRow: View {
    let title: String
    let status: String
    
    var statusColor: Color {
        switch status {
        case "complete":
            return .green
        case "partial":
            return .orange
        case "incomplete":
            return .red
        default:
            return .gray
        }
    }
    
    var statusIcon: String {
        switch status {
        case "complete":
            return "checkmark.circle.fill"
        case "partial":
            return "minus.circle.fill"
        case "incomplete":
            return "xmark.circle.fill"
        default:
            return "circle"
        }
    }
    
    var body: some View {
        HStack {
            Image(systemName: statusIcon)
                .foregroundColor(statusColor)
                .font(.caption)
            
            Text(title)
                .font(.caption)
                .foregroundColor(.primary)
            
            Spacer()
        }
    }
}

#Preview {
    ResumeProgressView(completenessSummary: ResumeCompletenessSummary(
        personal_details: "complete",
        work_experience: "partial",
        education: "incomplete",
        skills: "complete",
        projects: "not_started",
        certifications: "not_started",
        languages: "not_started",
        interests: "not_started",
        conversation_context: [:],
        suggested_topics: ["Add your education details"],
        missing_critical_info: ["education"],
        conversation_flow_hints: ["user_is_engaged"],
        user_progress_insights: [:]
    ))
} 