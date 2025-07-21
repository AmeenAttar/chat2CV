#!/bin/bash

echo "🎨 Regenerating template previews..."

# Make sure we're in the right directory
cd "$(dirname "$0")"

# Run the Node.js script
node generate_template_previews.js

echo "✅ Template previews regenerated!"
echo "📁 Check static/templates/ for the new preview images" 