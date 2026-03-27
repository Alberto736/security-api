# Aquiles Security API - N8N Integration Guide

## 🚀 **SIMPLE WORKFLOW FOR VULNERABILITY SCANNING**

### **📋 Workflow Overview:**
```
1. Webhook Trigger → 2. Call Security API → 3. Check Vulnerabilities → 4a. Send Slack Alert (if found) → 5a. Success Response
                                                              ↓
                                                              4b. No Vulnerabilities Response (if none)
```

---

## 🔧 **SETUP INSTRUCTIONS**

### **1. Import Workflow to N8N:**
```bash
1. Open N8N (http://localhost:5678)
2. Click "Import from file"
3. Select: n8n-workflows/aquiles-security-api-workflow.json
4. Click "Import"
```

### **2. Configure API Connection:**
```bash
✅ URL: http://localhost:3000/inventario
✅ Method: POST
✅ Headers: 
   - Content-Type: application/json
   - X-API-Key: test_api_key
✅ Timeout: 10 seconds
```

### **3. Configure Slack Integration (Optional):**
```bash
✅ Replace: https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
✅ With your actual Slack webhook URL
✅ Customize message format as needed
```

---

## 🧪 **TESTING THE WORKFLOW**

### **Test Data Example:**
```json
{
  "repo": "test-repo",
  "dependencias": [
    {
      "name": "requests",
      "version": "2.32.0",
      "ecosystem": "pip"
    },
    {
      "name": "flask",
      "version": "2.3.0",
      "ecosystem": "pip"
    }
  ]
}
```

### **How to Test:**
```bash
1. Start the workflow in N8N
2. Copy the webhook URL from N8N
3. Send POST request with test data:
   curl -X POST "N8N_WEBHOOK_URL" \
     -H "Content-Type: application/json" \
     -d '{"repo":"test-repo","dependencias":[{"name":"requests","version":"2.32.0","ecosystem":"pip"}]}'
4. Check N8N execution log
5. Verify API response and Slack notification (if configured)
```

---

## 📊 **WORKFLOW FEATURES**

### **✅ Core Functionality:**
```bash
🎯 **HTTP Webhook Trigger** - Receives inventory data
🎯 **Security API Integration** - Calls /inventario endpoint
🎯 **Vulnerability Detection** - Checks if alerts found
🎯 **Conditional Logic** - Different paths for found/not found
🎯 **Slack Notifications** - Alert when vulnerabilities found
🎯 **Webhook Responses** - Returns status to caller
```

### **✅ Error Handling:**
```bash
🛡️ **API Timeouts** - 10 second timeout
🛡️ **Authentication** - Uses API key header
🛡️ **Response Validation** - Checks vulnerability count
🛡️ **Graceful Fallbacks** - Handles no vulnerabilities case
```

---

## 🔧 **CUSTOMIZATION OPTIONS**

### **1. API Configuration:**
```json
{
  "url": "http://localhost:3000/inventario",
  "authentication": "headerAuth",
  "headerAuth": {
    "name": "X-API-Key",
    "value": "YOUR_ACTUAL_API_KEY"
  }
}
```

### **2. Slack Message Customization:**
```json
{
  "text": "🚨 *Vulnerability Alert!*\n\n*Repository*: {{ $json.repo }}\n*Vulnerabilities Found*: {{ $json.alertas_encontradas }}\n*Details*: {{ $json.detalle }}\n\n🔗 *API*: Aquiles Security API\n📅 *Date*: {{ $now }}",
  "username": "Aquiles Security Scanner",
  "icon_emoji": ":shield:"
}
```

### **3. Response Format:**
```json
{
  "status": "success",
  "message": "Security scan completed for {{ $json.repo }}",
  "vulnerabilities_found": {{ $json.alertas_encontradas }},
  "timestamp": "{{ $now }}"
}
```

---

## 🚀 **PRODUCTION DEPLOYMENT**

### **1. Update API URL:**
```bash
# Replace localhost with your ngrok URL:
"url": "https://your-ngrok-url.ngrok.io/inventario"
```

### **2. Secure API Key:**
```bash
# Use environment variables or N8N credentials:
"value": "={{ $credentials.apiKey.apiKey }}"
```

### **3. Enhanced Error Handling:**
```bash
# Add error nodes for:
- API connection failures
- Invalid response format
- Slack webhook failures
- Timeout handling
```

---

## 📱 **MOBILE TESTING**

### **Test with Postman/Insomnia:**
```bash
1. Method: POST
2. URL: N8N_WEBHOOK_URL
3. Headers: Content-Type: application/json
4. Body: Raw JSON with test data
5. Send and check response
```

### **Test with curl:**
```bash
curl -X POST "YOUR_N8N_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "repo": "mobile-test",
    "dependencias": [
      {"name": "axios", "version": "1.6.0", "ecosystem": "pip"}
    ]
  }'
```

---

## 🎯 **NEXT STEPS**

### **Enhancements to Add:**
```bash
🔹 **Email Notifications** - Add SMTP node for email alerts
🔹 **Database Storage** - Store scan results in database
🔹 **Scheduled Scans** - Add cron trigger for periodic scans
🔹 **Dashboard Integration** - Send results to monitoring dashboard
🔹 **Multi-repo Support** - Batch processing for multiple repos
```

---

## 🏆 **SUCCESS METRICS**

### **What to Monitor:**
```bash
📊 **Scan Success Rate** - % of successful API calls
📊 **Vulnerability Detection** - Number of alerts found
📊 **Response Time** - Average scan duration
📊 **Notification Delivery** - Slack/email success rate
📊 **Error Rate** - Failed scans and reasons
```

---

## 🛡️ **SECURITY CONSIDERATIONS**

### **Best Practices:**
```bash
🔒 **API Key Protection** - Use N8N credentials, not hardcoded
🔒 **Webhook Security** - Validate incoming data
🔒 **Rate Limiting** - Respect API rate limits
🔒 **Data Sanitization** - Clean input before processing
🔒 **Audit Logging** - Log all scan activities
```

---

## 🚀 **READY TO USE**

### **Your Simple N8N Workflow:**
```bash
✅ File: n8n-workflows/aquiles-security-api-workflow.json
✅ Nodes: 6 (Webhook, API Call, IF, Slack, 2 Responses)
✅ Logic: Vulnerability detection with notifications
✅ Integration: Full Aquiles Security API connection
✅ Testing: Ready for immediate use
```

**Import this workflow into N8N and start scanning! 🛡️**
