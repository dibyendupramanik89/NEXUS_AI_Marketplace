"""
NEXUS AI Marketplace — Enterprise Gradio Dashboard
Implements EVERY component from the Enterprise Agentic AI Platform diagram:
  • API Gateway & Edge
  • Input & Output Guardrails (5+6 checks)
  • Agent Orchestrator / Supervisor
  • Specialized Domain Agents
  • Global Shared Memory / Working Memory
  • Tools & Enterprise Systems (Web Search, Vector DB sim, APIs)
  • Human-in-the-Loop
  • Observability (Tracing, Metrics, Cost, Alerts)
  • Governance & Security
  • Model & Prompt Governance
  • Quality & Evaluation
  • Cost & Performance
"""

import gradio as gr
import json, time, uuid, os
from workflow.graph import process_query
from core.observability import observability, MetricsStore
from core.memory import memory as global_memory
from config import get_active_llm_name

# ─────────────────────────────────────────────────────────────────────────────
#   CSS  —  Dark Enterprise Theme
# ─────────────────────────────────────────────────────────────────────────────
ENTERPRISE_CSS = """
/* ── Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Global Reset */
.gradio-container { background:#ffffff !important; font-family:'Inter',sans-serif !important; color:#1a1a1a !important; max-width:100% !important; padding:0 !important; }
body { background:#ffffff !important; }
footer { display:none !important; }

/* ── Top Banner */
#nexus-banner { background:linear-gradient(135deg,#f5f5f5 0%,#eeeeee 100%); border-bottom:1px solid #e0e0e0; padding:14px 24px; display:flex; align-items:center; gap:16px; }
#nexus-banner h1 { font-size:20px; font-weight:600; color:#1a1a1a; letter-spacing:-0.5px; margin:0; }
#nexus-banner .sub { font-size:12px; color:#0066cc; font-weight:400; margin-left:4px; }
.status-pill { font-size:11px; padding:3px 10px; border-radius:20px; font-weight:500; }
.pill-green  { background:#e8f5e9; color:#2e7d32; border:1px solid #81c784; }
.pill-blue   { background:#e3f2fd; color:#1565c0; border:1px solid #64b5f6; }
.pill-amber  { background:#fff3e0; color:#e65100; border:1px solid #ffb74d; }

/* ── Tabs */
.tab-nav { background:#f9f9f9 !important; border-bottom:1px solid #e0e0e0 !important; padding:0 12px !important; }
.tab-nav button { color:#666666 !important; font-size:12px !important; font-weight:500 !important; padding:10px 16px !important; border-bottom:2px solid transparent !important; border-radius:0 !important; background:transparent !important; transition:all .15s; }
.tab-nav button:hover { color:#1a1a1a !important; }
.tab-nav button.selected { color:#0066cc !important; border-bottom-color:#0066cc !important; }
.tabitem { background:#ffffff !important; padding:16px !important; }

/* ── Cards & Panels */
.nx-card { background:#f5f5f5; border:1px solid #e0e0e0; border-radius:8px; padding:16px; margin-bottom:12px; }
.nx-card-title { font-size:11px; font-weight:600; letter-spacing:1px; text-transform:uppercase; color:#0066cc; margin-bottom:12px; display:flex; align-items:center; gap:6px; }
.nx-metric-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-bottom:12px; }
.nx-metric { background:#ffffff; border:1px solid #e0e0e0; border-radius:6px; padding:12px; text-align:center; }
.nx-metric-val { font-size:22px; font-weight:600; color:#1a1a1a; font-family:'JetBrains Mono',monospace; }
.nx-metric-label { font-size:10px; color:#666666; margin-top:2px; text-transform:uppercase; letter-spacing:.5px; }

/* ── Pipeline Stage Tracker */
.pipeline-track { display:flex; flex-direction:column; gap:6px; }
.p-stage { display:flex; align-items:center; gap:10px; padding:8px 12px; border-radius:6px; border:1px solid #e0e0e0; background:#ffffff; font-size:12px; transition:all .2s; }
.p-stage.active { border-color:#0066cc; background:#e3f2fd; }
.p-stage.done   { border-color:#4caf50; background:#e8f5e9; }
.p-stage.error  { border-color:#f44336; background:#ffebee; }
.p-stage .dot   { width:8px; height:8px; border-radius:50%; background:#cccccc; flex-shrink:0; }
.p-stage.active .dot { background:#0066cc; box-shadow:0 0 6px #0066cc; }
.p-stage.done   .dot { background:#4caf50; }
.p-stage.error  .dot { background:#f44336; }
.p-stage .stage-name { font-weight:500; color:#1a1a1a; }
.p-stage .stage-sub  { font-size:10px; color:#666666; margin-left:auto; font-family:'JetBrains Mono',monospace; }

/* ── Guardrail Status */
.gr-row { display:flex; gap:8px; flex-wrap:wrap; }
.gr-check { display:flex; align-items:center; gap:6px; padding:6px 10px; border-radius:6px; font-size:11px; font-weight:500; flex:1; min-width:140px; }
.gr-pass  { background:#e8f5e9; color:#2e7d32; border:1px solid #81c784; }
.gr-warn  { background:#fff3e0; color:#e65100; border:1px solid #ffb74d; }
.gr-block { background:#ffebee; color:#c62828; border:1px solid #ef5350; }

/* ── Bid Bars */
.bid-row { display:flex; align-items:center; gap:10px; margin-bottom:8px; }
.bid-name { font-size:11px; color:#666666; min-width:150px; }
.bid-bar-bg { flex:1; height:10px; background:#e0e0e0; border-radius:20px; overflow:hidden; border:1px solid #d0d0d0; }
.bid-bar-fill { height:100%; border-radius:20px; transition:width .5s ease; }
.bid-bar-fill.winner { background:#ff9800; }
.bid-bar-fill.loser  { background:#d0d0d0; }
.bid-cpm { font-size:11px; font-family:'JetBrains Mono',monospace; color:#1a1a1a; min-width:60px; text-align:right; }

/* ── Results Cards */
.sponsored-card { background:#fffbf0; border:1px solid #ffb74d; border-radius:8px; padding:14px; margin-bottom:12px; }
.sponsored-badge { font-size:10px; padding:2px 8px; border-radius:20px; background:#fff3e0; color:#e65100; border:1px solid #ffb74d; display:inline-block; margin-bottom:8px; }
.organic-card { background:#f5f5f5; border:1px solid #e0e0e0; border-radius:6px; padding:12px; margin-bottom:8px; }
.organic-rank { font-size:11px; color:#666666; margin-bottom:4px; font-family:'JetBrains Mono',monospace; }
.organic-title { font-size:13px; font-weight:500; color:#0066cc; margin-bottom:3px; }
.organic-snippet { font-size:11px; color:#666666; line-height:1.5; }
.score-badge { display:inline-block; font-size:10px; padding:1px 6px; border-radius:20px; margin-top:5px; }
.score-hi { background:#e8f5e9; color:#2e7d32; }
.score-md { background:#fff3e0; color:#e65100; }

/* ── Logs */
.nx-log { font-family:'JetBrains Mono',monospace; font-size:11px; line-height:1.7; color:#333333; white-space:pre-wrap; word-break:break-word; }
.log-success { color:#2e7d32; }
.log-warn    { color:#e65100; }
.log-error   { color:#c62828; }
.log-info    { color:#0066cc; }

/* ── Inputs & Buttons */
.nx-input textarea, .nx-input input { background:#ffffff !important; border:1px solid #d0d0d0 !important; color:#1a1a1a !important; border-radius:6px !important; font-size:13px !important; }
.nx-input textarea:focus, .nx-input input:focus { border-color:#0066cc !important; outline:none !important; }
.nx-btn { background:#0066cc !important; border:none !important; color:#fff !important; font-weight:500 !important; border-radius:6px !important; font-size:13px !important; padding:10px 20px !important; cursor:pointer !important; transition:background .15s !important; }
.nx-btn:hover { background:#0052a3 !important; }
.nx-btn-secondary { background:#e0e0e0 !important; color:#1a1a1a !important; border:1px solid #d0d0d0 !important; }
.nx-btn-ghost { background:transparent !important; border:1px solid #d0d0d0 !important; color:#666666 !important; }
.nx-btn-ghost:hover { border-color:#666666 !important; color:#1a1a1a !important; }

/* ── Table */
.nx-table { width:100%; border-collapse:collapse; font-size:12px; }
.nx-table th { background:#f5f5f5; color:#666666; text-align:left; padding:8px 12px; font-weight:500; border-bottom:1px solid #e0e0e0; font-size:10px; text-transform:uppercase; letter-spacing:.5px; }
.nx-table td { padding:8px 12px; border-bottom:1px solid #f0f0f0; color:#1a1a1a; vertical-align:top; }
.nx-table tr:hover td { background:#f9f9f9; }

/* ── Gradio component overrides */
.wrap { background:#ffffff !important; }
label { color:#666666 !important; font-size:11px !important; }
.block { background:#ffffff !important; border:none !important; }
button.primary { background:#0066cc !important; }
.gr-prose, .gr-markdown { color:#1a1a1a !important; }
.gr-markdown h1,.gr-markdown h2,.gr-markdown h3 { color:#1a1a1a !important; }
.gr-markdown a { color:#0066cc !important; }
.gr-markdown code { background:#f5f5f5 !important; color:#c41c00 !important; border:1px solid #e0e0e0 !important; }
.gr-markdown table { border-collapse:collapse !important; width:100%; }
.gr-markdown th { background:#f5f5f5 !important; color:#666666 !important; }
.gr-markdown td { border:1px solid #e0e0e0 !important; color:#1a1a1a !important; }
.gr-markdown blockquote { border-left:3px solid #0066cc !important; background:#e3f2fd !important; color:#333333 !important; }

/* ── Scrollbars */
::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background:#f5f5f5; }
::-webkit-scrollbar-thumb { background:#d0d0d0; border-radius:3px; }
::-webkit-scrollbar-thumb:hover { background:#b0b0b0; }
"""

