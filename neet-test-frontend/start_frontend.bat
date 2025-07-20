@echo off
echo 🚀 Starting NEET Test Frontend...
echo.
echo Frontend URL: http://localhost:3000
echo Backend URL: http://localhost:5000
echo.
echo Make sure backend is running on port 5000!
echo.

REM Kill any existing Node.js processes
taskkill /f /im node.exe >nul 2>&1

cd "c:\Program Files\BizFlow\QA\neet-test-frontend"
npm run dev
