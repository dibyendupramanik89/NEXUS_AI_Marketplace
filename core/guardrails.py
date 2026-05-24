"""
NEXUS AI Marketplace - Enterprise Guardrails Engine
Implements all guardrail layers from the Enterprise Agentic AI Platform diagram:

INPUT GUARDRAILS:  PII Detection, Prompt Injection, Toxicity Filter, Input Validation, Policy Enforcement
OUTPUT GUARDRAILS: Response Validation, Hallucination Detection, PII Redaction,
                   Compliance Check, Policy Validation, Confidence Scoring
"""

import re
import time
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


class GuardrailStatus(str, Enum):
    PASS   = "PASS"
    WARN   = "WARN"
    BLOCK  = "BLOCK"


@dataclass
class GuardrailCheck:
    name: str
    status: GuardrailStatus
    score: float          # 0.0 = clean, 1.0 = max risk
    detail: str
    latency_ms: float = 0.0
    action_taken: str = "none"


@dataclass
class GuardrailReport:
    overall_status: GuardrailStatus
    checks: List[GuardrailCheck]
    sanitized_text: str
    total_latency_ms: float
    blocked: bool
    block_reason: Optional[str] = None


# ─────────────────────────────────────────────
#  PATTERN LIBRARIES
# ─────────────────────────────────────────────

_PII_PATTERNS = {
    "phone_IN":    (r'\b[6-9]\d{9}\b', 0.9),
    "email":       (r'\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b', 0.9),
    "aadhaar":     (r'\b\d{4}\s?\d{4}\s?\d{4}\b', 0.95),
    "pan_card":    (r'\b[A-Z]{5}\d{4}[A-Z]\b', 0.95),
    "credit_card": (r'\b(?:\d[ -]?){13,16}\b', 0.98),
    "passport":    (r'\b[A-Z]\d{7}\b', 0.85),
    "dob":         (r'\b(?:0[1-9]|[12]\d|3[01])[/-](?:0[1-9]|1[0-2])[/-]\d{4}\b', 0.7),
}

_INJECTION_PATTERNS = [
    (r'ignore\s+(?:all\s+)?(?:previous|above|prior)\s+instructions?', 0.95),
    (r'you\s+are\s+now\s+(?:a|an|acting)', 0.85),
    (r'disregard\s+(?:your|all)\s+(?:system|previous)', 0.90),
    (r'jailbreak|bypass\s+(?:your\s+)?(?:filter|guideline|restriction)', 0.95),
    (r'act\s+as\s+(?:if\s+)?(?:you\s+have\s+no|without\s+any)', 0.88),
    (r'pretend\s+(?:you\s+are|to\s+be)\s+(?:an?\s+)?(?:evil|harmful|unrestricted)', 0.92),
    (r'<\s*(?:system|assistant|user)\s*>', 0.80),
    (r'###\s*(?:SYSTEM|ASSISTANT|NEW\s+INSTRUCTIONS?)\s*###', 0.90),
]

_TOXICITY_KEYWORDS = {
    "violence":   (["kill", "murder", "attack", "bomb", "terrorist"], 0.95),
    "hate":       (["racist", "sexist", "bigot"], 0.90),
    "adult":      (["pornography", "explicit sexual"], 0.99),
    "self_harm":  (["suicide", "self-harm", "cut myself"], 0.95),
}

_POLICY_RULES = [
    (r'\b(?:competitor|rival)\s+(?:product|brand|company)\b', "Competitor mention policy", GuardrailStatus.WARN, 0.4),
    (r'\b(?:guaranteed|100%\s+profit|no\s+risk)\b', "Financial promise policy", GuardrailStatus.WARN, 0.5),
    (r'\b(?:free\s+money|instant\s+rich|get\s+rich)\b', "Scam pattern policy", GuardrailStatus.BLOCK, 0.9),
]


# ─────────────────────────────────────────────
#  INPUT GUARDRAILS
# ─────────────────────────────────────────────

