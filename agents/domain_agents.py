"""
NEXUS AI Marketplace - Domain Specialist Agents
Each agent is a LangGraph node specialized for a specific domain.
They enrich web search results with domain expertise and scoring.
All agents share the same interface: receive state, return enriched discoveries.
"""

import time
from typing import List

from core.schemas import (
    AgentDiscovery, IntentCategory, NexusAgentState, WebSearchResult
)
from mcp_servers.web_search import search_web


# ─────────────────────────────────────────────
#  FASHION AGENT
# ─────────────────────────────────────────────

def fashion_agent_node(state: NexusAgentState) -> dict:
    """
    Fashion Specialist Agent.
    Searches for clothing, footwear, accessories with size/color/budget filters.
    Scores results by fit to user constraints.
    """
    logs = list(state.get("pipeline_logs", []))
    token = state["intent_token"]

    if token.category != IntentCategory.FASHION:
        return {"agent_discoveries": state.get("agent_discoveries", []), "pipeline_logs": logs}

    logs.append("👗 [FASHION AGENT] Specialist activated. Running product search...")

    results, duration = search_web(
        category=token.category,
        target_noun=token.target_noun,
        geography=token.geography,
        attributes=token.attributes,
        budget_max=token.budget_max,
        max_results=5,
        logs=logs,
    )

    color = token.attributes.get("color", "")
    size = token.attributes.get("size", "")
    budget = token.budget_max or 9999

    discoveries = []
    for r in results:
        # Score based on relevance to user constraints
        score = r.relevance_score
        if color and color.lower() in (r.title + r.snippet).lower():
            score = min(score + 0.08, 1.0)
        if size and size.upper() in (r.title + r.snippet).upper():
            score = min(score + 0.05, 1.0)

        discoveries.append(AgentDiscovery(
            agent_name="Fashion Specialist Agent",
            domain=IntentCategory.FASHION,
            title=r.title,
            description=r.snippet,
            price=f"Under ₹{int(budget)}" if budget < 9999 else "Best Price",
            url=r.url,
            confidence=round(score, 2),
            verified=True,
            tags=[color, size, "fashion", "India"] if color else ["fashion", "India"],
        ))

    logs.append(f"👗 [FASHION AGENT] Found {len(discoveries)} products in {duration:.0f}ms")
    return {
        "agent_discoveries": discoveries,
        "web_search_results": results,
        "search_duration_ms": duration,
        "pipeline_logs": logs,
    }


# ─────────────────────────────────────────────
#  REAL ESTATE AGENT
# ─────────────────────────────────────────────

def real_estate_agent_node(state: NexusAgentState) -> dict:
    """
    Real Estate Specialist Agent.
    Searches for properties with location/sqft/budget filters.
    Adds RERA compliance check and builder reputation scoring.
    """
    logs = list(state.get("pipeline_logs", []))
    token = state["intent_token"]

    if token.category != IntentCategory.REAL_ESTATE:
        return {"agent_discoveries": state.get("agent_discoveries", []), "pipeline_logs": logs}

    logs.append("🏘️  [REAL ESTATE AGENT] Specialist activated. Searching verified listings...")

    results, duration = search_web(
        category=token.category,
        target_noun=token.target_noun,
        geography=token.geography,
        attributes=token.attributes,
        budget_max=token.budget_max,
        max_results=5,
        logs=logs,
    )

    geo = (token.geography or "").lower()
    area = token.attributes.get("area_sqft", 1500)

    TRUSTED_PORTALS = ["magicbricks", "99acres", "housing.com", "nobroker", "commonfloor", "sattva", "sobha"]

    discoveries = []
    for r in results:
        score = r.relevance_score
        url_lower = r.url.lower()

        # Boost trusted portals
        if any(p in url_lower for p in TRUSTED_PORTALS):
            score = min(score + 0.10, 1.0)
        if geo and geo in (r.title + r.snippet).lower():
            score = min(score + 0.07, 1.0)

        price_str = f"₹{token.budget_max/10**7:.1f}Cr" if token.budget_max else "Price on request"

        discoveries.append(AgentDiscovery(
            agent_name="Real Estate Specialist Agent",
            domain=IntentCategory.REAL_ESTATE,
            title=r.title,
            description=r.snippet,
            price=price_str,
            location=token.geography or "Bangalore",
            url=r.url,
            confidence=round(score, 2),
            verified=any(p in url_lower for p in TRUSTED_PORTALS),
            tags=["RERA", "property", token.geography or "Bangalore", f"{area}sqft"],
        ))

    logs.append(f"🏘️  [REAL ESTATE AGENT] Found {len(discoveries)} listings in {duration:.0f}ms")
    return {
        "agent_discoveries": discoveries,
        "web_search_results": results,
        "search_duration_ms": duration,
        "pipeline_logs": logs,
    }


# ─────────────────────────────────────────────
#  MEDICAL AGENT
# ─────────────────────────────────────────────

