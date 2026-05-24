"""
NEXUS AI Marketplace - Core Data Schemas
Enterprise-grade Pydantic models for the multi-agent agentic pipeline.
"""

from __future__ import annotations
from typing import Annotated, Any, Dict, List, Optional, Sequence
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
import enum


# ─────────────────────────────────────────────
#  REDUCER FUNCTIONS FOR STATE MANAGEMENT
# ─────────────────────────────────────────────

def add_logs(existing: List[str], new: List[str]) -> List[str]:
    """Concatenate log lists for concurrent node updates."""
    return (existing or []) + (new or [])


def add_bids(existing: List, new: List) -> List:
    """Concatenate bid lists for concurrent auction updates."""
    return (existing or []) + (new or [])


def add_discoveries(existing: List, new: List) -> List:
    """Concatenate discovery lists from multiple agents."""
    return (existing or []) + (new or [])


# ─────────────────────────────────────────────
#  ENUMS
# ─────────────────────────────────────────────

class IntentCategory(str, enum.Enum):
    FASHION = "fashion"
    REAL_ESTATE = "real_estate"
    MEDICAL = "medical"
    LEARNING = "learning"
    GENERAL = "general"


class ConfidenceLevel(str, enum.Enum):
    HIGH = "high"       # > 0.85
    MEDIUM = "medium"   # 0.60 – 0.85
    LOW = "low"         # < 0.60


# ─────────────────────────────────────────────
#  INTENT TOKEN (Privacy-Safe Signal)
# ─────────────────────────────────────────────

class EphemeralIntentToken(BaseModel):
    """Privacy-safe representation of user intent. No PII leaves this token."""
    session_id: str = Field(description="Anonymous session identifier")
    category: IntentCategory = Field(description="Domain classification")
    target_noun: str = Field(description="Generic target item (e.g., 'tshirt', 'flat', 'medicine')")
    geography: Optional[str] = Field(None, description="Anonymized location (city/area only)")
    budget_min: Optional[float] = Field(None, description="Min budget in INR")
    budget_max: Optional[float] = Field(None, description="Max budget in INR")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Non-PII attributes")
    raw_query_hash: str = Field(description="SHA256 hash of original query for audit trail")
    confidence: float = Field(default=0.9, description="Classification confidence 0-1")


# ─────────────────────────────────────────────
#  SEARCH RESULT (Organic Web Search)
# ─────────────────────────────────────────────

class WebSearchResult(BaseModel):
    """Single organic search result from DuckDuckGo."""
    rank: int
    title: str
    snippet: str
    url: str
    source: str = "web"
    relevance_score: float = Field(default=0.5)
    agent_label: str = Field(default="Organic")


# ─────────────────────────────────────────────
#  AGENT DISCOVERY (Domain Specialist Output)
# ─────────────────────────────────────────────

class AgentDiscovery(BaseModel):
    """Structured output from a specialized domain agent."""
    agent_name: str
    domain: IntentCategory
    title: str
    description: str
    price: Optional[str] = None
    location: Optional[str] = None
    url: str
    confidence: float = Field(default=0.7)
    verified: bool = False
    tags: List[str] = Field(default_factory=list)


# ─────────────────────────────────────────────
#  PAX BID (Programmatic Ad Exchange)
# ─────────────────────────────────────────────

class BidRequest(BaseModel):
    """Sent to each advertiser during auction."""
    intent_token: EphemeralIntentToken
    floor_cpm_inr: float = Field(default=50.0)
    auction_id: str


class BidResponse(BaseModel):
    """Returned by an advertiser bidder."""
    advertiser: str
    brand: str
    cpm_bid_inr: float
    title: str
    description: str
    price: str
    cta: str = "Shop Now"
    deal_url: str
    verification_token: str
    creative_type: str = "text_ad"
    category: IntentCategory


class WinningAd(BaseModel):
    """Verified winning ad after auction + validation."""
    bid: BidResponse
    auction_rank: int = 1
    verification_passed: bool = False
    verification_reason: str = ""


# ─────────────────────────────────────────────
#  SYSTEM STATE (LangGraph State Machine)
# ─────────────────────────────────────────────

class NexusAgentState(TypedDict):
    """Complete pipeline state passed between LangGraph nodes."""
    # Conversation
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_query: str
    session_id: str

    # Intent Processing
    intent_token: Optional[EphemeralIntentToken]
    routing_category: str

    # Auction (with reducer for concurrent updates)
    all_bids: Annotated[List[BidResponse], add_bids]
    winning_ad: Optional[WinningAd]

    # Agent Discoveries (with reducer for concurrent updates)
    agent_discoveries: Annotated[List[AgentDiscovery], add_discoveries]
    web_search_results: Annotated[List[WebSearchResult], add_discoveries]

    # Pipeline Control (with reducer for concurrent updates)
    is_verified: bool
    pipeline_logs: Annotated[List[str], add_logs]
    error_state: Optional[str]

    # Analytics
    total_bids_received: int
    auction_duration_ms: float
    search_duration_ms: float
