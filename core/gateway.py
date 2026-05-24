"""
NEXUS AI Marketplace - API Gateway & Edge Layer
Implements: Authentication (OAuth2/SSO sim), Rate Limiting, Request Routing,
            WAF/DDoS Protection, Trace ID Injection

From the Enterprise Agentic AI Platform diagram (API Gateway & Edge node).
"""

import time
import uuid
import hashlib
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, Optional, Tuple


@dataclass
class GatewayRequest:
    trace_id: str
    session_id: str
    user_tier: str           # "free" | "pro" | "enterprise"
    request_id: str
    timestamp: float
    rate_limit_key: str
    authenticated: bool
    waf_score: float         # 0.0 = clean, 1.0 = blocked


@dataclass
class GatewayResult:
    allowed: bool
    request: GatewayRequest
    block_reason: Optional[str] = None
    latency_ms: float = 0.0


# ─────────────────────────────────────────────
#  RATE LIMITER
# ─────────────────────────────────────────────

class RateLimiter:
    _windows: Dict[str, deque] = defaultdict(lambda: deque())
    _limits = {
        "free":       (10, 60),    # 10 req per 60s
        "pro":        (60, 60),    # 60 req per 60s
        "enterprise": (500, 60),   # 500 req per 60s
    }

    @classmethod
    def check(cls, key: str, tier: str) -> Tuple[bool, int, int]:
        """Returns (allowed, remaining, reset_in_seconds)."""
        limit, window = cls._limits.get(tier, (10, 60))
        now = time.time()
        dq = cls._windows[key]
        # Evict old entries
        while dq and now - dq[0] > window:
            dq.popleft()

        count = len(dq)
        if count >= limit:
            reset_in = int(window - (now - dq[0])) if dq else window
            return False, 0, reset_in

        dq.append(now)
        return True, limit - count - 1, window


# ─────────────────────────────────────────────
#  WAF (Web Application Firewall)
# ─────────────────────────────────────────────

class WAF:
    """Simulated WAF — blocks known attack patterns."""
    _ATTACK_SIGNATURES = [
        "' OR 1=1",
        "<script>",
        "UNION SELECT",
        "DROP TABLE",
        "../../../",
        "cmd.exe",
        "wget http",
        "curl http",
    ]

    @classmethod
    def score(cls, payload: str) -> Tuple[float, str]:
        """Returns (risk_score, reason). Score 0.0=safe, 1.0=blocked."""
        pl = payload.lower()
        for sig in cls._ATTACK_SIGNATURES:
            if sig.lower() in pl:
                return 1.0, f"WAF signature match: {sig}"

        # Length-based heuristic
        if len(payload) > 5000:
            return 0.6, "Oversized payload"

        return 0.0, "Clean"


# ─────────────────────────────────────────────
#  AUTH SIMULATOR (OAuth2/SSO)
# ─────────────────────────────────────────────

class AuthEngine:
    """Simulates OAuth2/SSO validation for the POC."""
    _API_KEYS = {
        "demo-key-free":       "free",
        "demo-key-pro":        "pro",
        "demo-key-enterprise": "enterprise",
    }

    @classmethod
    def validate(cls, api_key: Optional[str]) -> Tuple[bool, str]:
        """Returns (authenticated, tier)."""
        if not api_key:
            return True, "free"     # POC: default to free tier for demo
        tier = cls._API_KEYS.get(api_key, "free")
        return True, tier           # POC: always authenticate; production uses JWT validation


# ─────────────────────────────────────────────
#  GATEWAY FACADE
# ─────────────────────────────────────────────

class APIGateway:
    """Single entry point for all requests. Injects trace ID, enforces security."""

    @classmethod
    def process(
        cls,
        session_id: str,
        payload: str,
        api_key: Optional[str] = None,
        logs: Optional[list] = None,
    ) -> GatewayResult:
        t0 = time.time()
        logs = logs or []
        logs.append("🔐 [API GATEWAY] Incoming request — running edge security checks...")

        # Step 1: Auth
        authed, tier = AuthEngine.validate(api_key)
        trace_id = uuid.uuid4().hex[:12]
        req_id = uuid.uuid4().hex[:8]

        # Step 2: WAF
        waf_score, waf_reason = WAF.score(payload)
        if waf_score >= 0.9:
            logs.append(f"🚫 [WAF] Blocked: {waf_reason}")
            return GatewayResult(
                allowed=False,
                request=GatewayRequest(
                    trace_id=trace_id, session_id=session_id, user_tier=tier,
                    request_id=req_id, timestamp=t0, rate_limit_key=session_id,
                    authenticated=authed, waf_score=waf_score,
                ),
                block_reason=f"WAF: {waf_reason}",
                latency_ms=(time.time() - t0) * 1000,
            )

        # Step 3: Rate limiting
        rl_allowed, remaining, reset = RateLimiter.check(session_id, tier)
        if not rl_allowed:
            logs.append(f"🚫 [RATE LIMITER] {tier} tier exceeded. Reset in {reset}s")
            return GatewayResult(
                allowed=False,
                request=GatewayRequest(
                    trace_id=trace_id, session_id=session_id, user_tier=tier,
                    request_id=req_id, timestamp=t0, rate_limit_key=session_id,
                    authenticated=authed, waf_score=waf_score,
                ),
                block_reason=f"Rate limit exceeded (tier={tier}, reset in {reset}s)",
                latency_ms=(time.time() - t0) * 1000,
            )

        logs.append(
            f"✅ [API GATEWAY] Auth={authed} | Tier={tier} | WAF={waf_score:.2f} | "
            f"RL={remaining} req remaining | TraceID={trace_id}"
        )

        req = GatewayRequest(
            trace_id=trace_id, session_id=session_id, user_tier=tier,
            request_id=req_id, timestamp=t0, rate_limit_key=session_id,
            authenticated=authed, waf_score=waf_score,
        )

        return GatewayResult(allowed=True, request=req, latency_ms=(time.time() - t0) * 1000)


# Singleton
gateway = APIGateway()