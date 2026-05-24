"""
NEXUS AI Marketplace - Supervisor / Intent Classification Agent
The "brain" of the pipeline. Classifies user query into a domain,
extracts structured constraints, and creates a privacy-safe intent token.
Supports Claude, Gemini, or deterministic fallback (no key needed).
"""

import json
import re
from typing import List, Optional

from langchain_core.messages import HumanMessage

from core.schemas import IntentCategory, NexusAgentState
from core.privacy import PrivacyEngine
from config import get_llm


# ─────────────────────────────────────────────
#  DETERMINISTIC FALLBACK PARSER
# ─────────────────────────────────────────────

def _deterministic_parse(query: str) -> dict:
    """Rule-based fallback when no LLM key is available. Covers common Indian use cases."""
    q = query.lower()

    # Real estate signals
    if any(w in q for w in ["flat", "apartment", "bhk", "sqft", "property", "house", "villa", "plot"]):
        geo = None
        for loc in ["varthur", "whitefield", "koramangala", "hsr", "pune", "mumbai", "delhi", "hyderabad", "chennai"]:
            if loc in q:
                geo = loc.title()
                break
        budget = None
        m = re.search(r'(\d+)\s*(?:cr|crore)', q)
        if m:
            budget = float(m.group(1)) * 10_000_000
        m2 = re.search(r'(\d+)\s*(?:l|lakh)', q)
        if m2:
            budget = float(m2.group(1)) * 100_000
        area = None
        m3 = re.search(r'(\d{3,4})\s*(?:sq\.?\s*ft|sqft|square feet)', q)
        if m3:
            area = int(m3.group(1))
        return {
            "category": "real_estate", "target_noun": "flat",
            "geography": geo or "Bangalore", "budget_min": None, "budget_max": budget,
            "attributes": {"area_sqft": area or 1500},
            "confidence": 0.88,
        }

    # Fashion signals
    if any(w in q for w in ["tshirt", "t-shirt", "shirt", "jeans", "dress", "kurta", "saree", "shoes", "jacket", "clothing"]):
        color = None
        for c in ["blue", "red", "black", "white", "green", "yellow", "grey", "navy", "pink"]:
            if c in q:
                color = c
                break
        size = None
        for s in ["xs", "s", "m", "l", "xl", "xxl", "2xl", "3xl"]:
            if re.search(rf'\b{s}\b', q, re.I):
                size = s.upper()
                break
        budget = None
        m = re.search(r'(?:₹|rs\.?|inr)\s*(\d+)', q, re.I)
        if m:
            budget = float(m.group(1))
        if not budget:
            m2 = re.search(r'(\d{3,5})\s*(?:rs|inr|rupees)?', q, re.I)
            if m2:
                budget = float(m2.group(1))
        noun = next((w for w in ["tshirt", "t-shirt", "shirt", "jeans", "dress", "shoes"] if w in q), "clothing")
        return {
            "category": "fashion", "target_noun": noun,
            "geography": None, "budget_min": None, "budget_max": budget or 1500,
            "attributes": {"color": color, "size": size},
            "confidence": 0.87,
        }

    # Medical signals
    if any(w in q for w in ["medicine", "medical", "doctor", "hospital", "migraine", "headache", "fever", "diabetes", "pain", "treatment", "symptom"]):
        noun = "general care"
        for condition in ["migraine", "headache", "fever", "diabetes", "bp", "cancer", "arthritis", "depression", "anxiety"]:
            if condition in q:
                noun = condition
                break
        return {
            "category": "medical", "target_noun": noun,
            "geography": None, "budget_min": None, "budget_max": None,
            "attributes": {"urgency": "routine"},
            "confidence": 0.85,
        }

    # Learning signals
    if any(w in q for w in ["learn", "course", "tutorial", "agentic", "ai", "ml", "python", "certification", "skill", "study"]):
        topic = "agentic AI"
        for t in ["agentic ai", "machine learning", "python", "data science", "llm", "langchain", "devops", "cloud"]:
            if t in q:
                topic = t
                break
        return {
            "category": "learning", "target_noun": topic,
            "geography": None, "budget_min": None, "budget_max": None,
            "attributes": {"format": "online"},
            "confidence": 0.83,
        }

    # General fallback
    return {
        "category": "general", "target_noun": query[:60],
        "geography": None, "budget_min": None, "budget_max": None,
        "attributes": {},
        "confidence": 0.60,
    }


