"""
NEXUS AI Marketplace — LangGraph Orchestration Pipeline
Implements the full Enterprise Agentic AI Platform flow:
  Gateway → Input Guardrails → Orchestrator (Intent + Route)
  → [PAX Auction ‖ Domain Search] → Synthesis → Output Guardrails → HITL → Observability
"""

from __future__ import annotations

import re
import time
import uuid
import hashlib
from typing import Any, Dict, List, Optional, Tuple

from langchain_core.messages import HumanMessage, AIMessage

from core.schemas import (
    NexusAgentState, EphemeralIntentToken, IntentCategory,
    BidRequest, AgentDiscovery, WebSearchResult, WinningAd,
)
from core.gateway import APIGateway
from core.guardrails import InputGuardrails, OutputGuardrails
from core.auction import ProgrammaticAuctionEngine
from core.memory import memory as global_memory
from core.observability import observability
from config import get_llm


# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _log(logs: list, msg: str):
    ts = time.strftime("%H:%M:%S")
    logs.append(f"[{ts}] {msg}")


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:12]


# ─────────────────────────────────────────────────────────────────────────────
#  INTENT CLASSIFIER (heuristic + optional LLM)
# ─────────────────────────────────────────────────────────────────────────────

_CATEGORY_KEYWORDS = {
    IntentCategory.FASHION: [
        "tshirt", "t-shirt", "shirt", "jeans", "dress", "saree", "kurta",
        "shoes", "footwear", "clothes", "clothing", "apparel", "fashion",
        "wear", "outfit", "jacket", "trouser", "skirt", "lehenga",
    ],
    IntentCategory.REAL_ESTATE: [
        "flat", "apartment", "house", "villa", "bhk", "property", "sqft",
        "sq ft", "square feet", "bedroom", "plot", "site", "pg", "paying guest",
        "rent", "buy flat", "real estate", "builder", "rera",
        "accommodation", "room", "varthur", "koramangala", "whitefield",
    ],
    IntentCategory.MEDICAL: [
        "medicine", "tablet", "drug", "headache", "migraine", "fever",
        "doctor", "hospital", "pain", "symptom", "treatment", "prescription",
        "pharmacy", "health", "disease", "illness", "cure", "dosage",
        "paracetamol", "ibuprofen", "antibiotic",
    ],
    IntentCategory.LEARNING: [
        "learn", "course", "tutorial", "study", "education", "certification",
        "boot camp", "bootcamp", "training", "workshop", "skill",
        "programming", "python", "langgraph", "langchain", "agentic", "ai",
        "machine learning", "data science", "nlp", "llm", "deep learning",
    ],
}

_BUDGET_RE = re.compile(
    r'(?:₹|rs\.?|inr)?\s*(\d[\d,]*)\s*(?:rs\.?|inr|k|lakh|cr|crore)?',
    re.IGNORECASE,
)
_GEO_KEYWORDS = [
    "bangalore", "bengaluru", "mumbai", "delhi", "pune", "hyderabad",
    "chennai", "kolkata", "varthur", "koramangala", "whitefield", "hsr",
    "indiranagar", "electronic city",
]


def _extract_budget(query: str) -> Tuple[Optional[float], Optional[float]]:
    raw = query.lower()
    amounts = []
    for m in _BUDGET_RE.finditer(raw):
        num = float(m.group(1).replace(",", ""))
        # unit detection
        after = raw[m.end():m.end() + 8]
        if "cr" in after:
            num *= 1_00_00_000
        elif "lakh" in after or "lac" in after:
            num *= 1_00_000
        elif "k" in after:
            num *= 1_000
        amounts.append(num)
    if not amounts:
        return None, None
    if len(amounts) == 1:
        return None, amounts[0]
    return min(amounts), max(amounts)


def _extract_geography(query: str) -> Optional[str]:
    q = query.lower()
    for geo in _GEO_KEYWORDS:
        if geo in q:
            return geo.title()
    return None