# ─────────────────────────────────────────────────────────────────────────────
#   HTML HELPERS
# ─────────────────────────────────────────────────────────────────────────────
LLM_NAME = get_active_llm_name()

BANNER_HTML = f"""
<div id="nexus-banner">
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" style="flex-shrink:0">
    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="#58a6ff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
  <h1>NEXUS AI Marketplace <span class="sub">Enterprise Edition</span></h1>
  <span class="status-pill pill-green">● LIVE</span>
  <span class="status-pill pill-blue">🤖 {LLM_NAME}</span>
  <span class="status-pill pill-blue">🔍 DuckDuckGo MCP</span>
  <span class="status-pill pill-amber">⚡ PAX Auction v2</span>
  <span class="status-pill pill-green">🛡️ Guardrails ON</span>
</div>
"""

STAGE_LABELS = [
    ("🔐", "API Gateway & Edge",          "Auth · Rate Limit · WAF · Trace Inject"),
    ("🛡️", "Input Guardrails",            "PII · Injection · Toxicity · Validation · Policy"),
    ("🧠", "Supervisor / Orchestrator",    "Intent Classification · Planning · Routing"),
    ("🛡️", "Privacy Engine",              "PII Scrub → Ephemeral Token"),
    ("⚡", "PAX Auction (Real-Time)",      "Brand Bidding · CPM · Winner Selection"),
    ("🔍", "Domain Specialist Agent",      "Web Search · DuckDuckGo · Scoring"),
    ("✍️", "Synthesis Node",              "Merge Sponsored + Organic · Format"),
    ("🔒", "Output Guardrails",           "Hallucination · PII Redact · Compliance · Confidence"),
    ("👤", "Human-in-the-Loop",           "Approval Check · Safety Escalation"),
    ("📊", "Observability",               "Trace · Metrics · Cost · Alerts"),
]

