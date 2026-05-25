# NEXUS AI Marketplace - Quick Start

## 🚀 Get Started in 2 Minutes

### Step 1: Activate Environment
```bash
cd <your path>/nexus_ai_marketplace
source .venv/bin/activate
```

### Step 2: Run the App
```bash
python app.py
```

### Step 3: Open Browser
```
http://localhost:7860
```

---

## 📚 Full Documentation

See **USER_GUIDE.md** for comprehensive setup and usage instructions.

---

## 📊 Architecture

The system has 10 pipeline stages:

```
Query Input
    ↓
🔐 API Gateway (Security)
    ↓
🛡️ Input Guardrails (5 checks)
    ↓
🧠 Orchestrator (Intent & Planning)
    ↓
⚡ Agents + PAX Auction (Bidding)
    ↓
🔍 Domain Specialist (Web Search)
    ↓
✍️ Synthesis (Merge Results)
    ↓
🔒 Output Guardrails (6 checks)
    ↓
👤 Human Review
    ↓
📊 Observability & Logging
    ↓
Final Response (Text/JSON/UI)
```

---

## 🎯 UI Tabs

1. **⚡ Command Center** — Main dashboard with query input and results
2. **📡 Pipeline Logs** — Full trace logs and markdown response
3. **📊 Observability** — Real-time metrics and session tracking

---

## ⚙️ Configuration

Create `.env` file:
```env
ACTIVE_LLM=claude
ANTHROPIC_API_KEY=your_key_here
LOG_LEVEL=INFO
```

---

## 🐛 Troubleshooting

**Error: `python: command not found`**
```bash
source .venv/bin/activate
```

**Error: `ModuleNotFoundError`**
```bash
pip install -r requirements.txt
```

**Port 7860 in use:**
```bash
lsof -i :7860
kill -9 <PID>
```

---

## 📖 More Help

- See `USER_GUIDE.md` for full documentation
- Check `config.py` for configuration options
- Review `requirements.txt` for dependencies

---

**Version:** 1.0.0  
**Last Updated:** May 24, 2026
