"""
NEXUS AI Marketplace - Auction & Synthesis Nodes (LangGraph)
- auction_node: runs the PAX programmatic auction
- synthesis_node: assembles final user-facing output
"""

from langchain_core.messages import AIMessage

from core.schemas import IntentCategory, NexusAgentState
from core.auction import ProgrammaticAuctionEngine


# ─────────────────────────────────────────────
#  AUCTION NODE
# ─────────────────────────────────────────────

def auction_node(state: NexusAgentState) -> dict:
    """
    LangGraph node: Runs the real-time programmatic auction.
    Inputs: intent_token
    Outputs: all_bids, winning_ad, total_bids_received, auction_duration_ms
    """
    logs = list(state.get("pipeline_logs", []))
    token = state["intent_token"]

    all_bids, winning_ad, duration = ProgrammaticAuctionEngine.run_auction(token, logs)

    return {
        "all_bids": all_bids,
        "winning_ad": winning_ad,
        "is_verified": winning_ad.verification_passed if winning_ad else False,
        "total_bids_received": len(all_bids),
        "auction_duration_ms": duration,
        "pipeline_logs": logs,
    }


# ─────────────────────────────────────────────
#  SYNTHESIS NODE
# ─────────────────────────────────────────────

_DOMAIN_ICONS = {
    IntentCategory.FASHION: "👗",
    IntentCategory.REAL_ESTATE: "🏘️",
    IntentCategory.MEDICAL: "🏥",
    IntentCategory.LEARNING: "📚",
    IntentCategory.GENERAL: "🔍",
}

_DOMAIN_LABELS = {
    IntentCategory.FASHION: "Fashion & Apparel",
    IntentCategory.REAL_ESTATE: "Real Estate",
    IntentCategory.MEDICAL: "Health & Medicine",
    IntentCategory.LEARNING: "Learning & Courses",
    IntentCategory.GENERAL: "General Search",
}


def synthesis_node(state: NexusAgentState) -> dict:
    """
    LangGraph node: Assembles the final user-facing output.
    Combines verified sponsored ad + organic agent discoveries.
    Formats for Gradio markdown rendering.
    """
    logs = list(state.get("pipeline_logs", []))
    logs.append("🎨 [SYNTHESIS] Assembling final presentation...")

    token = state["intent_token"]
    winning_ad = state.get("winning_ad")
    discoveries = state.get("agent_discoveries", [])
    all_bids = state.get("all_bids", [])

    icon = _DOMAIN_ICONS.get(token.category, "🔍")
    label = _DOMAIN_LABELS.get(token.category, "Search")

    # ── Header
    output = f"## {icon} NEXUS Results – {label}\n\n"
    output += f"> **Query processed** | Category: `{token.category.value.upper()}` | "
    output += f"Session: `{token.session_id}` | "
    output += f"Confidence: `{token.confidence:.0%}` | "
    output += f"Auction: `{state.get('total_bids_received', 0)} bids` in `{state.get('auction_duration_ms', 0):.0f}ms`\n\n"

    # ── Sponsored Result (Premium Placement)
    if winning_ad and winning_ad.verification_passed:
        bid = winning_ad.bid
        output += "---\n"
        output += "### ⚡ Sponsored Result (Verified)\n"
        output += f"**{bid.title}**\n\n"
        output += f"_{bid.description}_\n\n"
        output += f"💰 **Price:** {bid.price} &nbsp;|&nbsp; "
        output += f"🏷️ **Advertiser:** {bid.brand} &nbsp;|&nbsp; "
        output += f"📊 **Bid:** ₹{bid.cpm_bid_inr:.0f} CPM\n\n"
        output += f"🔗 [{bid.cta} →]({bid.deal_url})\n\n"

        # Competitive bids (transparency)
        if len(all_bids) > 1:
            output += "<details><summary>📊 View all auction bids</summary>\n\n"
            output += "| Advertiser | CPM Bid |\n|---|---|\n"
            for b in sorted(all_bids, key=lambda x: x.cpm_bid_inr, reverse=True):
                marker = " 🏆" if b.advertiser == bid.advertiser else ""
                output += f"| {b.advertiser}{marker} | ₹{b.cpm_bid_inr} |\n"
            output += "\n</details>\n\n"
    else:
        output += "---\n"
        output += "ℹ️ *No sponsored results for this query. Showing organic results only.*\n\n"

    # ── Organic Results
    output += "---\n"
    output += f"### 🌐 Top {min(len(discoveries), 5)} Organic Results\n\n"

    if token.category == IntentCategory.MEDICAL:
        output += "> ⚠️ **Medical Disclaimer:** These results are for informational purposes only. Always consult a licensed doctor before taking any medication or treatment.\n\n"

    if discoveries:
        # Sort by confidence descending
        sorted_d = sorted(discoveries, key=lambda x: x.confidence, reverse=True)[:5]
        for i, d in enumerate(sorted_d, 1):
            verified_badge = "✅" if d.verified else "🔵"
            output += f"**{i}. {verified_badge} [{d.title}]({d.url})**\n\n"
            output += f"   {d.description[:200]}{'...' if len(d.description) > 200 else ''}\n\n"
            details = []
            if d.price:
                details.append(f"💰 {d.price}")
            if d.location:
                details.append(f"📍 {d.location}")
            details.append(f"🎯 Relevance: {d.confidence:.0%}")
            if d.tags:
                details.append(f"🏷️ {', '.join(d.tags[:3])}")
            output += f"   {' &nbsp;|&nbsp; '.join(details)}\n\n"
    else:
        output += "*No organic results found. Try refining your query.*\n\n"

    # ── Footer
    output += "---\n"
    output += "**NEXUS AI Marketplace** | "
    output += "🛡️ Privacy-first · ✅ Verified results · 🔍 Real web search · ⚡ Real-time auction\n"
    output += f"*Powered by Agentic AI + Programmatic Ad Exchange (PAX) Protocol*"

    logs.append("🏁 [SYNTHESIS] Pipeline complete. Response ready.")

    return {
        "messages": [AIMessage(content=output)],
        "pipeline_logs": logs,
    }
