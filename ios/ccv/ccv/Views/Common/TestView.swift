import SwiftUI

struct TestView: View {
    @State private var healthStatus = "Testing..."
    @State private var templatesCount = 0
    @State private var isLoading = false
    @State private var testResults: [String: String] = [:]
    
    private let apiService = APIService.shared
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Text("API Connection Test")
                    .font(.title)
                    .fontWeight(.bold)
                
                ScrollView {
                    VStack(alignment: .leading, spacing: 10) {
                        TestResultRow(title: "Backend Health", result: testResults["health"] ?? "Testing...")
                        TestResultRow(title: "Templates Available", result: testResults["templates"] ?? "Testing...")
                        TestResultRow(title: "Resume Generation", result: testResults["generation"] ?? "Testing...")
                    }
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(10)
                }
                
                Button("Run All Tests") {
                    runAllTests()
                }
                .buttonStyle(.borderedProminent)
                .disabled(isLoading)
                
                if isLoading {
                    ProgressView()
                }
                
                Spacer()
            }
            .padding()
            .navigationTitle("API Test")
            .navigationBarTitleDisplayMode(.large)
            .onAppear {
                runAllTests()
            }
        }
    }
    
    private func runAllTests() {
        isLoading = true
        testResults.removeAll()
        
        Task {
            // Test 1: Health Check
            await testHealth()
            
            // Test 2: Templates
            await testTemplates()
            
            // Test 3: Resume Generation
            await testResumeGeneration()
            
            await MainActor.run {
                isLoading = false
            }
        }
    }
    
    private func testHealth() async {
        do {
            let health = try await apiService.getHealth()
            await MainActor.run {
                testResults["health"] = "✅ \(health.status)"
            }
        } catch {
            await MainActor.run {
                testResults["health"] = "❌ \(error.localizedDescription)"
            }
        }
    }
    
    private func testTemplates() async {
        do {
            let templates = try await apiService.getTemplates()
            await MainActor.run {
                testResults["templates"] = "✅ \(templates.count) templates found"
            }
        } catch {
            await MainActor.run {
                testResults["templates"] = "❌ \(error.localizedDescription)"
            }
        }
    }
    
    private func testResumeGeneration() async {
        do {
            let request = GenerateResumeSectionRequest(
                template_id: 1,
                section_name: "work_experience",
                raw_input: "I worked as a software engineer at Google for 2 years",
                user_id: "test@example.com",
                resume_id: nil
            )
            
            let response = try await apiService.generateResumeSection(request)
            await MainActor.run {
                testResults["generation"] = "✅ Generated: \(response.rephrased_content.prefix(50))..."
            }
        } catch {
            await MainActor.run {
                testResults["generation"] = "❌ \(error.localizedDescription)"
            }
        }
    }
}

struct TestResultRow: View {
    let title: String
    let result: String
    
    var body: some View {
        HStack {
            Text(title)
                .fontWeight(.medium)
            Spacer()
            Text(result)
                .foregroundColor(result.contains("✅") ? .green : result.contains("❌") ? .red : .blue)
                .font(.caption)
                .multilineTextAlignment(.trailing)
        }
    }
}

#Preview {
    TestView()
} 