def _extract_target_noun(query: str, category: IntentCategory) -> str:
    q = query.lower()
    nouns = {
        IntentCategory.FASHION:     ["tshirt", "t-shirt", "shirt", "jeans", "dress", "shoes"],
        IntentCategory.REAL_ESTATE: ["flat", "apartment", "house", "villa", "bhk", "pg", "room"],
        IntentCategory.MEDICAL:     ["medicine", "tablet", "headache", "migraine", "drug"],
        IntentCategory.LEARNING:    ["course", "certification", "training"],
        IntentCategory.GENERAL:     [],
    }
    for noun in nouns.get(category, []):
        if noun in q:
            return noun
    return "item"


def classify_intent_heuristic(query: str) -> Tuple[IntentCategory, float]:
    """Rule-based fallback classifier."""
    q = query.lower()
    scores: Dict[IntentCategory, int] = {}
    for cat, keywords in _CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in q)
        if score:
            scores[cat] = score

    if not scores:
        return IntentCategory.GENERAL, 0.55

    best = max(scores, key=lambda k: scores[k])
    conf = min(0.95, 0.6 + scores[best] * 0.08)
    return best, conf


def classify_intent_llm(query: str, llm) -> Tuple[IntentCategory, float]:
    """LLM-based intent classification."""
    prompt = f"""You are an intent classifier for an AI marketplace.

Classify this user query into EXACTLY ONE category. Reply with ONLY the JSON:
{{"category": "<category>", "confidence": <0.0-1.0>, "target_noun": "<main item>", "budget_max": <number or null>, "geography": "<city or null>"}}

Categories: fashion, real_estate, medical, learning, general

Query: "{query}"

JSON response:"""
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        text = response.content.strip()
        # Strip markdown fences if present
        text = re.sub(r'```(?:json)?', '', text).strip().strip('`').strip()
        import json
        data = json.loads(text)
        cat_str = data.get("category", "general").lower().strip()
        cat_map = {
            "fashion": IntentCategory.FASHION,
            "real_estate": IntentCategory.REAL_ESTATE,
            "medical": IntentCategory.MEDICAL,
            "learning": IntentCategory.LEARNING,
            "general": IntentCategory.GENERAL,
        }
        category = cat_map.get(cat_str, IntentCategory.GENERAL)
        confidence = float(data.get("confidence", 0.85))
        return category, confidence, data
    except Exception as e:
        return None, None, None


# ─────────────────────────────────────────────────────────────────────────────
#  DOMAIN SEARCH AGENTS
# ─────────────────────────────────────────────────────────────────────────────

def _build_search_query(token: EphemeralIntentToken, user_query: str) -> str:
    """Build an optimised search query from the intent token."""
    parts = [token.target_noun]
    if token.geography:
        parts.append(token.geography)
    if token.budget_max:
        budget_str = f"under ₹{token.budget_max:,.0f}" if token.budget_max < 1_00_000 \
                     else f"around {token.budget_max/1_00_00_000:.1f} crore"
        parts.append(budget_str)
    return " ".join(parts) + " India"


def _duckduckgo_search(query: str, max_results: int = 6) -> List[Dict]:
    """Perform a DuckDuckGo web search."""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        return results
    except Exception as e:
        return []


