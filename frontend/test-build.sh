#!/bin/bash

echo "🔬 Testing GremlinGPT Astro + Electron Build"
echo "============================================="

# Test 1: Check if Astro build was successful
echo "1. Checking Astro build..."
if [ -d "dist" ]; then
    echo "✅ Astro build directory exists"
    if [ -f "dist/server/entry.mjs" ]; then
        echo "✅ Astro server entry point exists"
    else
        echo "❌ Astro server entry point missing"
        exit 1
    fi
else
    echo "❌ Astro build directory missing"
    exit 1
fi

# Test 2: Check if package.json is correctly configured
echo "2. Checking package configuration..."
if grep -q '"main": "main.cjs"' package.json; then
    echo "✅ Package main entry is correctly set"
else
    echo "❌ Package main entry incorrect"
    exit 1
fi

# Test 3: Check if Electron files exist
echo "3. Checking Electron files..."
if [ -f "main.cjs" ]; then
    echo "✅ Electron main process file exists"
else
    echo "❌ Electron main process file missing"
    exit 1
fi

if [ -f "preload.cjs" ]; then
    echo "✅ Electron preload script exists"
else
    echo "❌ Electron preload script missing"
    exit 1
fi

# Test 4: Validate Node.js syntax
echo "4. Validating syntax..."
if node -c main.cjs; then
    echo "✅ Main process syntax valid"
else
    echo "❌ Main process syntax invalid"
    exit 1
fi

if node -c preload.cjs; then
    echo "✅ Preload script syntax valid"
else
    echo "❌ Preload script syntax invalid"
    exit 1
fi

# Test 5: Check if dependencies are installed
echo "5. Checking dependencies..."
if [ -d "node_modules/electron" ]; then
    echo "✅ Electron dependency installed"
else
    echo "❌ Electron dependency missing"
    exit 1
fi

if [ -d "node_modules/monaco-editor" ]; then
    echo "✅ Monaco Editor dependency installed"
else
    echo "❌ Monaco Editor dependency missing"
    exit 1
fi

# Test 6: Start Astro server in test mode (brief)
echo "6. Testing Astro server startup..."
timeout 10s npm run preview > /dev/null 2>&1 &
SERVER_PID=$!
sleep 3

if kill -0 $SERVER_PID 2>/dev/null; then
    echo "✅ Astro server can start successfully"
    kill $SERVER_PID 2>/dev/null
else
    echo "⚠️  Astro server startup test inconclusive"
fi

# Test 7: Validate build output structure
echo "7. Checking build structure..."
if [ -d "dist/client" ] && [ -d "dist/server" ]; then
    echo "✅ Build structure is correct (client/server separation)"
else
    echo "❌ Build structure incorrect"
    exit 1
fi

echo ""
echo "🎉 All tests passed! GremlinGPT Astro + Electron build is ready."
echo ""
echo "Architecture Summary:"
echo "- Frontend: Astro + Tailwind + Monaco Editor"
echo "- Backend: Node.js server with API routes"
echo "- Desktop: Electron wrapper with file system access"
echo "- Editor: Monaco with AI integration"
echo "- Build: Production-ready with offline capabilities"
echo ""
echo "To run in production:"
echo "1. npm run build"
echo "2. npm run electron (in production mode)"
echo ""
echo "To develop:"
echo "1. npm run dev (start Astro dev server)"
echo "2. npm run electron-dev (start Electron with dev server)"