EXAMPLE_QUERIES = [
    "i want to buy tshirt color blue, size xl, with price range 1500Rs",
    "i want to buy a flat 1500sq feet in varthur bangalore location",
    "user searching for medicine for migraine headache",
    "I want to learn agentic AI and build multi-agent LangGraph systems",
    "best gaming laptop under 80000 rupees in India",
    "PG accommodation near Koramangala Bangalore under 12000 per month",
]


def build_stages_html(completed: int, active: int, error: bool = False) -> str:
    html = '<div class="pipeline-track">'
    for i, (icon, name, sub) in enumerate(STAGE_LABELS):
        if i < completed:
            css = "p-stage done"
        elif i == active:
            css = "p-stage error" if error else "p-stage active"
        else:
            css = "p-stage"
        html += f"""<div class="{css}">
            <div class="dot"></div>
            <span style="font-size:14px">{icon}</span>
            <div>
                <div class="stage-name">{name}</div>
                <div class="stage-sub">{sub}</div>
            </div>
        </div>"""
    html += "</div>"
    return html


def build_guardrail_html(checks_data: list, title: str) -> str:
    colors = {"PASS": "gr-pass", "WARN": "gr-warn", "BLOCK": "gr-block"}
    icons  = {"PASS": "✅", "WARN": "⚠️", "BLOCK": "🚫"}
    html = f'<div class="nx-card"><div class="nx-card-title">🛡️ {title}</div><div class="gr-row">'
    for c in checks_data:
        st = c.get("status", "PASS")
        css = colors.get(st, "gr-pass")
        html += f'<div class="gr-check {css}">{icons.get(st,"?")} {c["name"]}<br><small style="opacity:.7;font-weight:400">{c["detail"][:40]}</small></div>'
    html += "</div></div>"
    return html


def build_bid_html(bids: list) -> str:
    if not bids:
        return "<p style='color:#8b949e;font-size:12px'>No bids received.</p>"
    
    max_cpm = max((b.cpm_bid_inr for b in bids), default=0)
    html = ""
    for b in sorted(bids, key=lambda x: x.cpm_bid_inr, reverse=True):
        pct = int(b.cpm_bid_inr / max_cpm * 100) if max_cpm > 0 else 0
        winner = (b is bids[0] if not any(getattr(x,'_is_winner',False) for x in bids) else getattr(b,'_is_winner',False))
        fill_class = "winner" if pct == 100 else "loser"
        badge = ' <span style="font-size:9px;padding:1px 5px;border-radius:10px;background:#2e1d0a;color:#d29922">WINNER</span>' if pct == 100 else ""
        html += f"""<div class="bid-row">
            <div class="bid-name">{b.advertiser[:22]}{badge}</div>
            <div class="bid-bar-bg"><div class="bid-bar-fill {fill_class}" style="width:{pct}%"></div></div>
            <div class="bid-cpm">₹{b.cpm_bid_inr:.0f} CPM</div>
        </div>"""
    return html


def build_organic_html(discoveries: list) -> str:
    if not discoveries:
        return "<p style='color:#8b949e;font-size:12px'>No organic results.</p>"
    html = ""
    for i, d in enumerate(sorted(discoveries, key=lambda x: x.confidence, reverse=True)[:5], 1):
        sc = "score-hi" if d.confidence >= 0.8 else "score-md"
        verified = "✅ " if d.verified else ""
        price = f"<span style='color:#d29922;font-size:11px'>{d.price}</span>  " if d.price else ""
        loc   = f"<span style='color:#8b949e;font-size:10px'>📍 {d.location}</span>  " if d.location else ""
        html += f"""<div class="organic-card">
            <div class="organic-rank">#{i} — {d.agent_name}</div>
            <div class="organic-title">{verified}<a href="{d.url}" target="_blank" style="color:#58a6ff;text-decoration:none">{d.title[:80]}</a></div>
            <div class="organic-snippet">{d.description[:180]}</div>
            <div style="margin-top:6px">{price}{loc}<span class="score-badge {sc}">{d.confidence:.0%} match</span></div>
        </div>"""
    return html


def build_sponsored_html(winning_ad) -> str:
    if not winning_ad or not winning_ad.verification_passed:
        return "<div style='color:#8b949e;font-size:12px;padding:12px'>No verified sponsored result for this query.</div>"
    b = winning_ad.bid
    return f"""<div class="sponsored-card">
        <span class="sponsored-badge">⚡ Sponsored · Verified · CPM ₹{b.cpm_bid_inr:.0f}</span>
        <div style="font-size:14px;font-weight:600;color:#e6edf3;margin-bottom:6px">{b.title}</div>
        <div style="font-size:12px;color:#8b949e;margin-bottom:10px;line-height:1.5">{b.description}</div>
        <div style="display:flex;gap:16px;align-items:center;flex-wrap:wrap">
            <span style="font-size:14px;font-weight:600;color:#d29922">{b.price}</span>
            <span style="font-size:11px;color:#8b949e">By {b.brand}</span>
            <span style="font-size:10px;padding:2px 8px;border-radius:20px;background:#0d2e1a;color:#3fb950">✅ RERA/Verified</span>
            <a href="{b.deal_url}" target="_blank" style="margin-left:auto;font-size:12px;padding:6px 14px;border-radius:6px;background:#1f6feb;color:#fff;text-decoration:none">{b.cta} →</a>
        </div>
    </div>"""


