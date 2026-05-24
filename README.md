# 🌐 NEXUS AI Marketplace
### Enterprise Multi-Agent Programmatic Search & Monetization Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-purple.svg)](https://langchain-ai.github.io/langgraph/)
[![Claude](https://img.shields.io/badge/LLM-Claude%20%7C%20Gemini-orange.svg)](https://anthropic.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

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

## 🏗️ Architecture

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

## 💰 Business Model (B2B2C)

```
Brands/Advertisers ──CPM Bid──► PAX Auction Engine
                                        │
                                   NEXUS takes 30%
                                        │
                               ◄────────┘
Platform sells to: Google, Meta, Claude, Flipkart as AI search layer
```

**Revenue streams:**
1. **CPM Auction Revenue** — brands pay per 1000 impressions of their ad
2. **API Licensing** — sell NEXUS as middleware to e-commerce platforms
3. **SaaS Dashboard** — brands manage bids via NEXUS console
4. **Data Intelligence** — anonymized intent analytics (privacy-safe)

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
git clone https://github.com/yourname/nexus-ai-marketplace.git
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
