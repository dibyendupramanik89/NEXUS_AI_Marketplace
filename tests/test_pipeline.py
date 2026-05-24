"""
NEXUS AI Marketplace - Test Suite
Tests all pipeline components without requiring API keys.
"""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.schemas import IntentCategory, NexusAgentState
from core.privacy import PrivacyEngine
from agents.supervisor import _deterministic_parse


class TestDeterministicParser:
    def test_fashion(self):
        result = _deterministic_parse("i want to buy tshirt color blue, size xl, price 1500Rs")
        assert result["category"] == "fashion"
        assert result["attributes"]["color"] == "blue"
        assert result["attributes"]["size"] == "XL"

    def test_real_estate(self):
        result = _deterministic_parse("i want to buy a flat 1500sq feet in varthur bangalore")
        assert result["category"] == "real_estate"
        assert result["geography"] == "Varthur"

    def test_medical(self):
        result = _deterministic_parse("user searching for medicine for migraine")
        assert result["category"] == "medical"
        assert result["target_noun"] == "migraine"

    def test_learning(self):
        result = _deterministic_parse("user wants to learn agentic ai and build agents")
        assert result["category"] == "learning"


class TestPrivacyEngine:
    def test_pii_scrubbed(self):
        from core.schemas import IntentCategory
        logs = []
        token = PrivacyEngine.create_token(
            raw_query="call me at 9876543210",
            category=IntentCategory.GENERAL,
            target_noun="item",
            geography=None,
            budget_min=None,
            budget_max=None,
            attributes={"contact": "9876543210"},
            confidence=0.7,
            logs=logs,
        )
        assert "[PHONE_REDACTED]" in str(token.attributes)

    def test_session_id_anonymous(self):
        logs = []
        token = PrivacyEngine.create_token(
            raw_query="test query",
            category=IntentCategory.FASHION,
            target_noun="tshirt",
            geography=None,
            budget_min=None,
            budget_max=1500,
            attributes={},
            confidence=0.9,
            logs=logs,
        )
        assert len(token.session_id) == 8
        assert "test query" not in token.session_id


class TestAuction:
    def test_auction_returns_winner(self):
        from core.auction import ProgrammaticAuctionEngine
        from core.schemas import IntentCategory
        from core.privacy import PrivacyEngine
        logs = []
        token = PrivacyEngine.create_token(
            raw_query="blue tshirt xl",
            category=IntentCategory.FASHION,
            target_noun="tshirt",
            geography=None,
            budget_min=None,
            budget_max=1500,
            attributes={"color": "blue", "size": "XL"},
            confidence=0.9,
            logs=logs,
        )
        all_bids, winning_ad, duration = ProgrammaticAuctionEngine.run_auction(token, logs)
        assert len(all_bids) > 0
        assert winning_ad is not None
        assert winning_ad.verification_passed is True
        assert duration > 0

    def test_highest_cpm_wins(self):
        from core.auction import ProgrammaticAuctionEngine
        from core.schemas import IntentCategory
        from core.privacy import PrivacyEngine
        logs = []
        token = PrivacyEngine.create_token(
            raw_query="flat in varthur bangalore",
            category=IntentCategory.REAL_ESTATE,
            target_noun="flat",
            geography="Varthur",
            budget_min=None,
            budget_max=12_000_000,
            attributes={"area_sqft": 1500},
            confidence=0.88,
            logs=logs,
        )
        all_bids, winning_ad, _ = ProgrammaticAuctionEngine.run_auction(token, logs)
        if len(all_bids) > 1:
            sorted_bids = sorted(all_bids, key=lambda b: b.cpm_bid_inr, reverse=True)
            assert winning_ad.bid.cpm_bid_inr == sorted_bids[0].cpm_bid_inr


class TestFullPipeline:
    def test_fashion_end_to_end(self):
        from workflow.graph import process_query
        output, logs, state = process_query("i want to buy tshirt color blue, size xl, with price range 1500Rs")
        assert "fashion" in output.lower() or "tshirt" in output.lower() or "myntra" in output.lower()
        assert len(logs) > 0

    def test_real_estate_end_to_end(self):
        from workflow.graph import process_query
        output, logs, state = process_query("i want to buy a flat 1500sq feet in varthur bangalore")
        assert "real estate" in output.lower() or "property" in output.lower() or "flat" in output.lower()

    def test_medical_disclaimer_present(self):
        from workflow.graph import process_query
        output, logs, state = process_query("user searching for medicine for migraine")
        assert "disclaimer" in output.lower() or "doctor" in output.lower() or "consult" in output.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