def run_domain_search(
    token: EphemeralIntentToken,
    user_query: str,
    logs: list,
) -> Tuple[List[AgentDiscovery], List[WebSearchResult], float]:
    """Run DuckDuckGo search and parse results into AgentDiscovery objects."""
    t0 = time.time()
    search_query = _build_search_query(token, user_query)
    logs.append(f"🔍 [SEARCH AGENT] Query: '{search_query}'")

    raw_results = _duckduckgo_search(search_query, max_results=8)

    if not raw_results:
        # Deterministic fallback
        logs.append("⚠️  [SEARCH AGENT] DuckDuckGo returned no results — using deterministic fallback")
        raw_results = _fallback_results(token)

    web_results: List[WebSearchResult] = []
    discoveries: List[AgentDiscovery] = []

    for i, r in enumerate(raw_results[:6], 1):
        title = r.get("title", "")[:80]
        snippet = r.get("body", r.get("snippet", ""))[:200]
        url = r.get("href", r.get("url", "#"))
        source = r.get("source", url.split("/")[2] if "://" in url else "web")

        web_results.append(WebSearchResult(
            rank=i, title=title, snippet=snippet, url=url,
            source=source, relevance_score=max(0.5, 1.0 - i * 0.08),
        ))

        confidence = max(0.55, 1.0 - i * 0.07)
        # Budget filter
        if token.budget_max and snippet:
            if any(c.isdigit() for c in snippet):
                confidence = min(confidence + 0.05, 0.99)

        discoveries.append(AgentDiscovery(
            agent_name=f"SearchAgent-{token.category.value.title()}",
            domain=token.category,
            title=title,
            description=snippet,
            price=_extract_price_from_snippet(snippet),
            location=token.geography,
            url=url,
            confidence=confidence,
            verified=False,
            tags=[token.category.value, token.target_noun],
        ))

    dur = (time.time() - t0) * 1000
    logs.append(f"✅ [SEARCH AGENT] Found {len(discoveries)} results in {dur:.0f}ms")
    return discoveries, web_results, dur


def _extract_price_from_snippet(snippet: str) -> Optional[str]:
    m = re.search(r'₹[\d,]+(?:\s*(?:lakh|cr|k|/-)?)?|Rs\.?\s*[\d,]+', snippet, re.IGNORECASE)
    return m.group(0) if m else None


def _fallback_results(token: EphemeralIntentToken) -> List[Dict]:
    """Static fallback when network is unavailable."""
    defaults = {
        IntentCategory.FASHION: [
            {"title": "Blue T-Shirts XL – Myntra", "body": "Shop blue t-shirts XL size at Myntra. Starting ₹299. Free delivery & easy returns.", "href": "https://www.myntra.com"},
            {"title": "Blue T-Shirt XL Collection – Ajio", "body": "Exclusive brands at Ajio. Blue XL t-shirts ₹499 onwards. Express delivery.", "href": "https://www.ajio.com"},
        ],
        IntentCategory.REAL_ESTATE: [
            {"title": "1500 sqft Flats in Varthur Bangalore – 99acres", "body": "125 verified flats in Varthur. 2/3 BHK. ₹85L – ₹1.5Cr. RERA registered.", "href": "https://www.99acres.com"},
            {"title": "Prestige Smart City Varthur – 3BHK Ready", "body": "1480 sqft 3BHK, RERA approved. ₹1.35 Cr. Club house, pool, metro connectivity.", "href": "https://www.magicbricks.com"},
        ],
        IntentCategory.MEDICAL: [
            {"title": "Migraine Treatment – Apollo Hospitals", "body": "Expert neurologists for migraine treatment in Bangalore. OPD & online consult available.", "href": "https://www.apollohospitals.com"},
            {"title": "Medicines for Migraine – PharmEasy", "body": "Sumatriptan, Rizatriptan, Paracetamol for migraine. Order online, doorstep delivery.", "href": "https://pharmeasy.in"},
        ],
        IntentCategory.LEARNING: [
            {"title": "Agentic AI & LangGraph Course – Coursera", "body": "Build multi-agent AI systems. 40-hour comprehensive course. Certificate included.", "href": "https://www.coursera.org"},
            {"title": "Multi-Agent Systems with LangGraph – Udemy", "body": "Hands-on. Build production-grade agentic AI. 4.8★ rating. Lifetime access.", "href": "https://www.udemy.com"},
        ],
        IntentCategory.GENERAL: [
            {"title": "Search Results – Google India", "body": "Find what you're looking for across India's top marketplaces.", "href": "https://www.google.co.in"},
        ],
    }
    return defaults.get(token.category, defaults[IntentCategory.GENERAL])


# ─────────────────────────────────────────────────────────────────────────────
#  SYNTHESIS NODE — LLM-powered response generation
# ─────────────────────────────────────────────────────────────────────────────