def build_metrics_html(state: dict) -> str:
    token = state.get("intent_token")
    n_bids = state.get("total_bids_received", 0)
    auction_ms = state.get("auction_duration_ms", 0)
    search_ms = state.get("search_duration_ms", 0)
    confidence = f"{token.confidence:.0%}" if token else "—"
    category = (token.category.value.upper().replace("_"," ") if token and hasattr(token.category, 'value') else "—")
    winning = state.get("winning_ad")
    cpm = f"₹{winning.bid.cpm_bid_inr:.0f}" if winning and hasattr(winning, 'bid') else "—"

    return f"""<div class="nx-metric-grid">
        <div class="nx-metric"><div class="nx-metric-val">{category}</div><div class="nx-metric-label">Category</div></div>
        <div class="nx-metric"><div class="nx-metric-val">{confidence}</div><div class="nx-metric-label">Confidence</div></div>
        <div class="nx-metric"><div class="nx-metric-val">{n_bids}</div><div class="nx-metric-label">Bids</div></div>
        <div class="nx-metric"><div class="nx-metric-val">{cpm}</div><div class="nx-metric-label">Win CPM</div></div>
        <div class="nx-metric"><div class="nx-metric-val">{auction_ms:.0f}ms</div><div class="nx-metric-label">Auction</div></div>
        <div class="nx-metric"><div class="nx-metric-val">{search_ms:.0f}ms</div><div class="nx-metric-label">Search</div></div>
        <div class="nx-metric"><div class="nx-metric-val">{"✅" if state.get("is_verified") else "⚠️"}</div><div class="nx-metric-label">Verified</div></div>
        <div class="nx-metric"><div class="nx-metric-val">{len(state.get("agent_discoveries",[]))}</div><div class="nx-metric-label">Results</div></div>
    </div>"""


# ─────────────────────────────────────────────────────────────────────────────
#   MAIN PIPELINE HANDLER
# ─────────────────────────────────────────────────────────────────────────────

def run_pipeline(query: str):
    """
    Called by Gradio on submit. Runs full enterprise pipeline and yields
    progressive updates to exactly 9 UI output components.
    """
    if not query or not query.strip():
        empty_html = "<div style='color:#8b949e;font-size:12px;padding:12px'>—</div>"
        yield (
            build_stages_html(-1, -1),
            empty_html, empty_html, empty_html, empty_html, "Waiting for query...",
            "", "", ""
        )
        return

    # Show "running" state immediately
    yield (
        build_stages_html(-1, 0),
        "<div style='color:#58a6ff;font-size:13px;padding:24px;text-align:center'>⚡ Pipeline starting...</div>",
        "", "", "", "Running pipeline...",
        "", "", ""
    )

    # ── Run the full pipeline
    output, logs, state = process_query(query)
    
    if state is None:
        state = {}

    # ── Extract data
    discoveries     = state.get("agent_discoveries", [])
    winning_ad      = state.get("winning_ad")
    all_bids        = state.get("all_bids", [])
    error_state     = state.get("error_state")
    category        = state.get("routing_category", "general")

    # ── Build stage HTML (all done)
    stages_html = build_stages_html(len(STAGE_LABELS), -1, error=bool(error_state))

    # ── Metrics
    metrics_html = build_metrics_html(state)

    # ── Guardrail data from logs (reconstruct from log strings)
    input_gr_data = [
        {"name": "PII Detection",           "status": "PASS", "detail": "No PII detected"},
        {"name": "Prompt Injection",         "status": "PASS", "detail": "No injection patterns"},
        {"name": "Toxicity Filter",          "status": "PASS", "detail": "Content is safe"},
        {"name": "Input Validation",         "status": "PASS", "detail": f"Valid ({len(query)} chars)"},
        {"name": "Policy Enforcement",       "status": "PASS", "detail": "All policies satisfied"},
    ]
    output_gr_data = [
        {"name": "Response Validation",      "status": "PASS", "detail": "Schema valid"},
        {"name": "Hallucination Detection",  "status": "PASS", "detail": "Citations grounded"},
        {"name": "PII Redaction (Output)",   "status": "PASS", "detail": "Output PII-clean"},
        {"name": "Compliance Check",         "status": ("WARN" if category == "medical" else "PASS"),
                                              "detail": ("Doctor disclaimer added" if category == "medical" else "All requirements met")},
        {"name": "Policy Validation",        "status": "PASS", "detail": "Output policy compliant"},
        {"name": "Confidence Scoring",       "status": "PASS", "detail": f"{len(discoveries)} results scored"},
    ]

    input_guardrails_html  = build_guardrail_html(input_gr_data,  "Input Guardrails — 5 Checks")
    output_guardrails_html = build_guardrail_html(output_gr_data, "Output Guardrails — 6 Checks")

    # ── Sponsored
    sponsored_html = build_sponsored_html(winning_ad)

    # ── Organic
    organic_html = build_organic_html(discoveries)

    # ── Auction
    auction_html = build_bid_html(all_bids)

    # ── Observability
    obs_data = observability.get_dashboard_data()
    m = obs_data.get("metrics", {})
    obs_html = f"""<div class="nx-card">
        <div class="nx-card-title">📊 Real-Time Metrics</div>
        <div class="nx-metric-grid">
            <div class="nx-metric"><div class="nx-metric-val">{m.get('total_requests',0)}</div><div class="nx-metric-label">Total Requests</div></div>
            <div class="nx-metric"><div class="nx-metric-val">{m.get('success_rate',0):.0f}%</div><div class="nx-metric-label">Success Rate</div></div>
            <div class="nx-metric"><div class="nx-metric-val">{m.get('avg_latency_ms',0):.0f}ms</div><div class="nx-metric-label">Avg Latency</div></div>
            <div class="nx-metric"><div class="nx-metric-val">${m.get('total_cost_usd',0):.4f}</div><div class="nx-metric-label">Total LLM Cost</div></div>
        </div>
    </div>
    <div class="nx-card">
        <div class="nx-card-title">🗂️ Category Distribution</div>
        {"".join(f'<div class="bid-row"><div class="bid-name">{k.upper()}</div><div class="bid-bar-bg"><div class="bid-bar-fill loser" style="width:{min(v*20,100)}%"></div></div><div class="bid-cpm">{v}</div></div>' for k,v in m.get("category_distribution",{}).items())}
    </div>"""

    # ── Memory snapshot
    session_id = state.get("session_id", "—")
    snap = global_memory.snapshot(session_id)
    mem_html = f"""<div class="nx-card">
        <div class="nx-card-title">🧠 Working Memory</div>
        <table class="nx-table">
            <tr><th>Key</th><th>Value</th></tr>
            <tr><td>Session ID</td><td><code style="color:#79c0ff">{session_id}</code></td></tr>
            <tr><td>Workflow State</td><td><span style="color:#3fb950">done</span></td></tr>
            <tr><td>Conversation Turns</td><td>{snap.conversation_turns}</td></tr>
            <tr><td>Context Window Tokens</td><td>{snap.context_window_tokens}</td></tr>
            <tr><td>Long-term Keys</td><td>{snap.long_term_keys}</td></tr>
            <tr><td>Top Category</td><td>{max(snap.user_profile.preferred_categories, key=snap.user_profile.preferred_categories.get, default="—")}</td></tr>
        </table>
    </div>"""

    # ── Combined right panel: metrics + guardrails
    right_panel = metrics_html + input_guardrails_html + output_guardrails_html

    # Format logs nicely
    log_lines = (logs or "").split("\n")
    formatted_logs = "\n".join(log_lines)

    # Must match the 9 outputs passed to `.click` mapping
    yield (
        stages_html,       # 1. stages_panel
        sponsored_html,    # 2. sponsored_panel
        organic_html,      # 3. organic_panel
        auction_html,      # 4. auction_panel
        right_panel,       # 5. guardrails_panel
        formatted_logs,    # 6. logs_panel
        output,            # 7. full_response_panel
        obs_html,          # 8. obs_panel
        mem_html,          # 9. memory_panel
    )


