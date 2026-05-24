# NEXUS AI Marketplace - User Guide & Setup Instructions

## 📋 Table of Contents
1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Running the Application](#running-the-application)
5. [Using the Dashboard](#using-the-dashboard)
6. [Troubleshooting](#troubleshooting)
7. [Architecture](#architecture)

---

## Overview

**NEXUS AI Marketplace** is an Enterprise Agentic AI Platform that implements a complete end-to-end pipeline for intelligent query processing with:

- ✅ **Input & Output Guardrails** — PII detection, prompt injection, toxicity filtering
- ✅ **Agent Orchestration** — Multi-agent supervisor with domain specialization
- ✅ **PAX Auction System** — Real-time bidding and brand placement
- ✅ **Observability** — Distributed tracing, metrics, cost tracking
- ✅ **Governance** — RBAC, audit logs, policy enforcement
- ✅ **Human-in-the-Loop** — Safety approvals and escalations

The platform is built with **Gradio** (UI), **LangGraph** (workflow orchestration), and supports multiple LLM providers.

---

## System Requirements

### Hardware
- **CPU**: 4+ cores (8+ recommended)
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 5GB free space

### Software
- **Python**: 3.10+ (tested on 3.11, 3.12)
- **Operating System**: macOS, Linux, or Windows

### Dependencies
- gradio 6.0+
- langgraph
- python-dotenv
- duckduckgo-search (for web search MCP)
- anthropic / openai (LLM clients)

---

## Installation

### Step 1: Clone/Navigate to Project

```bash
cd /Users/priyanka-dibyendu/Downloads/nexus_ai_marketplace
```

### Step 2: Create Virtual Environment

```bash
# Using venv (recommended)
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist or is incomplete, install manually:

```bash
pip install gradio>=6.0 langgraph python-dotenv anthropic duckduckgo-search
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```env
# LLM Configuration
ACTIVE_LLM=claude  # or 'openai', 'gemini'
ANTHROPIC_API_KEY=your_claude_api_key_here
OPENAI_API_KEY=your_openai_key_here

# Optional Settings
LOG_LEVEL=INFO
ENABLE_OBSERVABILITY=true
ENABLE_GUARDRAILS=true
```

---

## Running the Application

### Method 1: Direct Python Execution

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Run the app
python app.py
```

### Method 2: Using Gradio CLI

```bash
gradio app.py
```

### Method 3: With Custom Port

```bash
# Run on a different port (default is 7860)
python app.py --server_port 8000
```

### Expected Output

```
Note: The parameters have been moved from the Blocks constructor to the launch() method...

* Running on local URL:  http://0.0.0.0:7860
* To create a public link, set `share=True` in `launch()`.
```

### Access the Dashboard

Open your browser and navigate to:
```
http://localhost:7860
```

---

## Using the Dashboard

### Layout

The Gradio interface is organized into **3 main columns**:

#### **Left Column: Query Input & Pipeline Stages**
- Enter your query in the text box
- Click **🚀 Run Pipeline** to execute
- View real-time pipeline stage progression
- See example queries for quick testing

#### **Center Column: Results**
- **Sponsored Result** — Winner from PAX auction (top bidder)
- **Organic Results** — Top 5 domain specialist findings
- **PAX Auction Leaderboard** — All bids and CPM rankings

#### **Right Column: Metrics & Guardrails**
- **Pipeline Metrics** — Category, confidence, bid count, winning CPM
- **Input Guardrails** — 5 safety checks (PII, injection, toxicity, etc.)
- **Output Guardrails** — 6 compliance checks

### Tabs

1. **⚡ Command Center** (Main Dashboard)
   - Query input and execution
   - Real-time results visualization

2. **📡 Pipeline Logs**
   - Full trace logs with execution steps
   - Complete markdown response output

3. **📊 Observability**
   - Real-time metrics dashboard
   - Session memory and state tracking
   - Cost and performance analytics

---

## Example Queries

Try these pre-configured examples:

- `i want to buy tshirt color blue, size xl, with price range 1500Rs`
- `i want to buy a flat 1500sq feet in varthur bangalore location`
- `user searching for medicine for migraine headache`
- `I want to learn agentic AI and build multi-agent LangGraph systems`
- `best gaming laptop under 80000 rupees in India`
- `PG accommodation near Koramangala Bangalore under 12000 per month`

---

## Pipeline Stages Explained

The system processes queries through 10 sequential stages:

| Stage | Icon | Description |
|-------|------|-------------|
| API Gateway & Edge | 🔐 | Authentication, rate limiting, WAF |
| Input Guardrails | 🛡️ | PII detection, injection filtering, toxicity check |
| Supervisor / Orchestrator | 🧠 | Intent classification, planning, routing |
| Privacy Engine | 🛡️ | PII scrubbing, ephemeral tokens |
| PAX Auction | ⚡ | Real-time brand bidding, CPM selection |
| Domain Specialist Agent | 🔍 | Web search, discovery, scoring |
| Synthesis Node | ✍️ | Merge sponsored + organic results |
| Output Guardrails | 🔒 | Hallucination detection, PII redaction |
| Human-in-the-Loop | 👤 | Safety approval, escalation |
| Observability | 📊 | Tracing, metrics, cost tracking |

---

## Troubleshooting

### Issue: `python: command not found`

**Solution**: Use full Python path or activate virtual environment
```bash
source .venv/bin/activate
python app.py
```

### Issue: `ModuleNotFoundError: No module named 'gradio'`

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
# or
pip install gradio langgraph python-dotenv
```

### Issue: Port 7860 Already in Use

**Solution**: Kill the process or use a different port
```bash
# Find process using port 7860
lsof -i :7860

# Kill the process
kill -9 <PID>

# Or run on different port
python app.py --server_port 8000
```

### Issue: API Key Errors (Claude, OpenAI, etc.)

**Solution**: Check `.env` configuration
```bash
# Verify .env file exists and has valid keys
cat .env

# Test API key
python -c "from anthropic import Anthropic; print('✅ Claude API configured')"
```

### Issue: Application Crashes After Query Submission

**Solution**: Check logs and verify all dependencies
```bash
# Run with verbose logging
LOG_LEVEL=DEBUG python app.py

# Check terminal output for specific error
```

### Issue: UI Shows Dark Theme Despite Update

**Solution**: Clear browser cache
1. Open **Developer Tools** (F12 or Cmd+Option+I)
2. Right-click refresh button → **Empty Cache and Hard Refresh**
3. Or use: `Ctrl+Shift+Delete` (Windows) / `Cmd+Shift+Delete` (macOS)

---

## Configuration

### Environment Variables

```env
# Active LLM Model
ACTIVE_LLM=claude              # Options: claude, openai, gemini
ANTHROPIC_API_KEY=sk-...       # Claude API key
OPENAI_API_KEY=sk-...          # OpenAI API key
GOOGLE_API_KEY=...             # Gemini API key

# Application Settings
LOG_LEVEL=INFO                 # DEBUG, INFO, WARNING, ERROR
ENABLE_OBSERVABILITY=true      # Enable metrics tracking
ENABLE_GUARDRAILS=true         # Enable safety checks
SERVER_PORT=7860               # Gradio server port

# Auction Settings
PAX_AUCTION_ENABLED=true       # Enable real-time bidding
DEFAULT_CPM_BUDGET=100         # Default CPM budget
```

### File Structure

```
nexus_ai_marketplace/
├── app.py                 # Main Gradio application
├── config.py              # Configuration loader
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── agents/                # Agent implementations
│   ├── supervisor.py
│   ├── domain_agents.py
│   └── auction_synthesis.py
├── core/                  # Core utilities
│   ├── guardrails.py
│   ├── observability.py
│   ├── memory.py
│   ├── gateway.py
│   └── schemas.py
├── workflow/              # LangGraph workflow
│   └── graph.py
├── mcp_servers/           # Model Context Protocol servers
│   └── web_search.py
└── tests/                 # Test suite
    └── test_pipeline.py
```

---

## Architecture Overview

The platform implements a **10-stage enterprise AI pipeline**:

```
User Input
    ↓
🔐 API Gateway & Edge (Auth, Rate Limit, WAF)
    ↓
🛡️ Input Guardrails (PII, Injection, Toxicity)
    ↓
🧠 Agent Orchestrator (Intent, Planning, Routing)
    ↓
⚡ Specialized Agents + PAX Auction (Domain + Bidding)
    ↓
🔍 Web Search & Discovery (DuckDuckGo MCP)
    ↓
✍️ Synthesis Node (Merge Sponsored + Organic)
    ↓
🔒 Output Guardrails (Hallucination, PII Redaction)
    ↓
👤 Human-in-the-Loop (Approval, Escalation)
    ↓
📊 Observability (Tracing, Metrics, Cost)
    ↓
User Response (Text, JSON, UI)
```

See `ARCHITECTURE_DIAGRAM.png` for visual representation.

---

## Advanced Usage

### Running with Custom LLM

```python
# In .env
ACTIVE_LLM=openai
OPENAI_API_KEY=sk-your-key-here

# Or in Python
from config import get_active_llm
llm = get_active_llm()
```

### Accessing Observability Data

```python
from core.observability import observability

# Get dashboard data
data = observability.get_dashboard_data()
print(f"Total Requests: {data['metrics']['total_requests']}")
print(f"Success Rate: {data['metrics']['success_rate']:.2%}")
print(f"Avg Latency: {data['metrics']['avg_latency_ms']:.0f}ms")
```

### Memory & Session Management

```python
from core.memory import memory

# Get session snapshot
session_id = "user-session-123"
snapshot = memory.snapshot(session_id)
print(f"Conversation Turns: {snapshot.conversation_turns}")
print(f"User Profile: {snapshot.user_profile}")
```

---

## Performance Tips

1. **Enable Caching** — Reduce API calls for similar queries
2. **Batch Processing** — Process multiple queries efficiently
3. **Monitor Costs** — Track LLM usage and spending
4. **Use Local LLMs** — Deploy Llama or similar locally to reduce latency
5. **Database Indexing** — Index frequently searched fields

---

## Support & Documentation

- **Gradio Docs**: https://www.gradio.app/docs
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **Anthropic Claude**: https://docs.anthropic.com/
- **OpenAI API**: https://platform.openai.com/docs/

---

## License

This project is proprietary. All rights reserved.

---

**Last Updated**: May 24, 2026
**Version**: 1.0.0