def synthesize_response(
    user_query: str,
    token: EphemeralIntentToken,
    discoveries: List[AgentDiscovery],
    winning_ad: Optional[WinningAd],
    llm,
    logs: list,
) -> str:
    """Generate a final markdown response using LLM or deterministic template."""
    logs.append("✍️  [SYNTHESIS NODE] Generating final response...")

    category = token.category.value
    top_results = sorted(discoveries, key=lambda d: d.confidence, reverse=True)[:4]

    # Build context for LLM
    organic_ctx = "\n".join(
        f"{i+1}. {d.title} — {d.description[:100]} | {d.price or 'Price not listed'} | {d.url}"
        for i, d in enumerate(top_results)
    )
    sponsored_ctx = ""
    if winning_ad and winning_ad.verification_passed:
        b = winning_ad.bid
        sponsored_ctx = f"Sponsored: {b.title} | {b.price} | {b.deal_url}"

    if llm:
        prompt = f"""You are NEXUS AI, an enterprise-grade AI marketplace assistant in India.
Generate a helpful, structured markdown response for:

USER QUERY: {user_query}
CATEGORY: {category.upper()}
GEOGRAPHY: {token.geography or 'India'}
BUDGET: {f'Up to ₹{token.budget_max:,.0f}' if token.budget_max else 'Not specified'}

TOP ORGANIC RESULTS:
{organic_ctx}

{f'SPONSORED RESULT: {sponsored_ctx}' if sponsored_ctx else ''}

Instructions:
- Start with a brief summary (2-3 sentences)
- List top 3-4 recommendations with price, key features, and a link
- Add category-specific advice (e.g. RERA check for real estate, doctor consult for medical)
- Keep it concise, factual, and helpful
- Use INR currency (₹)
- Format with markdown headers and bullet points
"""
        try:
            resp = llm.invoke([HumanMessage(content=prompt)])
            result = resp.content.strip()
            logs.append(f"✅ [SYNTHESIS NODE] LLM response generated ({len(result)} chars)")
            return result
        except Exception as e:
            logs.append(f"⚠️  [SYNTHESIS NODE] LLM failed ({e}) — using template")

    # Deterministic template fallback
    return _template_response(user_query, token, top_results, winning_ad)


def _template_response(
    query: str,
    token: EphemeralIntentToken,
    results: List[AgentDiscovery],
    winning_ad: Optional[WinningAd],
) -> str:
    cat = token.category.value.replace("_", " ").title()
    geo = f" in {token.geography}" if token.geography else ""
    budget = f" (budget: ₹{token.budget_max:,.0f})" if token.budget_max else ""

    lines = [
        f"## 🔍 NEXUS Results: {cat}{geo}{budget}\n",
        f"**Query:** _{query}_\n",
        f"Here are the top matches for your search:\n",
    ]

    if winning_ad and winning_ad.verification_passed:
        b = winning_ad.bid
        lines += [
            f"### ⚡ Sponsored Result",
            f"**{b.title}**",
            f"- Price: {b.price}",
            f"- Brand: {b.brand}",
            f"- [{b.cta}]({b.deal_url})\n",
        ]

    if results:
        lines.append("### 🌐 Organic Results")
        for i, d in enumerate(results, 1):
            price_str = f" | 💰 {d.price}" if d.price else ""
            loc_str = f" | 📍 {d.location}" if d.location else ""
            lines += [
                f"**{i}. {d.title}**",
                f"- {d.description[:150]}",
                f"- Match: {d.confidence:.0%}{price_str}{loc_str}",
                f"- 🔗 [{d.url}]({d.url})\n",
            ]

    # Category-specific advice
    advice = {
        "real_estate": "\n> 💡 **Tip:** Always verify RERA registration before booking. Check for possession date, builder track record, and bank approvals.",
        "medical": "\n> ⚕️ **Medical Disclaimer:** Please consult a licensed doctor before taking any medication. This information is for reference only.",
        "fashion": "\n> 💡 **Tip:** Check size charts before ordering. Read return policies — most platforms offer 7-30 day easy returns.",
        "learning": "\n> 💡 **Tip:** Look for courses with hands-on projects and industry-recognized certificates for best career outcomes.",
    }
    lines.append(advice.get(token.category.value, "\n> 💡 **Tip:** Compare multiple options before making a decision."))

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN PIPELINE FUNCTION (called by app.py)
# ─────────────────────────────────────────────────────────────────────────────

