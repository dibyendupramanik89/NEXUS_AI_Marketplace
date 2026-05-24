"""
NEXUS AI Marketplace - Web Search MCP Server
Uses DuckDuckGo Search (100% free, no API key required).
Also supports Brave Search (free tier 2000 req/month) as upgrade path.

MCP-compatible interface: structured tool definitions + async execution.
"""

import time
from typing import List, Optional

from core.schemas import IntentCategory, WebSearchResult


# ─────────────────────────────────────────────
#  DUCKDUCKGO SEARCH ENGINE
# ─────────────────────────────────────────────

def _build_search_query(
    category: IntentCategory,
    target_noun: str,
    geography: Optional[str],
    attributes: dict,
    budget_max: Optional[float],
) -> str:
    """Build an optimized search query from intent token."""
    parts = []

    if category == IntentCategory.FASHION:
        color = attributes.get("color", "")
        size = attributes.get("size", "")
        budget = f"under ₹{int(budget_max)}" if budget_max else ""
        parts = [color, target_noun, size, budget, "India buy online"]

    elif category == IntentCategory.REAL_ESTATE:
        area = attributes.get("area_sqft", "")
        geo = geography or ""
        budget = f"₹{int(budget_max/100000)}L budget" if budget_max else ""
        parts = [target_noun, area, "sqft", geo, budget, "site visit RERA India"]

    elif category == IntentCategory.MEDICAL:
        parts = [target_noun, "treatment India", "best medicine", "doctor advice", "symptoms"]

    elif category == IntentCategory.LEARNING:
        parts = [target_noun, "online course", "tutorial", "learn free", "India 2025"]

    else:
        parts = [target_noun, geography or "", "India", "best options 2025"]

    return " ".join(p for p in parts if p).strip()


def search_web(
    category: IntentCategory,
    target_noun: str,
    geography: Optional[str],
    attributes: dict,
    budget_max: Optional[float],
    max_results: int = 5,
    logs: Optional[List[str]] = None,
) -> tuple[List[WebSearchResult], float]:
    """
    Performs a real DuckDuckGo web search and returns structured results.
    Falls back to curated mock results if duckduckgo_search is unavailable.
    """
    query = _build_search_query(category, target_noun, geography, attributes, budget_max)
    if logs is not None:
        logs.append(f"🔍 [WEB SEARCH MCP] Query: \"{query}\"")

    t0 = time.time()

    try:
        from duckduckgo_search import DDGS
        raw = list(DDGS().text(query, max_results=max_results))
        duration_ms = (time.time() - t0) * 1000

        results = []
        for i, r in enumerate(raw):
            results.append(WebSearchResult(
                rank=i + 1,
                title=r.get("title", "No Title"),
                snippet=r.get("body", "")[:300],
                url=r.get("href", "https://www.google.com"),
                source="DuckDuckGo",
                relevance_score=round(1.0 - (i * 0.12), 2),
                agent_label="Organic Search",
            ))

        if logs is not None:
            logs.append(
                f"🔍 [WEB SEARCH MCP] {len(results)} results returned in {duration_ms:.0f}ms"
            )
        return results, duration_ms

    except ImportError:
        # Graceful fallback with curated results per category
        duration_ms = (time.time() - t0) * 1000
        if logs is not None:
            logs.append("⚠️  [WEB SEARCH MCP] duckduckgo_search not installed. Using curated fallback.")
        return _curated_fallback(category, target_noun, geography, budget_max), duration_ms

    except Exception as e:
        duration_ms = (time.time() - t0) * 1000
        if logs is not None:
            logs.append(f"⚠️  [WEB SEARCH MCP] Search error: {str(e)[:60]}. Using fallback.")
        return _curated_fallback(category, target_noun, geography, budget_max), duration_ms


