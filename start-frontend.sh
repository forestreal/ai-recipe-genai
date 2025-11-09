#!/bin/bash
# Script to start the frontend server

echo "🚀 Starting Frontend Server..."
echo ""

cd "$(dirname "$0")/frontend"

# Check if port 5173 is already in use
if lsof -i :5173 > /dev/null 2>&1; then
    echo "⚠️  Port 5173 is already in use"
    echo "   Either stop the existing server or use a different port"
    echo ""
    read -p "Use a different port? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter port number (default: 5174): " PORT
        PORT=${PORT:-5174}
    else
        echo "Exiting..."
        exit 1
    fi
else
    PORT=5173
fi

echo "📦 Starting Python HTTP server on port $PORT..."
echo ""
echo "✅ Frontend server starting..."
echo ""
echo "📋 Access the application at:"
echo "   - Diagnosis: http://localhost:$PORT/diagnosis.html"
echo "   - Flavor: http://localhost:$PORT/flavor.html"
echo "   - Recipe: http://localhost:$PORT/recipe.html"
echo "   - Index: http://localhost:$PORT/index.html"
echo ""
echo "🌐 Make sure the backend API is running on http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 -m http.server $PORT

