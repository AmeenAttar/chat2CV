import SwiftUI

struct TemplateSelectionView: View {
    @StateObject private var viewModel = TemplateSelectionViewModel()
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                if viewModel.isLoading {
                    Spacer()
                    ProgressView("Loading templates...")
                    Spacer()
                } else if let error = viewModel.errorMessage {
                    Spacer()
                    VStack {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.largeTitle)
                            .foregroundColor(.orange)
                        Text("Error loading templates")
                            .font(.headline)
                        Text(error)
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                        Button("Retry") {
                            viewModel.loadTemplates()
                        }
                        .buttonStyle(.borderedProminent)
                    }
                    .padding()
                    Spacer()
                } else {
                    ScrollView {
                        LazyVGrid(columns: [
                            GridItem(.flexible()),
                            GridItem(.flexible())
                        ], spacing: 16) {
                            ForEach(viewModel.templates, id: \.id) { template in
                                TemplateCard(template: template) {
                                    viewModel.selectTemplate(template)
                                }
                            }
                        }
                        .padding()
                    }
                }
            }
            .navigationTitle("Choose Template")
            .navigationBarTitleDisplayMode(.large)
        }
        .onChange(of: viewModel.shouldNavigateToChat) { _, shouldNavigate in
            if shouldNavigate, let template = viewModel.selectedTemplate, let sessionId = viewModel.sessionId {
                NotificationCenter.default.post(
                    name: .templateSelected,
                    object: ["template": template, "sessionId": sessionId]
                )
                viewModel.shouldNavigateToChat = false
            }
        }
    }
}

struct TemplateCard: View {
    let template: TemplateInfo
    let onSelect: () -> Void
    
    var body: some View {
        Button(action: onSelect) {
            VStack(alignment: .leading, spacing: 8) {
                if let previewUrl = template.preview_url {
                    AsyncImage(url: URL(string: previewUrl)) { image in
                        image
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                    } placeholder: {
                        Rectangle()
                            .fill(Color.gray.opacity(0.3))
                            .overlay(
                                Image(systemName: "doc.text")
                                    .font(.largeTitle)
                                    .foregroundColor(.gray)
                            )
                    }
                    .frame(height: 140)
                    .clipped()
                    .cornerRadius(8)
                } else {
                    Rectangle()
                        .fill(Color.gray.opacity(0.3))
                        .frame(height: 140)
                        .overlay(
                            Image(systemName: "doc.text")
                                .font(.largeTitle)
                                .foregroundColor(.gray)
                        )
                        .cornerRadius(8)
                }
                
                Text(template.name)
                    .font(.headline)
                    .foregroundColor(.primary)
                    .lineLimit(1)
                
                Text(template.description)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .lineLimit(3)
                    .multilineTextAlignment(.leading)
            }
            .padding()
            .frame(maxWidth: .infinity)
            .background(Color(.systemBackground))
            .cornerRadius(12)
            .shadow(radius: 2)
        }
        .buttonStyle(PlainButtonStyle())
    }
}

#Preview {
    TemplateSelectionView()
} 