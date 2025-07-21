//
//  ContentView.swift
//  ccv
//
//  Created by Ameen Attar on 7/20/25.
//

import SwiftUI

struct ContentView: View {
    @State private var selectedTab = 0
    @State private var selectedTemplate: TemplateInfo?
    
    var body: some View {
        TabView(selection: $selectedTab) {
            TemplateSelectionView()
                .tabItem {
                    Image(systemName: "doc.text")
                    Text("Templates")
                }
                .tag(0)
            
            ChatView(selectedTemplate: selectedTemplate)
                .tabItem {
                    Image(systemName: "message")
                    Text("Chat")
                }
                .tag(1)
            
            ResumePreviewView()
                .tabItem {
                    Image(systemName: "eye")
                    Text("Preview")
                }
                .tag(2)
            
            TestView()
                .tabItem {
                    Image(systemName: "wrench.and.screwdriver")
                    Text("Test")
                }
                .tag(3)
        }
        .onReceive(NotificationCenter.default.publisher(for: .templateSelected)) { notification in
            if let template = notification.object as? TemplateInfo {
                selectedTemplate = template
                selectedTab = 1 // Switch to chat tab
            }
        }
        .onReceive(NotificationCenter.default.publisher(for: .switchToChat)) { _ in
            selectedTab = 1 // Switch to chat tab
        }
    }
}

// MARK: - Notification Extension
extension Notification.Name {
    static let templateSelected = Notification.Name("templateSelected")
    static let resumeUpdated = Notification.Name("resumeUpdated")
    static let switchToChat = Notification.Name("switchToChat")
}

#Preview {
    ContentView()
}
