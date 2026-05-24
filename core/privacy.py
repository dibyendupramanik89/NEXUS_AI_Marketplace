"""
NEXUS AI Marketplace - Privacy Engine
Implements PII scrubbing, ephemeral token generation, and GDPR-compliant
data handling for the agentic pipeline.
"""

import re
import hashlib
import uuid
from typing import Tuple, Dict, Any, Optional
from core.schemas import EphemeralIntentToken, IntentCategory


_PII_PATTERNS = {
    "phone_IN":    r'\b[6-9]\d{9}\b',
    "email":       r'\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b',
    "aadhaar":     r'\b\d{4}\s?\d{4}\s?\d{4}\b',
    "pan_card":    r'\b[A-Z]{5}\d{4}[A-Z]\b',
    "credit_card": r'\b(?:\d[ -]?){13,16}\b',
    "passport":    r'\b[A-Z]\d{7}\b',
    "dob":         r'\b(?:0[1-9]|[12]\d|3[01])[/-](?:0[1-9]|1[0-2])[/-]\d{4}\b',
}

_PII_REPLACEMENTS = {
    "phone_IN":    "[PHONE_REDACTED]",
    "email":       "[EMAIL_REDACTED]",
    "aadhaar":     "[AADHAAR_REDACTED]",
    "pan_card":    "[PAN_REDACTED]",
    "credit_card": "[CARD_REDACTED]",
    "passport":    "[PASSPORT_REDACTED]",
    "dob":         "[DOB_REDACTED]",
}


class PrivacyEngine:
    """
    Enterprise Privacy Engine — strips PII before it enters the pipeline
    and generates ephemeral, privacy-safe intent tokens.
    """

    @staticmethod
    def scrub_pii(text: str) -> Tuple[str, Dict[str, int]]:
        """Remove PII from text. Returns (sanitized_text, {pii_type: count})."""
        found: Dict[str, int] = {}
        sanitized = text
        for name, pattern in _PII_PATTERNS.items():
            matches = re.findall(pattern, sanitized, re.IGNORECASE)
            if matches:
                found[name] = len(matches)
                sanitized = re.sub(pattern, _PII_REPLACEMENTS[name], sanitized, flags=re.IGNORECASE)
        return sanitized, found

    @staticmethod
    def hash_query(query: str) -> str:
        """SHA-256 hash of query for audit trail."""
        return hashlib.sha256(query.encode()).hexdigest()[:16]

    @staticmethod
    def build_intent_token(
        session_id: str,
        query: str,
        category: IntentCategory,
        target_noun: str,
        geography: Optional[str] = None,
        budget_min: Optional[float] = None,
        budget_max: Optional[float] = None,
        attributes: Optional[Dict[str, Any]] = None,
        confidence: float = 0.85,
    ) -> EphemeralIntentToken:
        """Build a privacy-safe ephemeral intent token — no raw PII inside."""
        return EphemeralIntentToken(
            session_id=session_id,
            category=category,
            target_noun=target_noun,
            geography=geography,
            budget_min=budget_min,
            budget_max=budget_max,
            attributes=attributes or {},
            raw_query_hash=PrivacyEngine.hash_query(query),
            confidence=confidence,
        )