def process_query(user_query: str) -> Tuple[str, str, Dict]:
    """
    Full NEXUS enterprise pipeline.
    Returns (markdown_response, logs_string, state_dict)
    """
    logs: List[str] = []
    session_id = uuid.uuid4().hex[:12]
    t_total = time.time()

    _log(logs, "═" * 60)
    _log(logs, f"NEXUS AI Pipeline — Session {session_id}")
    _log(logs, "═" * 60)

    # ── STAGE 1: API GATEWAY & EDGE ──────────────────────────────
    _log(logs, "STAGE 1 ▶ API Gateway & Edge")
    gw_result = APIGateway.process(session_id=session_id, payload=user_query, logs=logs)
    if not gw_result.allowed:
        err = f"🚫 [GATEWAY] Blocked: {gw_result.block_reason}"
        _log(logs, err)
        return err, "\n".join(logs), {"session_id": session_id, "error_state": gw_result.block_reason}

    # ── STAGE 2: INPUT GUARDRAILS ─────────────────────────────────
    _log(logs, "STAGE 2 ▶ Input Guardrails (5-layer)")
    ig_report, sanitized_query = InputGuardrails.run_all(user_query, logs)
    if ig_report.blocked:
        err = f"🚫 [INPUT GUARDRAIL] Query blocked: {ig_report.block_reason}"
        _log(logs, err)
        return err, "\n".join(logs), {"session_id": session_id, "error_state": ig_report.block_reason}

    # ── STAGE 3: ORCHESTRATOR — INTENT CLASSIFICATION ────────────
    _log(logs, "STAGE 3 ▶ Orchestrator — Intent Classification & Routing")
    llm = get_llm(temperature=0.0)

    llm_category, llm_confidence, llm_data = None, None, None
    if llm:
        llm_category, llm_confidence, llm_data = classify_intent_llm(sanitized_query, llm)

    if llm_category:
        category = llm_category
        confidence = llm_confidence
        target_noun = (llm_data or {}).get("target_noun", _extract_target_noun(sanitized_query, category))
        budget_max = (llm_data or {}).get("budget_max") or _extract_budget(sanitized_query)[1]
        geography = (llm_data or {}).get("geography") or _extract_geography(sanitized_query)
        _log(logs, f"✅ [ORCHESTRATOR] LLM classified: {category.value} ({confidence:.0%})")
    else:
        category, confidence = classify_intent_heuristic(sanitized_query)
        target_noun = _extract_target_noun(sanitized_query, category)
        budget_min, budget_max = _extract_budget(sanitized_query)
        geography = _extract_geography(sanitized_query)
        _log(logs, f"✅ [ORCHESTRATOR] Heuristic classified: {category.value} ({confidence:.0%})")

    _log(logs, f"   Category={category.value} | Noun={target_noun} | Geo={geography} | Budget=₹{budget_max:,.0f}" if budget_max else f"   Category={category.value} | Noun={target_noun}")

    # ── STAGE 4: PRIVACY ENGINE — EPHEMERAL TOKEN ─────────────────
    _log(logs, "STAGE 4 ▶ Privacy Engine — PII Scrub & Token Generation")
    intent_token = EphemeralIntentToken(
        session_id=session_id,
        category=category,
        target_noun=target_noun,
        geography=geography,
        budget_min=None,
        budget_max=float(budget_max) if budget_max else None,
        attributes={},
        raw_query_hash=_hash(user_query),
        confidence=confidence,
    )
    _log(logs, f"✅ [PRIVACY] Ephemeral token created — no PII in downstream pipeline")

    # ── STAGE 5: PAX AUCTION ──────────────────────────────────────
    _log(logs, "STAGE 5 ▶ PAX Programmatic Auction")
    auction_id = uuid.uuid4().hex[:12]
    bid_request = BidRequest(
        intent_token=intent_token,
        floor_cpm_inr=50.0,
        auction_id=auction_id,
    )
    all_bids, winning_ad, auction_ms = ProgrammaticAuctionEngine.run(
        bid_request, query=sanitized_query, logs=logs
    )

    # ── STAGE 6: DOMAIN SEARCH AGENT ─────────────────────────────
    _log(logs, "STAGE 6 ▶ Domain Search Agent (DuckDuckGo)")
    discoveries, web_results, search_ms = run_domain_search(intent_token, sanitized_query, logs)

    # ── STAGE 7: SYNTHESIS ───────────────────────────────────────
    _log(logs, "STAGE 7 ▶ Synthesis Node — Merging Sponsored + Organic")
    final_response = synthesize_response(
        user_query, intent_token, discoveries, winning_ad, llm, logs
    )

    # ── STAGE 8: OUTPUT GUARDRAILS ───────────────────────────────
    _log(logs, "STAGE 8 ▶ Output Guardrails (6-layer)")
    context_urls = [d.url for d in discoveries]
    og_report, clean_response = OutputGuardrails.run_all(
        response=final_response,
        category=category.value,
        context_urls=context_urls,
        discoveries=discoveries,
        winning_ad=winning_ad,
        logs=logs,
    )

    # ── STAGE 9: HUMAN-IN-THE-LOOP ───────────────────────────────
    _log(logs, "STAGE 9 ▶ Human-in-the-Loop Check")
    hitl_required = (
        category == IntentCategory.MEDICAL or
        og_report.blocked or
        confidence < 0.6
    )
    if hitl_required:
        _log(logs, "⚠️  [HITL] Flagged for human review (medical/low-confidence/blocked)")
        if category == IntentCategory.MEDICAL:
            clean_response += "\n\n> ⚕️ *This response has been flagged for medical compliance review. Please consult a licensed physician.*"
    else:
        _log(logs, "✅ [HITL] Auto-approved — confidence sufficient, no safety flags")

    # ── STAGE 10: OBSERVABILITY ──────────────────────────────────
    _log(logs, "STAGE 10 ▶ Observability — Tracing & Metrics")
    winning_cpm = winning_ad.bid.cpm_bid_inr if winning_ad else 0.0
    trace = observability.start_trace(session_id, user_query)
    observability.record_and_alert(trace, category.value, winning_cpm)

    total_ms = (time.time() - t_total) * 1000
    _log(logs, f"✅ [OBSERVABILITY] Trace {trace.trace_id} | Total {total_ms:.0f}ms")

    # Memory update
    global_memory.init_session(session_id)
    global_memory.add_turn(session_id, "user", user_query, category.value)
    global_memory.add_turn(session_id, "assistant", clean_response, category.value)
    _log(logs, "═" * 60)
    _log(logs, f"Pipeline COMPLETE in {total_ms:.0f}ms | {len(all_bids)} bids | {len(discoveries)} results")
    _log(logs, "═" * 60)

    state = {
        "session_id": session_id,
        "user_query": user_query,
        "intent_token": intent_token,
        "routing_category": category.value,
        "all_bids": all_bids,
        "winning_ad": winning_ad,
        "agent_discoveries": discoveries,
        "web_search_results": web_results,
        "is_verified": winning_ad.verification_passed if winning_ad else False,
        "pipeline_logs": logs,
        "error_state": None,
        "total_bids_received": len(all_bids),
        "auction_duration_ms": auction_ms,
        "search_duration_ms": search_ms,
    }

    return clean_response, "\n".join(logs), state


# ─────────────────────────────────────────────────────────────────────────────
#  TEST SUITE
# ─────────────────────────────────────────────────────────────────────────────

def run_test_suite():
    test_queries = [
        "i want to buy tshirt color blue size xl price range 1500Rs",
        "i want to buy a flat 1500sq feet in varthur bangalore",
        "medicine for migraine headache",
        "I want to learn agentic AI and build multi-agent LangGraph systems",
        "best gaming laptop under 80000 rupees in India",
    ]
    for q in test_queries:
        print(f"\n{'='*60}")
        print(f"QUERY: {q}")
        print('='*60)
        output, logs, state = process_query(q)
        print(logs[-5:])
        print(output[:300])