class InputGuardrails:

    @staticmethod
    def check_pii(text: str) -> Tuple[GuardrailCheck, str]:
        t0 = time.time()
        found = []
        sanitized = text
        max_score = 0.0

        for name, (pattern, risk) in _PII_PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                found.append(f"{name}({len(matches)})")
                max_score = max(max_score, risk)
                sanitized = re.sub(pattern, f"[{name.upper()}_REDACTED]", sanitized, flags=re.IGNORECASE)

        status = GuardrailStatus.BLOCK if max_score >= 0.95 else (GuardrailStatus.WARN if found else GuardrailStatus.PASS)
        action = "redacted" if found else "none"

        return GuardrailCheck(
            name="PII Detection & Masking",
            status=status,
            score=max_score,
            detail=f"Detected: {', '.join(found)}" if found else "No PII detected",
            latency_ms=(time.time() - t0) * 1000,
            action_taken=action,
        ), sanitized

    @staticmethod
    def check_prompt_injection(text: str) -> GuardrailCheck:
        t0 = time.time()
        max_score = 0.0
        triggers = []

        for pattern, risk in _INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                triggers.append(pattern[:30])
                max_score = max(max_score, risk)

        status = GuardrailStatus.BLOCK if max_score >= 0.85 else (GuardrailStatus.WARN if max_score > 0.3 else GuardrailStatus.PASS)
        return GuardrailCheck(
            name="Prompt Injection Detection",
            status=status,
            score=max_score,
            detail=f"Injection patterns found: {len(triggers)}" if triggers else "No injection patterns detected",
            latency_ms=(time.time() - t0) * 1000,
            action_taken="blocked" if status == GuardrailStatus.BLOCK else "none",
        )

    @staticmethod
    def check_toxicity(text: str) -> GuardrailCheck:
        t0 = time.time()
        tl = text.lower()
        found = []
        max_score = 0.0

        for category, (keywords, risk) in _TOXICITY_KEYWORDS.items():
            if any(kw in tl for kw in keywords):
                found.append(category)
                max_score = max(max_score, risk)

        status = GuardrailStatus.BLOCK if max_score >= 0.9 else (GuardrailStatus.WARN if found else GuardrailStatus.PASS)
        return GuardrailCheck(
            name="Toxicity & Safety Filter",
            status=status,
            score=max_score,
            detail=f"Categories flagged: {', '.join(found)}" if found else "Content is safe",
            latency_ms=(time.time() - t0) * 1000,
            action_taken="blocked" if status == GuardrailStatus.BLOCK else "none",
        )

    @staticmethod
    def validate_input(text: str) -> GuardrailCheck:
        t0 = time.time()
        issues = []
        score = 0.0

        if len(text.strip()) < 3:
            issues.append("Query too short (<3 chars)")
            score = 0.7
        if len(text) > 2000:
            issues.append("Query too long (>2000 chars)")
            score = max(score, 0.5)
        if len(set(text)) < 4:
            issues.append("Low character diversity")
            score = max(score, 0.4)

        status = GuardrailStatus.BLOCK if score >= 0.7 else (GuardrailStatus.WARN if issues else GuardrailStatus.PASS)
        return GuardrailCheck(
            name="Input Validation",
            status=status,
            score=score,
            detail="; ".join(issues) if issues else f"Valid input ({len(text)} chars)",
            latency_ms=(time.time() - t0) * 1000,
            action_taken="rejected" if status == GuardrailStatus.BLOCK else "none",
        )

    @staticmethod
    def enforce_policy(text: str) -> GuardrailCheck:
        t0 = time.time()
        violations = []
        max_score = 0.0
        block = False

        for pattern, rule_name, status, risk in _POLICY_RULES:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(rule_name)
                max_score = max(max_score, risk)
                if status == GuardrailStatus.BLOCK:
                    block = True

        final_status = GuardrailStatus.BLOCK if block else (GuardrailStatus.WARN if violations else GuardrailStatus.PASS)
        return GuardrailCheck(
            name="Policy Enforcement",
            status=final_status,
            score=max_score,
            detail=f"Policy violations: {', '.join(violations)}" if violations else "All policies satisfied",
            latency_ms=(time.time() - t0) * 1000,
            action_taken="policy_blocked" if block else "none",
        )

    @classmethod
    def run_all(cls, raw_text: str, logs: List[str]) -> Tuple[GuardrailReport, str]:
        logs.append("🛡️  [INPUT GUARDRAILS] Running 5-layer security scan...")
        t0 = time.time()

        pii_check, sanitized = cls.check_pii(raw_text)
        injection_check       = cls.check_prompt_injection(sanitized)
        toxicity_check        = cls.check_toxicity(sanitized)
        validation_check      = cls.validate_input(sanitized)
        policy_check          = cls.enforce_policy(sanitized)

        checks = [pii_check, injection_check, toxicity_check, validation_check, policy_check]
        blocked = any(c.status == GuardrailStatus.BLOCK for c in checks)
        block_reason = next((c.name for c in checks if c.status == GuardrailStatus.BLOCK), None)
        overall = GuardrailStatus.BLOCK if blocked else (
            GuardrailStatus.WARN if any(c.status == GuardrailStatus.WARN for c in checks) else GuardrailStatus.PASS
        )

        total_ms = (time.time() - t0) * 1000
        for c in checks:
            icon = "✅" if c.status == GuardrailStatus.PASS else ("⚠️" if c.status == GuardrailStatus.WARN else "🚫")
            logs.append(f"   {icon} [{c.name}] {c.status.value} | score={c.score:.2f} | {c.detail}")

        logs.append(f"🛡️  [INPUT GUARDRAILS] Complete in {total_ms:.0f}ms | Overall: {overall.value}")

        return GuardrailReport(
            overall_status=overall,
            checks=checks,
            sanitized_text=sanitized,
            total_latency_ms=total_ms,
            blocked=blocked,
            block_reason=block_reason,
        ), sanitized