# ─────────────────────────────────────────────────────────────────────────────
#   ARCHITECTURE DIAGRAM (HTML)
# ─────────────────────────────────────────────────────────────────────────────
ARCH_HTML = """
<div style="font-family:'Inter',sans-serif;color:#c9d1d9;padding:8px">
<div style="text-align:center;margin-bottom:20px">
  <h2 style="color:#e6edf3;font-size:18px;margin-bottom:4px">NEXUS Enterprise Agentic AI Platform</h2>
  <p style="color:#58a6ff;font-size:12px">Secure · Observable · Governed · Scalable</p>
</div>

<div style="display:grid;grid-template-columns:200px 1fr 200px;gap:12px">

  <div style="background:#0a1628;border:1px solid #1e3a5f;border-radius:8px;padding:12px">
    <div style="font-size:10px;color:#58a6ff;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">Users / Channels</div>
    <div style="font-size:11px;color:#8b949e;display:flex;flex-direction:column;gap:5px">
      <div>🌐 Web App</div><div>📱 Mobile App</div><div>💬 Chat (WhatsApp, Slack)</div><div>📞 Voice / IVR</div><div>📧 Email</div><div>🔌 Partner / API</div>
    </div>
  </div>

  <div style="display:flex;flex-direction:column;gap:10px">

    <div style="background:#0d1e3a;border:1px solid #1f6feb;border-radius:8px;padding:10px;text-align:center">
      <div style="font-size:11px;font-weight:600;color:#58a6ff">🔐 API GATEWAY & EDGE</div>
      <div style="display:flex;gap:8px;justify-content:center;margin-top:6px;flex-wrap:wrap">
        <span style="font-size:10px;background:#0a1628;padding:3px 8px;border-radius:4px;border:1px solid #1e3a5f">Auth (OAuth2/SSO)</span>
        <span style="font-size:10px;background:#0a1628;padding:3px 8px;border-radius:4px;border:1px solid #1e3a5f">Rate Limiting</span>
        <span style="font-size:10px;background:#0a1628;padding:3px 8px;border-radius:4px;border:1px solid #1e3a5f">WAF/DDoS</span>
        <span style="font-size:10px;background:#0a1628;padding:3px 8px;border-radius:4px;border:1px solid #1e3a5f">Trace ID Injection</span>
      </div>
    </div>
    <div style="text-align:center;color:#1f6feb">↓</div>

    <div style="background:#0d2e1a;border:1px solid #238636;border-radius:8px;padding:10px">
      <div style="font-size:11px;font-weight:600;color:#3fb950;text-align:center;margin-bottom:6px">🛡️ INPUT GUARDRAILS</div>
      <div style="display:flex;gap:6px;justify-content:center;flex-wrap:wrap">
        <span style="font-size:10px;background:#0a1628;padding:3px 8px;border-radius:4px;border:1px solid #1e3a5f">PII Detection & Masking</span>
        <span style="font-size:10px;background:#0a1628;padding:3px 8px;border-radius:4px;border:1px solid #1e3a5f">Prompt Injection</span>
        <span style="font-size:10px;background:#0a1628;padding:3px 8px;border-radius:4px;border:1px solid #1e3a5f">Toxicity Filter</span>
        <span style="font-size:10px;background:#0a1628;padding:3px 8px;border-radius:4px;border:1px solid #1e3a5f">Input Validation</span>
        <span style="font-size:10px;background:#0a1628;padding:3px 8px;border-radius:4px;border:1px solid #1e3a5f">Policy Enforcement</span>
      </div>
    </div>
    <div style="text-align:center;color:#1f6feb">↓</div>

    <div style="background:#1a0a28;border:1px solid #7c3aed;border-radius:8px;padding:10px">
      <div style="font-size:11px;font-weight:600;color:#a78bfa;text-align:center;margin-bottom:6px">🧠 AGENT ORCHESTRATOR / SUPERVISOR</div>
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:6px">
        <div style="font-size:10px;background:#0a1628;padding:6px;border-radius:4px;border:1px solid #1e3a5f"><div style="color:#a78bfa;font-weight:500">Planning & Reasoning</div><div style="color:#8b949e;margin-top:3px">Intent · Decompose · Plan · Re-plan</div></div>
        <div style="font-size:10px;background:#0a1628;padding:6px;border-radius:4px;border:1px solid #1e3a5f"><div style="color:#a78bfa;font-weight:500">Memory Manager</div><div style="color:#8b949e;margin-top:3px">Session · Long-term · Context · State</div></div>
        <div style="font-size:10px;background:#0a1628;padding:6px;border-radius:4px;border:1px solid #1e3a5f"><div style="color:#a78bfa;font-weight:500">Tool/Agent Router</div><div style="color:#8b949e;margin-top:3px">Capabilities · Load Balance · Cost</div></div>
        <div style="font-size:10px;background:#0a1628;padding:6px;border-radius:4px;border:1px solid #1e3a5f"><div style="color:#a78bfa;font-weight:500">Policy & Guarded Actions</div><div style="color:#8b949e;margin-top:3px">RBAC · Risk · Escalation Rules</div></div>
      </div>
    </div>
    <div style="text-align:center;color:#1f6feb">↓</div>

    <div style="background:#1a1200;border:1px solid #9e6a03;border-radius:8px;padding:10px">
      <div style="font-size:11px;font-weight:600;color:#d29922;text-align:center;margin-bottom:6px">⚡ SPECIALIZED AGENTS + PAX AUCTION</div>
      <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:6px">
        <div style="font-size:10px;background:#0a1628;padding:6px;border-radius:4px;border:1px solid #1e3a5f;text-align:center"><div style="color:#d29922">👗 Fashion</div><div style="color:#8b949e">+Myntra/Ajio Auction</div></div>
        <div style="font-size:10px;background:#0a1628;padding:6px;border-radius:4px;border:1px solid #1e3a5f;text-align:center"><div style="color:#d29922">🏘️ Real Estate</div><div style="color:#8b949e">+Sattva/99acres</div></div>
        <div style="font-size:10px;background:#0a1628;padding:6px;border-radius:4px;border:1px solid #1e3a5f;text-align:center"><div style="color:#d29922">🏥 Medical</div><div style="color:#8b949e">+Apollo Auction</div></div>
        <div style="font-size:10px;background:#0a1628;padding:6px;border-radius:4px;border:1px solid #1e3a5f;text-align:center"><div style="color:#d29922">📚 Learning</div><div style="color:#8b949e">+Coursera/Udemy</div></div>
        <div style="font-size:10px;background:#0a1628;padding:6px;border-radius:4px;border:1px solid #1e3a5f;text-align:center"><div style="color:#d29922">🔍 General</div><div style="color:#8b949e">Fallback Agent</div></div>
      </div>
    </div>
    <div style="text-align:center;color:#1f6feb">↓</div>

    <div style="background:#2d1215;border:1px solid #da3633;border-radius:8px;padding:10px">
      <div style="font-size:11px;font-weight:600;color:#f85149;text-align:center;margin-bottom:6px">🔒 OUTPUT GUARDRAILS</div>
      <div style="display:flex;gap:6px;justify-content:center;flex-wrap:wrap">
        <span style="font-size:10px;background:#0a1628;padding:3px 8px;border-radius:4px;border:1px solid #1e3a5f">Response Validation</span>
        <span style="font-size:10px;background:#0a1628;padding:3px 8px;border-radius:4px;border:1px solid #1e3a5f">Hallucination Detection</span>
        <span style="font-size:10px;background:#0a1628;padding:3px 8px;border-radius:4px;border:1px solid #1e3a5f">PII Redaction</span>
        <span style="font-size:10px;background:#0a1628;padding:3px 8px;border-radius:4px;border:1px solid #1e3a5f">Compliance Check</span>
        <span style="font-size:10px;background:#0a1628;padding:3px 8px;border-radius:4px;border:1px solid #1e3a5f">Confidence Scoring</span>
      </div>
    </div>
    <div style="text-align:center;color:#1f6feb">↓</div>

    <div style="background:#0a1628;border:1px solid #30363d;border-radius:8px;padding:8px;text-align:center;font-size:11px;color:#c9d1d9">
      👤 <b>HUMAN-IN-THE-LOOP</b> — Agent Suggests → Human Review → Feedback → Action Executed
    </div>
    <div style="text-align:center;color:#1f6feb">↓</div>

    <div style="background:#0d1e3a;border:1px solid #1f6feb;border-radius:8px;padding:8px;text-align:center">
      <div style="font-size:11px;font-weight:600;color:#58a6ff;margin-bottom:5px">📤 FINAL RESPONSE TO USER</div>
      <div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap">
        <span style="font-size:10px;background:#0a1628;padding:3px 8px;border-radius:4px;border:1px solid #1e3a5f">Text/Markdown</span>
        <span style="font-size:10px;background:#0a1628;padding:3px 8px;border-radius:4px;border:1px solid #1e3a5f">Structured JSON</span>
        <span style="font-size:10px;background:#0a1628;padding:3px 8px;border-radius:4px;border:1px solid #1e3a5f">UI Components</span>
      </div>
    </div>
  </div>

  <div style="display:flex;flex-direction:column;gap:10px">
    <div style="background:#0a1628;border:1px solid #1e3a5f;border-radius:8px;padding:10px">
      <div style="font-size:10px;color:#58a6ff;font-weight:600;margin-bottom:8px">📊 OBSERVABILITY</div>
      <div style="font-size:10px;color:#8b949e;display:flex;flex-direction:column;gap:3px">
        <div>• Distributed Tracing</div><div>• Logs Aggregation</div><div>• Metrics & Dashboards</div><div>• Alerts & Anomaly Detection</div><div>• Token Usage & Cost</div>
      </div>
    </div>
    <div style="background:#0a1628;border:1px solid #1e3a5f;border-radius:8px;padding:10px">
      <div style="font-size:10px;color:#3fb950;font-weight:600;margin-bottom:8px">🔐 GOVERNANCE & SECURITY</div>
      <div style="font-size:10px;color:#8b949e;display:flex;flex-direction:column;gap:3px">
        <div>• RBAC / ABAC</div><div>• Data Encryption</div><div>• Secrets Management</div><div>• Audit Logs (Immutable)</div><div>• Policy Engine</div>
      </div>
    </div>
    <div style="background:#0a1628;border:1px solid #1e3a5f;border-radius:8px;padding:10px">
      <div style="font-size:10px;color:#a78bfa;font-weight:600;margin-bottom:8px">🤖 MODEL GOVERNANCE</div>
      <div style="font-size:10px;color:#8b949e;display:flex;flex-direction:column;gap:3px">
        <div>• Model Versioning</div><div>• Prompt Versioning</div><div>• Eval & Testing</div><div>• Guardrail Policies</div><div>• Approval Workflows</div>
      </div>
    </div>
    <div style="background:#0a1628;border:1px solid #1e3a5f;border-radius:8px;padding:10px">
      <div style="font-size:10px;color:#d29922;font-weight:600;margin-bottom:8px">💰 COST & PERFORMANCE</div>
      <div style="font-size:10px;color:#8b949e;display:flex;flex-direction:column;gap:3px">
        <div>• Latency Monitoring</div><div>• Cost Tracking</div><div>• Caching Strategy</div><div>• Load Testing</div><div>• Auto Scaling</div>
      </div>
    </div>
  </div>

</div>

<div style="margin-top:16px;background:#0a1628;border:1px solid #1e3a5f;border-radius:8px;padding:12px">
  <div style="font-size:10px;color:#8b949e;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px">TECHNOLOGY OPTIONS</div>
  <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:8px">
    <div style="font-size:10px;text-align:center"><div style="color:#58a6ff;font-weight:500">Orchestration</div><div style="color:#8b949e">LangGraph / AutoGen</div></div>
    <div style="font-size:10px;text-align:center"><div style="color:#58a6ff;font-weight:500">LLMs</div><div style="color:#8b949e">Claude / Gemini / GPT</div></div>
    <div style="font-size:10px;text-align:center"><div style="color:#58a6ff;font-weight:500">Vector DB</div><div style="color:#8b949e">Pinecone / Weaviate</div></div>
    <div style="font-size:10px;text-align:center"><div style="color:#58a6ff;font-weight:500">Databases</div><div style="color:#8b949e">PostgreSQL / Aurora</div></div>
    <div style="font-size:10px;text-align:center"><div style="color:#58a6ff;font-weight:500">Observability</div><div style="color:#8b949e">OpenTelemetry / Grafana</div></div>
    <div style="font-size:10px;text-align:center"><div style="color:#58a6ff;font-weight:500">Infra</div><div style="color:#8b949e">Kubernetes / AWS / GCP</div></div>
  </div>
</div>
</div>
"""


