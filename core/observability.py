"""
NEXUS AI Marketplace - Observability Engine
Implements: Distributed Tracing, Logs Aggregation, Metrics & Dashboards,
            Alerts & Anomaly Detection, Token Usage & Cost Tracking

From the Enterprise Agentic AI Platform cross-cutting concerns panel.
"""

import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ─────────────────────────────────────────────
#  DISTRIBUTED TRACING
# ─────────────────────────────────────────────

@dataclass
class Span:
    span_id: str
    trace_id: str
    node_name: str
    start_ts: float
    end_ts: Optional[float] = None
    status: str = "running"     # running | ok | error
    tokens_in: int = 0
    tokens_out: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> float:
        if self.end_ts:
            return (self.end_ts - self.start_ts) * 1000
        return (time.time() - self.start_ts) * 1000


@dataclass
class Trace:
    trace_id: str
    session_id: str
    query_hash: str
    start_ts: float = field(default_factory=time.time)
    end_ts: Optional[float] = None
    spans: List[Span] = field(default_factory=list)
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    status: str = "running"

    @property
    def total_duration_ms(self) -> float:
        if self.end_ts:
            return (self.end_ts - self.start_ts) * 1000
        return (time.time() - self.start_ts) * 1000

    def add_span(self, node_name: str) -> Span:
        span = Span(
            span_id=uuid.uuid4().hex[:8],
            trace_id=self.trace_id,
            node_name=node_name,
            start_ts=time.time(),
        )
        self.spans.append(span)
        return span

    def close_span(self, span: Span, status: str = "ok", tokens_in: int = 0, tokens_out: int = 0) -> None:
        span.end_ts = time.time()
        span.status = status
        span.tokens_in = tokens_in
        span.tokens_out = tokens_out
        self.total_tokens += tokens_in + tokens_out

    def finalize(self, status: str = "ok") -> None:
        self.end_ts = time.time()
        self.status = status
        # Cost estimate: Claude Sonnet ~$0.003 input / $0.015 output per 1K tokens
        self.total_cost_usd = (self.total_tokens * 0.003) / 1000


# ─────────────────────────────────────────────
#  METRICS STORE
# ─────────────────────────────────────────────

class MetricsStore:
    """Rolling window metrics — last 100 requests."""
    _latencies: deque = deque(maxlen=100)        # ms per request
    _token_counts: deque = deque(maxlen=100)
    _costs: deque = deque(maxlen=100)
    _category_counts: Dict[str, int] = defaultdict(int)
    _error_count: int = 0
    _success_count: int = 0
    _auction_cpms: deque = deque(maxlen=50)

    @classmethod
    def record(cls, trace: Trace, category: str, winning_cpm: float = 0.0) -> None:
        cls._latencies.append(trace.total_duration_ms)
        cls._token_counts.append(trace.total_tokens)
        cls._costs.append(trace.total_cost_usd)
        cls._category_counts[category] += 1
        if trace.status == "ok":
            cls._success_count += 1
        else:
            cls._error_count += 1
        if winning_cpm > 0:
            cls._auction_cpms.append(winning_cpm)

    @classmethod
    def summary(cls) -> Dict:
        lats = list(cls._latencies)
        toks = list(cls._token_counts)
        costs = list(cls._costs)
        total = cls._success_count + cls._error_count
        return {
            "total_requests": total,
            "success_rate": (cls._success_count / total * 100) if total else 0,
            "avg_latency_ms": round(sum(lats) / len(lats), 1) if lats else 0,
            "p95_latency_ms": round(sorted(lats)[int(len(lats) * 0.95)], 1) if len(lats) >= 5 else 0,
            "avg_tokens": round(sum(toks) / len(toks), 0) if toks else 0,
            "total_cost_usd": round(sum(costs), 6),
            "avg_cost_per_req_usd": round(sum(costs) / len(costs), 6) if costs else 0,
            "category_distribution": dict(cls._category_counts),
            "avg_winning_cpm_inr": round(sum(cls._auction_cpms) / len(cls._auction_cpms), 2) if cls._auction_cpms else 0,
            "error_count": cls._error_count,
        }


