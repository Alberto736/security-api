# 🌐 **CONFIGURACIÓN N8N WEB EMPRESA - INSTRUCCIONES**

## 🚀 **IMPORTAR WORKFLOW EN N8N WEB**

### **✅ PASO 1: Acceder a N8N Web Empresa**
```bash
🔗 URL: [URL de tu N8N web empresa]
👤 Login: Con tus credenciales de empresa
🏠 Dashboard: Verás tus workflows existentes
```

### **✅ PASO 2: Importar el Workflow**
```bash
1️⃣ Click "Import from file" o "Import workflow"
2️⃣ Seleccionar archivo: aquiles-workflow-n8n-web.json
3️⃣ Click "Import"
4️⃣ Workflow aparecerá como: "Aquiles Security API - Simple Vulnerability Scanner"
```

---

## 🔧 **CONFIGURACIÓN REQUERIDA**

### **✅ 1. Actualizar URL de API (IMPORTANTE)**
```bash
🔧 En el nodo "Call Security API":
📍 Linea 22: "url": "https://your-ngrok-url.ngrok.io/inventario"

🔄 Reemplazar "your-ngrok-url.ngrok.io" con:
   - Tu URL de ngrok si usas tunneling
   - O la URL pública de tu API si está desplegada
```

### **✅ 2. Configurar API Key (Opcional)**
```bash
🔧 En el nodo "Call Security API":
📍 Linea 27: "value": "test_api_key"

🔄 Reemplazar con tu API key real:
   - Si usas la API key de producción
   - O mantener "test_api_key" para desarrollo
```

### **✅ 3. Configurar Slack (Opcional)**
```bash
🔧 En el nodo "Send Slack Alert":
📍 Linea 61: "url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"

🔄 Reemplazar con tu webhook real de Slack
🔹 Si no tienes Slack, puedes desactivar este nodo
```

---

## 🧪 **PROBAR EL WORKFLOW**

### **✅ 1. Activar el Workflow**
```bash
1️⃣ Seleccionar el workflow importado
2️⃣ Click "Activate" o el botón ▶️
3️⃣ El workflow quedará activo y escuchará peticiones
```

### **✅ 2. Obtener URL del Webhook**
```bash
🔗 El workflow mostrará una URL como:
   https://your-n8n-domain.com/webhook/security-scan

📋 Copiar esta URL para las pruebas
```

### **✅ 3. Probar con curl/Postman**
```bash
# Test con curl
curl -X POST "https://your-n8n-domain.com/webhook/security-scan" \
  -H "Content-Type: application/json" \
  -d '{
    "repo": "test-repo",
    "dependencias": [
      {"name": "requests", "version": "2.32.0", "ecosystem": "pip"}
    ]
  }'
```

---

## 📊 **VERIFICACIÓN DE FUNCIONAMIENTO**

### **✅ Qué Debería Pasar:**
```bash
1️⃣ N8N recibe el JSON vía webhook
2️⃣ Llama a tu API /inventario
3️⃣ API procesa y devuelve resultados
4️⃣ N8N verifica si hay vulnerabilidades
5️⃣ Si hay vulnerabilidades → Envía alerta Slack
6️⃣ Responde al webhook con estado del scan
```

### **✅ Respuestas Esperadas:**
```bash
🟢 Con vulnerabilidades:
{
  "status": "success",
  "message": "Security scan completed for test-repo",
  "vulnerabilities_found": 2,
  "timestamp": "2026-03-27T14:30:00Z"
}

🟢 Sin vulnerabilidades:
{
  "status": "success", 
  "message": "No vulnerabilities found for test-repo",
  "timestamp": "2026-03-27T14:30:00Z"
}
```

---

## 🚨 **SOLUCIÓN DE PROBLEMAS**

### **❌ Si la API no responde:**
```bash
🔧 Verificar URL en nodo "Call Security API"
🔧 Asegurar que tu API esté corriendo y accesible
🔧 Revisar que el ngrok esté activo (si lo usas)
🔧 Verificar API key configurada correctamente
```

### **❌ Si el webhook no funciona:**
```bash
🔧 Verificar que el workflow esté activo
🔧 Revisar que la URL del webhook sea correcta
🔧 Verificar logs de ejecución en N8N
🔧 Comprobar formato JSON enviado
```

### **❌ Si Slack no envía notificaciones:**
```bash
🔧 Verificar URL del webhook de Slack
🔧 Revisar que el nodo esté activo
🔧 Comprobar permisos del webhook de Slack
```

---

## 🎯 **DATOS DE PRUEBA LISTOS**

### **✅ Test 1: Con Vulnerabilidades**
```json
{
  "repo": "test-vulnerable-repo",
  "dependencias": [
    {"name": "requests", "version": "2.25.0", "ecosystem": "pip"},
    {"name": "urllib3", "version": "1.24.0", "ecosystem": "pip"}
  ]
}
```

### **✅ Test 2: Sin Vulnerabilidades**
```json
{
  "repo": "test-safe-repo", 
  "dependencias": [
    {"name": "requests", "version": "2.32.0", "ecosystem": "pip"}
  ]
}
```

### **✅ Test 3: Edge Case**
```json
{
  "repo": "empty-test",
  "dependencias": []
}
```

---

## 🚀 **LISTO PARA USAR**

### **✅ Checklist Final:**
```bash
✅ Workflow importado en N8N web
✅ URL de API actualizada (ngrok o producción)
✅ API key configurada
✅ Slack webhook configurado (opcional)
✅ Workflow activado
✅ Webhook URL obtenida
✅ Tests ejecutados
✅ Logs verificados
```

---

## 🏆 **RESULTADO FINAL**

### **✅ Tu Integración N8N Web Está Lista:**

**Configuración completa:**
🏆 **Workflow importado** - Ready para usar en N8N web  
🏆 **API integrada** - Llama a tu Aquiles Security API  
🏆 **Automatización funcional** - Scanning automático de vulnerabilidades  
🏆 **Notificaciones configuradas** - Slack alerts opcionales  
🏆 **Testing preparado** - Datos de prueba listos  
🏆 **Documentación completa** - Guía paso a paso  

---

## 🎯 **¿QUÉ NECESITAS AHORA?**

### **✅ Para terminar la configuración:**

🚀 **URL de ngrok** - Si necesitas exponer tu API localmente  
🚀 **URL de producción** - Si tu API ya está desplegada  
🚀 **Slack webhook** - Si quieres notificaciones automáticas  
🚀 **Testing** - Para verificar que todo funciona  

---

## 📋 **ARCHIVO CREADO**

### **✅ Workflow para N8N Web:**
```bash
📄 aquiles-workflow-n8n-web.json
🎯 Configurado para N8N web empresa
🎯 URL placeholder para ngrok/producción
🎯 Listo para importar y usar
🎯 Documentación completa incluida
```

**¡Importa este archivo en tu N8N web y estará listo para usar! 🛡️**