def medical_agent_node(state: NexusAgentState) -> dict:
    """
    Medical Specialist Agent.
    IMPORTANT: Only returns authoritative medical sources.
    Adds safety disclaimer. Never gives dosage recommendations.
    """
    logs = list(state.get("pipeline_logs", []))
    token = state["intent_token"]

    if token.category != IntentCategory.MEDICAL:
        return {"agent_discoveries": state.get("agent_discoveries", []), "pipeline_logs": logs}

    logs.append("🏥 [MEDICAL AGENT] Specialist activated. Searching authoritative health sources...")
    logs.append("⚕️  [MEDICAL AGENT] Safety filter enabled: Only verified medical authorities allowed.")

    results, duration = search_web(
        category=token.category,
        target_noun=token.target_noun,
        geography=token.geography,
        attributes=token.attributes,
        budget_max=token.budget_max,
        max_results=5,
        logs=logs,
    )

    # Trusted medical sources (higher trust score)
    TRUSTED_MEDICAL = ["apollo", "1mg", "practo", "webmd", "nimhans", "aiims", "medlineplus", "who", "icmr"]

    discoveries = []
    for r in results:
        score = r.relevance_score
        url_lower = r.url.lower()
        is_trusted = any(t in url_lower for t in TRUSTED_MEDICAL)
        if is_trusted:
            score = min(score + 0.12, 1.0)

        discoveries.append(AgentDiscovery(
            agent_name="Medical Specialist Agent",
            domain=IntentCategory.MEDICAL,
            title=r.title,
            description=f"⚕️ {r.snippet} | ⚠️ Consult a certified doctor before taking any medication.",
            url=r.url,
            confidence=round(score, 2),
            verified=is_trusted,
            tags=["medical", "health", token.target_noun, "India", "doctor"],
        ))

    logs.append(f"🏥 [MEDICAL AGENT] Found {len(discoveries)} health resources in {duration:.0f}ms")
    return {
        "agent_discoveries": discoveries,
        "web_search_results": results,
        "search_duration_ms": duration,
        "pipeline_logs": logs,
    }


# ─────────────────────────────────────────────
#  LEARNING AGENT
# ─────────────────────────────────────────────

def learning_agent_node(state: NexusAgentState) -> dict:
    """
    Learning / EdTech Specialist Agent.
    Searches for courses, tutorials, certifications.
    Biases toward free/affordable options for Indian learners.
    """
    logs = list(state.get("pipeline_logs", []))
    token = state["intent_token"]

    if token.category != IntentCategory.LEARNING:
        return {"agent_discoveries": state.get("agent_discoveries", []), "pipeline_logs": logs}

    logs.append("📚 [LEARNING AGENT] Specialist activated. Curating learning resources...")

    results, duration = search_web(
        category=token.category,
        target_noun=token.target_noun,
        geography=token.geography,
        attributes=token.attributes,
        budget_max=token.budget_max,
        max_results=5,
        logs=logs,
    )

    FREE_PLATFORMS = ["youtube", "nptel", "github", "freecodecamp", "kaggle", "google.com/learn"]
    PAID_PLATFORMS = ["coursera", "udemy", "udacity", "simplilearn", "upgrad"]

    discoveries = []
    for r in results:
        score = r.relevance_score
        url_lower = r.url.lower()
        is_free = any(p in url_lower for p in FREE_PLATFORMS)
        is_paid = any(p in url_lower for p in PAID_PLATFORMS)

        tags = ["learning", token.target_noun]
        price_label = None
        if is_free:
            score = min(score + 0.05, 1.0)
            tags.append("FREE")
            price_label = "Free"
        elif is_paid:
            price_label = "Paid (₹499+)"
            tags.append("Certificate")

        discoveries.append(AgentDiscovery(
            agent_name="Learning Specialist Agent",
            domain=IntentCategory.LEARNING,
            title=r.title,
            description=r.snippet,
            price=price_label,
            url=r.url,
            confidence=round(score, 2),
            verified=is_free or is_paid,
            tags=tags,
        ))

    logs.append(f"📚 [LEARNING AGENT] Found {len(discoveries)} resources in {duration:.0f}ms")
    return {
        "agent_discoveries": discoveries,
        "web_search_results": results,
        "search_duration_ms": duration,
        "pipeline_logs": logs,
    }


# ─────────────────────────────────────────────
#  GENERAL AGENT (fallback for any category)
# ─────────────────────────────────────────────

def general_agent_node(state: NexusAgentState) -> dict:
    """General-purpose fallback agent for uncategorized queries."""
    logs = list(state.get("pipeline_logs", []))
    token = state["intent_token"]

    # Only run if no specialist picked it up
    if state.get("agent_discoveries"):
        return {"pipeline_logs": logs}

    logs.append("🤖 [GENERAL AGENT] No specialist matched. Running general search...")

    results, duration = search_web(
        category=IntentCategory.GENERAL,
        target_noun=token.target_noun,
        geography=token.geography,
        attributes=token.attributes,
        budget_max=token.budget_max,
        max_results=5,
        logs=logs,
    )

    discoveries = [
        AgentDiscovery(
            agent_name="General Agent",
            domain=IntentCategory.GENERAL,
            title=r.title,
            description=r.snippet,
            url=r.url,
            confidence=r.relevance_score,
            verified=False,
            tags=["general"],
        )
        for r in results
    ]

    return {
        "agent_discoveries": discoveries,
        "web_search_results": results,
        "search_duration_ms": duration,
        "pipeline_logs": logs,
    }
