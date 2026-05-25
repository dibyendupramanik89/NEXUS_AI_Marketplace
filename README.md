# 🌐 NEXUS AI Marketplace
### Enterprise Multi-Agent Programmatic Search & Monetization Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-purple.svg)](https://langchain-ai.github.io/langgraph/)
[![Claude](https://img.shields.io/badge/LLM-Claude%20%7C%20Gemini-orange.svg)](https://anthropic.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

<img width="933" height="743" alt="image" src="https://github.com/user-attachments/assets/fb784a96-de7c-46a3-8376-0a0c0f9c927d" />



# 🧠 NEXUS AI Marketplace
## The Programmatic Ad Exchange for the AI Era


NEXUS is a real-time auction engine that runs INSIDE
any LLM conversation pipeline — converting user intent
into ad revenue without tracking a single cookie.

### Live Demo Queries
- "I want a 3BHK flat in Varthur Bangalore"
- "Blue t-shirt XL under ₹1500"
- "Medicine for migraine headache"
- "Learn agentic AI with LangGraph"

### Why This Matters
- ChatGPT: 10M queries/day → $0 ad revenue
- Gemini: Billions of queries → $0 from conversations  
- NEXUS: Every commercial query → Real auction revenue

## 🚀 What is NEXUS?

NEXUS is an **intent-driven agentic marketplace** that turns any user search query into a monetizable signal — routing it through specialized AI agents, running a real-time programmatic ad auction, performing live web search, and delivering unified **sponsored + organic results** in a single intelligent response.

Think of it as: **Google Ads + Google Search + ChatGPT** — unified by agentic AI, with full transparency.

---

## 🎯 The Problem NEXUS Solves

Today people search across Claude, ChatGPT, Gemini for things like:
- *"I want to buy a blue XL tshirt for ₹1500"*
- *"Show me 1500 sqft flats in Varthur Bangalore"*
- *"Medicine for migraine"*
- *"Learn agentic AI from scratch"*

**Current platforms each handle this poorly:**
- **Google Search**: Ads and organic are disconnected. No agentic reasoning.
- **ChatGPT / Claude / Gemini**: Great reasoning, but no marketplace, no real-time auction, no revenue model.
- **Shopping platforms**: Category-specific. No cross-domain intelligence.

**NEXUS does all of it in one pipeline, with a revenue model built in.**

---

## 🏗️ Enterprise Agentic AI Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                  NEXUS AI MARKETPLACE — ENTERPRISE AGENTIC PLATFORM                                 │
│            Intent-Based • Auction-Driven • Privacy-First • Observable & Auditable                   │
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ INPUT CHANNELS                          │ API GATEWAY & EDGE                                        │
├─────────────────────────────────────────┼─────────────────────────────────────────────────────────  ┤
│  • Web UI (Gradio Dashboard)            │  • Auth & Validation      • Rate Limiting                 │
│  • CLI Query Mode                       │  • Request Routing        • Trace ID Injection            │
│  • API Endpoint (Future)                │  • User Session Mgmt      • Request Timeout               │
└─────────────────────────────────────────┴─────────────────────────────────────────────────────────  ┘
                                                          │
                                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ INPUT GUARDRAILS (6 Checks)                                                                         │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  ✓ PII Detection & Masking  ✓ Toxicity & Safety Filter  ✓ Query Validation                          │
│  ✓ Budget Sanity Check      ✓ Category Whitelist        ✓ Policy Enforcement                        │
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                          │
                                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                    AGENT ORCHESTRATOR / SUPERVISOR (The Brain)                                      │
│  🧠 Central Command: Intent Extraction • Privacy Engine • Routing Logic • Request Decomposition     │
├──────────────────────────────────────────────────────────────────────────────────────────────────── ┤ 
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────┐  ┌────────────────┐  ┌────────────┐    │
│  │ Intent          │  │ Privacy Engine   │  │ Routing      │  │ Request        │  │ Policy &   │    │
│  │ Classification  │  │ (PII Scrubbing)  │  │ Logic        │  │ Decomposition  │  │ Action     │    │
│  │ (LLM/Heuristic) │  │ Token Creation   │  │ (Multi-Path) │  │ (Parallel)     │  │ Rules      │    │
│  └─────────────────┘  └──────────────────┘  └──────────────┘  └────────────────┘  └────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘
                  │                                                                  │
        ┌─────────┘                                                                  └──────────┐
        ▼                                                                                       ▼
┌──────────────────────────────────────────┐              ┌──────────────────────────────────────────┐
│  ⚡ PAX AUCTION PATH                      │              │  🤖 DOMAIN AGENTS PATH                   │
├──────────────────────────────────────────┤              ├──────────────────────────────────────────┤
│  • 2nd-Price Auction Engine              │              │  • Fashion Specialist Agent              │
│  • Real-time Bidding Pool                │              │  • Real Estate Specialist Agent          │
│  • Budget Adjustment & Verification      │              │  • Medical Specialist Agent              │
│  • Winner Selection (~15-30ms)           │              │  • Learning & Ed-Tech Agent              │
│  • Inventory Checks (RERA, Active)       │              │  • General Search Agent                  │
│                                          │              │  • DuckDuckGo Web Search (FREE)          │
└──────────────────────────────────────────┘              └──────────────────────────────────────────┘
        │                                                          │
        └──────────────────────────┬─────────────────────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ TOOLS & ENTERPRISE SYSTEMS                                                                          │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  • Web Search (DuckDuckGo)  • Vector DB Simulation  • LLM APIs (Claude/Gemini)                      │
│  • Verification Engines    • Privacy Checks        • Memory Store                                   │
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                          │
                                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ OUTPUT GUARDRAILS (6 Checks)                                                                        │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  ✓ Response Validation  ✓ PII Redaction  ✓ Audit Trail Logging  ✓ Cost Aggregation                  │
│  ✓ Quality Scoring      ✓ Bias Detection                                                            │
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                          │
                                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ HUMAN-IN-THE-LOOP (Escalation on High-Cost / Ambiguous)                                             │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  Agent Suggests Action  →  Human Review & Approval  →  Feedback Capture  →  Policy Update           │
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                          │
                                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ FINAL RESPONSE TO USER                                                                              │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  • JSON Structured Result  • Winning Sponsored Ad  • Organic Results  • Metrics & Traces            │ 
│  • Cost Breakdown          • Audit Log & Reasoning                                                  │
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────┐  ┌──────────────────────┐  ┌──────────────────────────────────┐
│  GLOBAL SHARED MEMORY           │  │  OBSERVABILITY       │  │  GOVERNANCE & SECURITY           │
├─────────────────────────────────┤  ├──────────────────────┤  ├──────────────────────────────────┤
│  • Session Memory               │  │  • Distributed       │  │  • RBAC & Approval Workflows     │
│  • Long-Term Memory             │  │    Tracing           │  │  • Data Encryption (TLS/E2E)     │
│  • User Profile (Non-PII)       │  │  • Metrics           │  │  • Audit Trail (Immutable)       │
│  • Context Retrieval            │  │  • Latency Tracking  │  │  • Policy Engine & Rules         │
│  • State Management             │  │  • Cost Tracking     │  │  • Compliance (GDPR/CCPA)        │
│                                 │  │  • Anomaly Detection │  │  • Rate Limiting & Quotas        │
└─────────────────────────────────┘  └──────────────────────┘  └──────────────────────────────────┘

KEY DESIGN PRINCIPLES:
  ✓ Intent-Based Routing        ✓ Privacy-First (Ephemeral Tokens)   ✓ Dual Execution (Auction + Search)
  ✓ Observable & Auditable      ✓ Scalable & Extensible              ✓ Multi-LLM Support (Claude/Gemini)
```

### Simple End-to-End Flow

```
User Query: "I want to buy a flat 1500sq feet in varthur bangalore"
                            │
                            ▼
        ┌──────────────────────────────────┐
        │     🧠 Supervisor Agent           │
        │   (Claude / Gemini / Fallback)    │
        │   Intent Classification + NLU     │
        └─────────────┬────────────────────┘
                      │
        ┌─────────────▼────────────────────┐
        │     🛡️ Privacy Engine             │
        │   PII Scrubbing → Ephemeral Token │
        │   (GDPR-safe, no raw query shared)│
        └─────────────┬────────────────────┘
                      │
         ┌────────────┴────────────┐
         ▼                         ▼
┌──────────────────┐    ┌─────────────────────────┐
│  ⚡ PAX Auction  │    │  🤖 Domain Specialist    │
│  All brands bid  │    │  Agent (one per domain)  │
│  concurrently    │    │  + Real DuckDuckGo       │
│  (~15–30ms)      │    │  Web Search (FREE)        │
└────────┬─────────┘    └──────────┬──────────────┘
         │                         │
         ▼                         ▼
┌──────────────────────────────────────────────────┐
│              🎨 Synthesis Node                   │
│   Verified Sponsored Ad + Organic Results        │
│   Anti-hallucination gate | Confidence scoring  │
└──────────────────────────────────────────────────┘
                      │
                      ▼
           ✅ Unified User Response
```

---

## 🔧 Architecture Components Deep Dive

### **Input Layer**
- **Web UI**: Enterprise Gradio dashboard with real-time pipeline visualization
- **CLI Mode**: Single-query command-line interface for quick testing
- **API Endpoint**: RESTful endpoint for embedding NEXUS into third-party platforms

### **API Gateway & Edge**
- **Authentication & Validation**: OAuth2-ready, rate limiting per user/API key
- **Request Tracing**: Every request gets a unique trace ID for observability
- **Session Management**: Maintains user context across multiple queries

### **Input Guardrails** (Defense-in-Depth)
1. **PII Detection & Masking** — Detects names, emails, phone numbers; masks before processing
2. **Toxicity & Safety Filter** — Blocks harmful queries using ML classifiers
3. **Query Validation** — Format checking, length limits, character set validation
4. **Budget Sanity Check** — Rejects unrealistic budget constraints (e.g., -₹100)
5. **Category Whitelist** — Prevents queries for restricted categories (if configured)
6. **Policy Enforcement** — Custom business rules (geo-blocking, time-based rules, etc.)

### **Agent Orchestrator/Supervisor** (The Brain)
- **Intent Classification**: Uses LLM (Claude/Gemini) or deterministic fallback to classify user intent into Fashion, Real Estate, Medical, Learning, or General
- **Privacy Engine**: Scrubs PII and creates ephemeral tokens containing only intent metadata (category, budget, geography)
- **Routing Logic**: Decides whether to invoke PAX Auction Path, Domain Search Path, or both
- **Request Decomposition**: Breaks complex queries into sub-tasks for parallel execution
- **Policy & Action Rules**: Applies business rules, escalation thresholds, and approval gates

### **Dual Execution Paths**

#### **Path A: PAX Auction (Real-time Bidding)**
- Concurrent bidding from all registered advertisers in the relevant category
- Second-price auction mechanism: winner pays second-highest bid
- Budget-aware pricing: CPM adjusted based on advertiser constraints
- ~15-30ms execution time (sub-100ms for guaranteed response)
- Result: Single **Winning Ad** (verified and formatted for display)

#### **Path B: Domain Specialist Agents + Web Search**
- Category-specific agents apply domain expertise:
  - **Fashion Agent**: Filters by color, size, fit, brand reputation
  - **Real Estate Agent**: Verifies RERA registration, checks locality safety, computes EMI
  - **Medical Agent**: Flags prescription vs. OTC, checks doctor credentials
  - **Learning Agent**: Verifies course accreditation, checks instructor reviews
- Parallel DuckDuckGo web search (free, no API key)
- Result: 5–10 **Organic Results** (ranked by relevance + domain confidence)

### **Tools & Enterprise Systems**
- **Web Search**: DuckDuckGo (free, unlimited), Brave Search (paid), Tavily AI (AI-optimized)
- **Vector Database**: Simulated for demo; can integrate Pinecone/Weaviate/Milvus
- **LLM APIs**: Claude 3 (Anthropic), Gemini (Google), Ollama (self-hosted)
- **Verification Engines**: RERA database lookups, brand reputation checks, credential validation
- **Privacy Checks**: Re-verification of PII masking, encryption audit
- **Memory Store**: Session context, user preferences, interaction history (encrypted)

### **Output Guardrails** (Final Quality Gates)
1. **Response Validation** — Checks structure, completeness, formatting
2. **PII Redaction** — Final pass to ensure no PII leaked into response
3. **Audit Trail Logging** — Records every step for compliance/debugging
4. **Cost Aggregation** — Calculates total cost (auction CPM + search cost + processing fee)
5. **Quality Scoring** — Confidence scores for each result; flags low-confidence results
6. **Bias Detection** — ML model flags potentially biased recommendations

### **Human-in-the-Loop (HITL)**
Triggered for:
- **High-cost transactions** (e.g., real estate deals >₹50L)
- **Ambiguous intents** (low classification confidence)
- **Policy violations** (potential fraud signals)
- **Customer escalations** (user disputes the recommendation)

Flow: Agent Suggests → Human Reviews → Feedback Captured → Policy Updated (continuous learning)

### **Final Response**
Unified JSON structure containing:
- **Sponsored Result**: Winning ad with bid price, verification status
- **Organic Results**: Top 5 domain-verified results with ranking explanation
- **Metrics**: Latency breakdown, cost, confidence scores
- **Audit Log**: Full trace of decision-making (for transparency & debugging)

### **Cross-Cutting Concerns**

#### **Global Shared Memory**
- **Session Memory**: Current conversation context, intermediate results
- **Long-Term Memory**: User preferences, purchase history (anonymized)
- **User Profile**: Non-PII behavioral profile for personalization
- **Context Retrieval**: Vector similarity search for relevant past sessions

#### **Observability**
- **Distributed Tracing**: Every step instrumented with OpenTelemetry
- **Metrics**: Latency (p50/p95/p99), cost per request, success rate
- **Structured Logging**: JSON logs with trace ID correlation
- **Anomaly Detection**: Auto-alerts on unusual patterns (e.g., 100x cost spike)

#### **Governance & Security**
- **RBAC**: Role-based access (admin, brand manager, analyst)
- **Approval Workflows**: Multi-step sign-off for policy changes
- **Data Encryption**: TLS in-transit, encryption at-rest for sensitive fields
- **Audit Trail**: Immutable ledger of all state changes (Merkle tree validation)
- **Compliance**: GDPR-compliant (consent, data retention, deletion)

---

## 🌟 Unique Features (Not in Google / Claude / Meta AI)

| Feature | Google | ChatGPT | Claude | Gemini | **NEXUS** |
|---------|--------|---------|--------|--------|-----------|
| Agentic multi-step reasoning | ❌ | ✅ | ✅ | ✅ | ✅ |
| Real-time programmatic auction | ❌ | ❌ | ❌ | ❌ | ✅ **UNIQUE** |
| Privacy tokenization (GDPR) | Partial | ❌ | ❌ | ❌ | ✅ **UNIQUE** |
| Sponsored + Organic unified | ❌ | ❌ | ❌ | ❌ | ✅ **UNIQUE** |
| Domain specialist agents | ❌ | ❌ | ❌ | ❌ | ✅ **UNIQUE** |
| Free real web search | ✅ | Limited | Limited | ✅ | ✅ Free |
| Anti-hallucination gate | ❌ | Partial | Partial | Partial | ✅ |
| B2B CPM revenue model | Closed | ❌ | ❌ | ❌ | ✅ **UNIQUE** |
| LLM-agnostic (Claude+Gemini) | N/A | N/A | N/A | N/A | ✅ |
| Transparent bid disclosure | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 🤖 Domain Specialist Agents

| Agent | Domain | Search Strategy | Scoring |
|-------|--------|----------------|---------|
| Fashion Agent | Clothing, footwear, accessories | Color + Size + Budget filters | Product fit score |
| Real Estate Agent | Flats, villas, plots, PGs | Location + sqft + Budget | RERA trust boost |
| Medical Agent | Medicines, symptoms, doctors | Condition + urgency | Authority source filter |
| Learning Agent | Courses, tutorials, certs | Topic + skill level + format | Free/paid tagging |
| General Agent | Everything else | Broad intent | Relevance ranking |


---

## 🔌 Free Web Search APIs Used

| API | Cost | Limit | Use Case |
|-----|------|-------|----------|
| DuckDuckGo Search | **FREE** | Unlimited | Primary search |
| Brave Search | Free tier | 2000/month | Upgrade path |
| Tavily AI | Free tier | 1000/month | AI-optimized search |

No API key needed for DuckDuckGo. NEXUS runs fully offline in fallback mode.

---

## ⚡ Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/dibyendupramanik89/NEXUS_AI_Marketplace.git
cd nexus-ai-marketplace

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure API Key

```bash
cp .env.example .env
# Edit .env and add your key:
# ANTHROPIC_API_KEY=sk-ant-...   (Claude - recommended)
# GEMINI_API_KEY=...             (Gemini - alternative)
# No key = deterministic fallback mode (still works!)
# I have used Ollama model
### 4. Install Ollama Models
```
```bash
# Install Ollama
# Mac:   brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh
# Win:   https://ollama.com/download

# Start Ollama
ollama serve

# Pull primary model (9.6GB — best quality, Google Gemma 4)
ollama pull gemma4:e4b

# Pull fallback model (2.7GB — fast & lightweight)
ollama pull qwen3.5:2b

# Verify
ollama list
```

### 3. Run

```bash
# Launch UI (recommended)
python main.py --ui

# Run test suite
python main.py --test

# Single query
python main.py i want to buy a blue tshirt size xl
```

Open **http://localhost:7860** in your browser.

---

## 📁 Project Structure

```
nexus_ai_marketplace/
├── main.py                    ← Entry point (CLI + UI launcher)
├── app.py                     ← Enterprise Gradio dashboard
├── config.py                  ← LLM configuration (Claude/Gemini)
├── requirements.txt
├── .env.example
│
├── core/
│   ├── schemas.py             ← All Pydantic models + LangGraph state
│   ├── privacy.py             ← PII scrubbing + ephemeral token engine
│   └── auction.py             ← Programmatic Ad Exchange (PAX)
│
├── agents/
│   ├── supervisor.py          ← Intent classification (LLM + deterministic)
│   ├── domain_agents.py       ← Fashion, Real Estate, Medical, Learning, General
│   └── auction_synthesis.py   ← Auction node + synthesis/presentation node
│
├── mcp_servers/
│   └── web_search.py          ← DuckDuckGo MCP server (free, no key)
│
├── workflow/
│   └── graph.py               ← LangGraph state machine + routing
│
└── tests/
    └── test_pipeline.py       ← Full test suite (no API key needed)
```

---

## 🧪 Running Tests

```bash
# All tests (no API key required)
pytest tests/ -v

# Specific test class
pytest tests/test_pipeline.py::TestAuction -v
```

---

## 🔮 Roadmap (Next Steps for Enterprise)

- [ ] **PostgreSQL persistence** — store sessions, bids, user preferences
- [ ] **Redis caching** — cache search results for 5 minutes
- [ ] **Streaming responses** — real-time token streaming to UI
- [ ] **Brand API integrations** — real Myntra, Magicbricks, Apollo APIs
- [ ] **Multi-language support** — Hindi, Kannada, Tamil queries
- [ ] **User preference memory** — personalization without PII storage
- [ ] **Admin dashboard** — bid analytics, CPM trends, category reports
- [ ] **FastAPI REST layer** — expose NEXUS as an API for embedding
- [ ] **Kubernetes deployment** — Helm charts for production scale
- [ ] **A/B testing framework** — test different auction strategies

---

## 🛡️ Three Core Pillars

**1. Privacy First** — Raw queries never leave the privacy engine. Only anonymized ephemeral tokens are broadcast to bidders. GDPR-compliant by design.

**2. Verification** — Every sponsored result passes an inventory verification gate before reaching users. Hallucinated or inactive listings are dropped automatically.

**3. Transparency** — Users see both sponsored and organic results clearly labeled, with bid prices disclosed. No black-box manipulation.

---

## 📜 License

MIT License — free for personal and commercial use.

---

**Built with:** Python · LangGraph · LangChain · Claude/Gemini · DuckDuckGo · Gradio · Pydantic

*NEXUS AI Marketplace — Turning intent into opportunity, transparently.*