# ─────────────────────────────────────────────
#  LLM-POWERED INTENT CLASSIFIER
# ─────────────────────────────────────────────

_SYSTEM_PROMPT = """You are an intent classification engine for an Indian e-commerce marketplace.
Extract structured intent from user queries and return ONLY valid JSON with this exact schema:
{
  "category": "fashion" | "real_estate" | "medical" | "learning" | "general",
  "target_noun": "<generic item, no PII>",
  "geography": "<city or area name, null if none>",
  "budget_min": <number in INR or null>,
  "budget_max": <number in INR or null>,
  "attributes": {<key-value pairs relevant to category, no PII>},
  "confidence": <0.0 to 1.0>
}

Rules:
- Never include names, phone numbers, emails in output
- Convert "1500Rs" to budget_max: 1500
- Convert "1.2Cr" to budget_max: 12000000
- For fashion: attributes include color, size, gender, brand_preference
- For real_estate: attributes include area_sqft, bhk, furnished_status, property_type
- For medical: attributes include urgency (routine/urgent/emergency), condition
- For learning: attributes include skill_level (beginner/intermediate/advanced), format (online/offline)
- Return ONLY JSON, no explanation, no markdown fences"""


def llm_classify_intent(query: str, llm, logs: List[str]) -> dict:
    """Use LLM to classify intent. Returns parsed dict."""
    logs.append(f"🧠 [SUPERVISOR] Calling {type(llm).__name__} for intent classification...")
    try:
        response = llm.invoke([
            HumanMessage(content=f"{_SYSTEM_PROMPT}\n\nUser Query: \"{query}\"")
        ])
        text = response.content.strip()
        # Strip markdown fences if present
        text = re.sub(r'^```(?:json)?\n?', '', text)
        text = re.sub(r'\n?```$', '', text)
        parsed = json.loads(text)
        logs.append(f"🧠 [SUPERVISOR] LLM classified as: {parsed.get('category', 'unknown').upper()} (confidence: {parsed.get('confidence', 0):.0%})")
        return parsed
    except Exception as e:
        logs.append(f"⚠️  [SUPERVISOR] LLM parse error: {str(e)[:60]}. Using deterministic fallback.")
        return _deterministic_parse(query)


# ─────────────────────────────────────────────
#  LANGGRAPH NODE
# ─────────────────────────────────────────────

_llm = get_llm(temperature=0.0)


def supervisor_node(state: NexusAgentState) -> dict:
    """
    LangGraph node: Classifies intent + creates privacy-safe token.
    Inputs: user_query
    Outputs: intent_token, routing_category
    """
    logs = list(state.get("pipeline_logs", []))
    query = state["user_query"]
    logs.append(f"🎬 [SUPERVISOR] Received query: \"{query[:80]}...\"" if len(query) > 80 else f"🎬 [SUPERVISOR] Received query: \"{query}\"")

    # Classify intent
    if _llm:
        data = llm_classify_intent(query, _llm, logs)
    else:
        logs.append("📝 [SUPERVISOR] No LLM key. Using deterministic classifier...")
        data = _deterministic_parse(query)

    # Map to enum
    try:
        category = IntentCategory(data.get("category", "general"))
    except ValueError:
        category = IntentCategory.GENERAL

    # Build privacy token
    token = PrivacyEngine.create_token(
        raw_query=query,
        category=category,
        target_noun=data.get("target_noun", query[:30]),
        geography=data.get("geography"),
        budget_min=data.get("budget_min"),
        budget_max=data.get("budget_max"),
        attributes=data.get("attributes", {}),
        confidence=data.get("confidence", 0.7),
        logs=logs,
    )

    return {
        "intent_token": token,
        "routing_category": category.value,
        "pipeline_logs": logs,
    }
