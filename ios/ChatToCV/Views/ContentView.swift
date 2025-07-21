import SwiftUI

struct ContentView: View {
    var body: some View {
        TabView {
            TemplateSelectionView()
                .tabItem {
                    Image(systemName: "doc.text")
                    Text("Templates")
                }
            
            ChatView()
                .tabItem {
                    Image(systemName: "message")
                    Text("Chat")
                }
            
            ResumePreviewView()
                .tabItem {
                    Image(systemName: "eye")
                    Text("Preview")
                }
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