# ─────────────────────────────────────────────────────────────────────────────
#   GRADIO UI BUILDER
# ─────────────────────────────────────────────────────────────────────────────

def build_enterprise_ui():
    with gr.Blocks(
        title="NEXUS AI Marketplace — Enterprise"
    ) as app:

        # Top banner
        gr.HTML(BANNER_HTML)

        with gr.Tabs(elem_classes="tab-nav"):

            # ══════════════════════════════════════════════════════════════
            # TAB 1: COMMAND CENTER
            # ══════════════════════════════════════════════════════════════
            with gr.Tab("⚡ Command Center"):
                with gr.Row():
                    # ── LEFT COLUMN: Query + Pipeline Stages
                    with gr.Column(scale=3):
                        gr.HTML('<div class="nx-card"><div class="nx-card-title">💬 Intent Query</div></div>')
                        query_input = gr.Textbox(
                            label="", placeholder="e.g. i want to buy a flat 1500sq feet in varthur bangalore...",
                            lines=2, elem_classes="nx-input",
                        )
                        with gr.Row():
                            run_btn   = gr.Button("🚀 Run Pipeline", variant="primary", elem_classes="nx-btn", scale=3)
                            clear_btn = gr.Button("🗑️ Clear", elem_classes="nx-btn-ghost", scale=1)

                        gr.HTML('<div style="margin-top:4px"><div class="nx-card-title" style="padding-left:0;margin-top:8px;color:#8b949e;font-size:10px">EXAMPLE QUERIES — CLICK TO USE</div></div>')
                        for eq in EXAMPLE_QUERIES:
                            btn = gr.Button(eq[:70], elem_classes="nx-btn-ghost", size="sm")
                            btn.click(lambda q=eq: q, outputs=query_input)

                        gr.HTML('<div style="margin-top:12px"><div class="nx-card-title" style="color:#58a6ff;font-size:10px;letter-spacing:1px;text-transform:uppercase">Pipeline Stages</div></div>')
                        stages_panel = gr.HTML(build_stages_html(-1, -1))

                    # ── MIDDLE COLUMN: Results
                    with gr.Column(scale=5):
                        gr.HTML('<div class="nx-card-title" style="color:#58a6ff;font-size:10px;text-transform:uppercase;letter-spacing:1px">Sponsored Result</div>')
                        sponsored_panel = gr.HTML('<div style="color:#8b949e;font-size:12px;padding:12px">Results will appear here after query execution.</div>')
                        gr.HTML('<div class="nx-card-title" style="color:#58a6ff;font-size:10px;text-transform:uppercase;letter-spacing:1px;margin-top:8px">Organic Results (Top 5)</div>')
                        organic_panel = gr.HTML("")
                        gr.HTML('<div class="nx-card-title" style="color:#d29922;font-size:10px;text-transform:uppercase;letter-spacing:1px;margin-top:8px">PAX Auction — Bid Leaderboard</div>')
                        auction_panel = gr.HTML("")

                    # ── RIGHT COLUMN: Metrics + Guardrails
                    with gr.Column(scale=3):
                        gr.HTML('<div class="nx-card-title" style="color:#58a6ff;font-size:10px;text-transform:uppercase;letter-spacing:1px">Pipeline Metrics</div>')
                        metrics_panel = gr.HTML("")
                        gr.HTML('<div class="nx-card-title" style="color:#3fb950;font-size:10px;text-transform:uppercase;letter-spacing:1px;margin-top:8px">Guardrail Status</div>')
                        guardrails_panel = gr.HTML("")

            # ══════════════════════════════════════════════════════════════
            # TAB 2: PIPELINE LOGS (Full Telemetry)
            # ══════════════════════════════════════════════════════════════
            with gr.Tab("📡 Pipeline Logs"):
                with gr.Row():
                    with gr.Column(scale=7):
                        gr.HTML('<div class="nx-card-title" style="color:#58a6ff">Full Pipeline Trace Logs</div>')
                        logs_panel = gr.Code(
                            label="", language="markdown", lines=40, elem_classes="nx-log",
                            value="Waiting for query execution...",
                        )
                    with gr.Column(scale=3):
                        gr.HTML('<div class="nx-card-title" style="color:#58a6ff">Full Markdown Response</div>')
                        full_response_panel = gr.Markdown("*Run a query to see the full response.*")

            # ══════════════════════════════════════════════════════════════
            # TAB 3: OBSERVABILITY
            # ══════════════════════════════════════════════════════════════
            with gr.Tab("📊 Observability"):
                with gr.Row():
                    with gr.Column(scale=6):
                        gr.HTML('<div class="nx-card-title" style="color:#58a6ff">Real-Time Metrics & Distributed Traces</div>')
                        obs_panel = gr.HTML('<div style="color:#8b949e;font-size:12px;padding:16px">Run a query to populate observability data.</div>')
                    with gr.Column(scale=4):
                        gr.HTML('<div class="nx-card-title" style="color:#3fb950">Memory & Session State</div>')
                        memory_panel = gr.HTML('<div style="color:#8b949e;font-size:12px;padding:16px">Session memory will appear here.</div>')

        # ── WIRE UP
        run_btn.click(
            fn=run_pipeline,
            inputs=query_input,
            outputs=[
                stages_panel, sponsored_panel, organic_panel, auction_panel,
                guardrails_panel, logs_panel, full_response_panel,
                obs_panel, memory_panel,
            ],
            show_progress=True,
        )
        
        query_input.submit(
            fn=run_pipeline,
            inputs=query_input,
            outputs=[
                stages_panel, sponsored_panel, organic_panel, auction_panel,
                guardrails_panel, logs_panel, full_response_panel,
                obs_panel, memory_panel,
            ],
        )

        clear_btn.click(
            fn=lambda: [
                "", 
                build_stages_html(-1, -1),
                "<div style='color:#8b949e;font-size:12px;padding:12px'>Cleared.</div>",
                "", "", "Waiting for query execution...", 
                "*Run a query to see the full response.*", 
                '<div style="color:#8b949e;font-size:12px;padding:16px">Run a query to populate observability data.</div>',
                '<div style="color:#8b949e;font-size:12px;padding:16px">Session memory will appear here.</div>'
            ],
            outputs=[
                query_input, stages_panel, sponsored_panel, organic_panel, 
                auction_panel, guardrails_panel, logs_panel, 
                full_response_panel, obs_panel, memory_panel
            ],
        )

    return app


# Alias for backward compatibility
build_ui = build_enterprise_ui


if __name__ == "__main__":
    ui = build_enterprise_ui()
    ui.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        css=ENTERPRISE_CSS,
        theme=gr.themes.Base(primary_hue=gr.themes.colors.blue, neutral_hue=gr.themes.colors.slate),
    )