def _curated_fallback(
    category: IntentCategory,
    target_noun: str,
    geography: Optional[str],
    budget_max: Optional[float],
) -> List[WebSearchResult]:
    """Curated high-quality fallback results per domain when web search unavailable."""

    if category == IntentCategory.FASHION:
        return [
            WebSearchResult(rank=1, title="Myntra – Blue T-Shirts for Men", snippet="Wide range of blue t-shirts, starting ₹399. Free delivery, easy returns.", url="https://www.myntra.com/blue-tshirts-men", source="Fallback", relevance_score=0.92),
            WebSearchResult(rank=2, title="Flipkart – Blue Cotton Tshirts XL", snippet="Buy men's blue t-shirts online. 30-day returns. Cash on delivery.", url="https://www.flipkart.com/blue-tshirts", source="Fallback", relevance_score=0.87),
            WebSearchResult(rank=3, title="Amazon India – Blue T-Shirts under ₹1500", snippet="Explore blue t-shirts. Prime delivery. Hundreds of brands.", url="https://www.amazon.in/blue-tshirts", source="Fallback", relevance_score=0.82),
            WebSearchResult(rank=4, title="Ajio – Branded Tees Blue XL", snippet="Latest fashion finds from top brands. 50% off on first order.", url="https://www.ajio.com", source="Fallback", relevance_score=0.76),
            WebSearchResult(rank=5, title="Meesho – Blue T-Shirts Budget Deals", snippet="Reseller-backed fashion. Blue tees from ₹199.", url="https://www.meesho.com", source="Fallback", relevance_score=0.70),
        ]

    elif category == IntentCategory.REAL_ESTATE:
        geo = geography or "Bangalore"
        return [
            WebSearchResult(rank=1, title=f"MagicBricks – 1500 sqft Flats in {geo}", snippet=f"RERA-verified properties in {geo}. Verified photos, virtual tours.", url="https://www.magicbricks.com", source="Fallback", relevance_score=0.93),
            WebSearchResult(rank=2, title=f"99acres – Buy Flat {geo}", snippet=f"Best properties in {geo} at lowest prices. Zero brokerage options.", url="https://www.99acres.com", source="Fallback", relevance_score=0.88),
            WebSearchResult(rank=3, title=f"Housing.com – 3BHK in {geo}", snippet="Trusted housing portal. RERA approved. Book site visits online.", url="https://housing.com", source="Fallback", relevance_score=0.83),
            WebSearchResult(rank=4, title="NoBroker – Flats Direct from Owners", snippet="No brokerage fee. Contact owners directly. Thousands of listings.", url="https://www.nobroker.in", source="Fallback", relevance_score=0.78),
            WebSearchResult(rank=5, title="CommonFloor – Apartments Bangalore", snippet="Explore projects, resale, ready-to-move options across Bangalore.", url="https://www.commonfloor.com", source="Fallback", relevance_score=0.71),
        ]

    elif category == IntentCategory.MEDICAL:
        return [
            WebSearchResult(rank=1, title="WebMD India – Migraine Causes & Treatment", snippet="Evidence-based information on migraine symptoms, triggers, and treatments.", url="https://www.webmd.com/migraines-headaches/migraines-headaches-migraines", source="Fallback", relevance_score=0.94),
            WebSearchResult(rank=2, title="Apollo Health – Online Neurologist Consultation", snippet="Consult certified neurologists online. Migraine diagnosis & prescription.", url="https://www.apollohospitals.com", source="Fallback", relevance_score=0.90),
            WebSearchResult(rank=3, title="1mg – Migraine Medicines", snippet="Buy prescription migraine medicines with a valid Rx. Home delivery.", url="https://www.1mg.com/search/all?name=migraine", source="Fallback", relevance_score=0.85),
            WebSearchResult(rank=4, title="Practo – Migraine Doctors in Bangalore", snippet="Book appointments with top neurologists in Bangalore.", url="https://www.practo.com", source="Fallback", relevance_score=0.80),
            WebSearchResult(rank=5, title="NIMHANS – Headache Clinic India", snippet="Expert migraine care at NIMHANS, Bangalore. Rated #1 neurology center.", url="https://nimhans.ac.in", source="Fallback", relevance_score=0.74),
        ]

    elif category == IntentCategory.LEARNING:
        return [
            WebSearchResult(rank=1, title=f"Coursera – {target_noun.title()} Courses", snippet="Learn from top universities. Free audit. Certificates from ₹2000.", url="https://www.coursera.org", source="Fallback", relevance_score=0.92),
            WebSearchResult(rank=2, title=f"Udemy – {target_noun.title()} Bootcamp", snippet="Practical hands-on courses. Lifetime access. Starts at ₹499.", url="https://www.udemy.com", source="Fallback", relevance_score=0.87),
            WebSearchResult(rank=3, title="YouTube – Free Agentic AI Tutorials", snippet="Full-length free courses on YouTube. Indian instructors available.", url="https://www.youtube.com", source="Fallback", relevance_score=0.82),
            WebSearchResult(rank=4, title="NPTEL – Free Indian University Courses", snippet="IIT/IISc faculty courses. Free certificates on completion.", url="https://nptel.ac.in", source="Fallback", relevance_score=0.77),
            WebSearchResult(rank=5, title="GitHub – Open Source AI Projects", snippet="Learn by doing. Explore agentic AI repos and contribute.", url="https://github.com/topics/agentic-ai", source="Fallback", relevance_score=0.71),
        ]

    else:
        return [
            WebSearchResult(rank=1, title=f"Google – {target_noun}", snippet=f"Search results for {target_noun} in India.", url="https://www.google.com", source="Fallback", relevance_score=0.70),
        ]
