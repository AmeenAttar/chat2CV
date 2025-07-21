import SwiftUI

struct TemplateSelectionView: View {
    @StateObject private var viewModel = TemplateSelectionViewModel()
    
    var body: some View {
        NavigationView {
            List(viewModel.templates) { template in
                TemplateRowView(template: template)
            }
            .navigationTitle("Choose Template")
            .onAppear {
                viewModel.loadTemplates()
            }
        }
    }
}

struct TemplateRowView: View {
    let template: TemplateInfo
    
    var body: some View {
        VStack(alignment: .leading) {
            Text(template.name)
                .font(.headline)
            Text(template.description)
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
        .padding(.vertical, 8)
    }
}

struct TemplateSelectionView_Previews: PreviewProvider {
    static var previews: some View {
        TemplateSelectionView()
    }
}
