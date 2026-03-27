@echo off
REM Test Script for Aquiles Security API + N8N Integration (Windows)
REM Usage: test-workflow.bat

echo 🚀 Testing Aquiles Security API + N8N Integration
echo ================================================

REM Configuration
set N8N_WEBHOOK_URL=http://localhost:5678/webhook/security-scan
set API_BASE_URL=http://localhost:3000

echo 📋 Configuration:
echo   N8N Webhook URL: %N8N_WEBHOOK_URL%
echo   API Base URL: %API_BASE_URL%
echo.

REM Test 1: Check API Health
echo 🔍 Test 1: Checking API Health...
curl -s "%API_BASE_URL%/health/simple"
echo.

REM Test 2: Test with Vulnerabilities
echo 🔍 Test 2: Testing with Vulnerabilities...
set VULN_DATA={"repo": "test-vulnerable-repo","dependencias": [{"name": "requests","version": "2.25.0","ecosystem": "pip"},{"name": "urllib3","version": "1.24.0","ecosystem": "pip"}]}

echo Sending data to N8N workflow...
curl -X POST "%N8N_WEBHOOK_URL%" -H "Content-Type: application/json" -d "%VULN_DATA%" -w "Response Time: %%{time_total}s HTTP Code: %%{http_code}%%n"
echo.

REM Test 3: Test without Vulnerabilities
echo 🔍 Test 3: Testing without Vulnerabilities...
set SAFE_DATA={"repo": "test-safe-repo","dependencias": [{"name": "requests","version": "2.32.0","ecosystem": "pip"}]}

echo Sending safe data to N8N workflow...
curl -X POST "%N8N_WEBHOOK_URL%" -H "Content-Type: application/json" -d "%SAFE_DATA%" -w "Response Time: %%{time_total}s HTTP Code: %%{http_code}%%n"
echo.

REM Test 4: Test Edge Cases
echo 🔍 Test 4: Testing Edge Cases...
set EMPTY_DATA={"repo": "empty-test","dependencias": []}

echo Sending empty dependencies...
curl -X POST "%N8N_WEBHOOK_URL%" -H "Content-Type: application/json" -d "%EMPTY_DATA%" -w "Response Time: %%{time_total}s HTTP Code: %%{http_code}%%n"
echo.

echo ✅ All tests completed!
echo 📊 Check N8N execution logs for detailed results
echo 🔗 N8N Interface: http://localhost:5678
pause