# ─────────────────────────────────────────────
#  ALERT ENGINE
# ─────────────────────────────────────────────

@dataclass
class Alert:
    level: str        # "info" | "warning" | "critical"
    rule: str
    detail: str
    ts: float = field(default_factory=time.time)


class AlertEngine:
    _alerts: deque = deque(maxlen=50)
    _thresholds = {
        "latency_critical_ms": 8000,
        "latency_warn_ms":     3000,
        "error_rate_critical": 30.0,   # %
        "error_rate_warn":     10.0,
        "cost_warn_usd":       0.10,
    }

    @classmethod
    def evaluate(cls, trace: Trace, metrics: Dict) -> List[Alert]:
        new_alerts = []

        if trace.total_duration_ms > cls._thresholds["latency_critical_ms"]:
            a = Alert("critical", "High Latency", f"Request took {trace.total_duration_ms:.0f}ms (>{cls._thresholds['latency_critical_ms']}ms)")
            new_alerts.append(a)
            cls._alerts.append(a)
        elif trace.total_duration_ms > cls._thresholds["latency_warn_ms"]:
            a = Alert("warning", "Elevated Latency", f"Request took {trace.total_duration_ms:.0f}ms")
            new_alerts.append(a)
            cls._alerts.append(a)

        if metrics.get("success_rate", 100) < (100 - cls._thresholds["error_rate_critical"]):
            a = Alert("critical", "High Error Rate", f"Error rate: {100 - metrics['success_rate']:.1f}%")
            new_alerts.append(a)
            cls._alerts.append(a)

        if trace.total_cost_usd > cls._thresholds["cost_warn_usd"]:
            a = Alert("warning", "High Request Cost", f"Cost: ${trace.total_cost_usd:.4f}")
            new_alerts.append(a)
            cls._alerts.append(a)

        return new_alerts

    @classmethod
    def get_recent(cls, n: int = 10) -> List[Alert]:
        return list(cls._alerts)[-n:]


# ─────────────────────────────────────────────
#  OBSERVABILITY FACADE
# ─────────────────────────────────────────────

class ObservabilityEngine:
    """Single entry point for all observability operations."""
    _traces: Dict[str, Trace] = {}

    @classmethod
    def start_trace(cls, session_id: str, query: str) -> Trace:
        trace_id = uuid.uuid4().hex[:12]
        q_hash = str(hash(query))[:8]
        trace = Trace(trace_id=trace_id, session_id=session_id[:8], query_hash=q_hash)
        cls._traces[trace_id] = trace
        return trace

    @classmethod
    def get_trace(cls, trace_id: str) -> Optional[Trace]:
        return cls._traces.get(trace_id)

    @classmethod
    def record_and_alert(cls, trace: Trace, category: str, winning_cpm: float = 0.0) -> List[Alert]:
        trace.finalize("ok")
        MetricsStore.record(trace, category, winning_cpm)
        return AlertEngine.evaluate(trace, MetricsStore.summary())

    @classmethod
    def get_dashboard_data(cls) -> Dict:
        return {
            "metrics": MetricsStore.summary(),
            "recent_alerts": [
                {"level": a.level, "rule": a.rule, "detail": a.detail}
                for a in AlertEngine.get_recent(5)
            ],
            "recent_traces": [
                {
                    "trace_id": t.trace_id,
                    "session": t.session_id,
                    "duration_ms": round(t.total_duration_ms, 1),
                    "status": t.status,
                    "spans": len(t.spans),
                    "tokens": t.total_tokens,
                    "cost_usd": round(t.total_cost_usd, 6),
                }
                for t in list(cls._traces.values())[-5:]
            ],
        }


# Singleton
observability = ObservabilityEngine()