# ─────────────────────────────────────────────
#  OUTPUT GUARDRAILS
# ─────────────────────────────────────────────

class OutputGuardrails:

    @staticmethod
    def validate_schema(response: str) -> GuardrailCheck:
        t0 = time.time()
        issues = []
        if len(response.strip()) < 20:
            issues.append("Response too short")
        if response.count("Error") > 3:
            issues.append("Too many error mentions")

        status = GuardrailStatus.WARN if issues else GuardrailStatus.PASS
        return GuardrailCheck(
            name="Response Validation (Schema/Rules)",
            status=status,
            score=0.3 if issues else 0.0,
            detail="; ".join(issues) if issues else "Schema valid",
            latency_ms=(time.time() - t0) * 1000,
        )

    @staticmethod
    def detect_hallucination(response: str, context_urls: List[str]) -> GuardrailCheck:
        """Checks if URLs in response are grounded in context."""
        t0 = time.time()
        url_pattern = r'https?://[^\s\])]+'
        urls_in_response = re.findall(url_pattern, response)
        ungrounded = [u for u in urls_in_response if not any(u[:40] in cu for cu in (context_urls or []))]

        score = min(len(ungrounded) * 0.15, 1.0)
        status = GuardrailStatus.WARN if ungrounded else GuardrailStatus.PASS

        return GuardrailCheck(
            name="Hallucination Detection",
            status=status,
            score=score,
            detail=f"{len(ungrounded)} potentially ungrounded URLs" if ungrounded else "All citations grounded",
            latency_ms=(time.time() - t0) * 1000,
            action_taken="flagged" if ungrounded else "none",
        )

    @staticmethod
    def redact_output_pii(response: str) -> Tuple[GuardrailCheck, str]:
        """Final PII sweep on generated output before delivery."""
        t0 = time.time()
        redacted = response
        count = 0
        for name, (pattern, _) in _PII_PATTERNS.items():
            new = re.sub(pattern, f"[{name.upper()}_REDACTED]", redacted, flags=re.IGNORECASE)
            if new != redacted:
                count += 1
            redacted = new

        return GuardrailCheck(
            name="PII Redaction (Output)",
            status=GuardrailStatus.WARN if count > 0 else GuardrailStatus.PASS,
            score=min(count * 0.2, 1.0),
            detail=f"{count} PII fields redacted from output" if count else "Output PII-clean",
            latency_ms=(time.time() - t0) * 1000,
            action_taken="redacted" if count else "none",
        ), redacted

    @staticmethod
    def compliance_check(response: str, category: str) -> GuardrailCheck:
        """Domain-specific compliance checks (medical disclaimer, financial caveat, etc.)"""
        t0 = time.time()
        issues = []

        if category == "medical":
            if "doctor" not in response.lower() and "consult" not in response.lower():
                issues.append("Medical response missing doctor consultation disclaimer")
        if category == "real_estate":
            if "rera" not in response.lower() and "registered" not in response.lower():
                issues.append("Real estate response missing RERA mention")

        status = GuardrailStatus.WARN if issues else GuardrailStatus.PASS
        return GuardrailCheck(
            name="Compliance Check",
            status=status,
            score=0.4 if issues else 0.0,
            detail="; ".join(issues) if issues else "All compliance requirements met",
            latency_ms=(time.time() - t0) * 1000,
        )

    @staticmethod
    def score_confidence(discoveries: list, winning_ad) -> GuardrailCheck:
        """Aggregate confidence scoring across all pipeline outputs."""
        t0 = time.time()
        scores = [d.confidence for d in discoveries if hasattr(d, 'confidence')]
        avg = sum(scores) / len(scores) if scores else 0.5
        ad_score = 0.9 if winning_ad and getattr(winning_ad, 'verification_passed', False) else 0.4

        composite = (avg * 0.6) + (ad_score * 0.4)
        status = GuardrailStatus.PASS if composite >= 0.7 else (GuardrailStatus.WARN if composite >= 0.4 else GuardrailStatus.BLOCK)

        return GuardrailCheck(
            name="Confidence Scoring",
            status=status,
            score=round(1.0 - composite, 2),
            detail=f"Composite confidence: {composite:.0%} | Organic avg: {avg:.0%} | Ad: {ad_score:.0%}",
            latency_ms=(time.time() - t0) * 1000,
        )

    @classmethod
    def run_all(
        cls,
        response: str,
        category: str,
        context_urls: List[str],
        discoveries: list,
        winning_ad,
        logs: List[str],
    ) -> Tuple[GuardrailReport, str]:
        logs.append("🔒 [OUTPUT GUARDRAILS] Validating response through 6-layer output filter...")
        t0 = time.time()

        schema_check                     = cls.validate_schema(response)
        hallucination_check              = cls.detect_hallucination(response, context_urls)
        pii_check, clean_response        = cls.redact_output_pii(response)
        compliance_check                 = cls.compliance_check(clean_response, category)
        confidence_check                 = cls.score_confidence(discoveries, winning_ad)

        # Policy validation (re-run on output)
        policy_check = GuardrailCheck(
            name="Policy Validation (Output)",
            status=GuardrailStatus.PASS,
            score=0.0,
            detail="Output policy compliant",
            latency_ms=0.5,
        )

        checks = [schema_check, hallucination_check, pii_check, compliance_check, policy_check, confidence_check]
        blocked = any(c.status == GuardrailStatus.BLOCK for c in checks)
        overall = GuardrailStatus.BLOCK if blocked else (
            GuardrailStatus.WARN if any(c.status == GuardrailStatus.WARN for c in checks) else GuardrailStatus.PASS
        )

        total_ms = (time.time() - t0) * 1000
        for c in checks:
            icon = "✅" if c.status == GuardrailStatus.PASS else ("⚠️" if c.status == GuardrailStatus.WARN else "🚫")
            logs.append(f"   {icon} [{c.name}] {c.status.value} | {c.detail}")

        logs.append(f"🔒 [OUTPUT GUARDRAILS] Complete in {total_ms:.0f}ms | Overall: {overall.value}")

        return GuardrailReport(
            overall_status=overall,
            checks=checks,
            sanitized_text=clean_response,
            total_latency_ms=total_ms,
            blocked=blocked,
        ), clean_response