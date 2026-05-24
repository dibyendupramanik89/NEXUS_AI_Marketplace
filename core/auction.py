"""
NEXUS AI Marketplace - PAX Programmatic Ad Exchange Engine
Second-price real-time auction for sponsored listings.
"""

import time
import uuid
import random
from typing import List, Optional, Tuple
from core.schemas import (
    BidRequest, BidResponse, WinningAd, EphemeralIntentToken, IntentCategory,
)

_FASHION_ADVERTISERS = [
    {"advertiser": "Myntra Ads", "brand": "Myntra", "cpm_base": 320,
     "title": "Latest Fashion Trends – Up to 70% Off", "description": "Shop 5 lakh+ styles across brands. T-shirts, jeans, dresses & more. Free delivery & easy returns.", "price": "Starts ₹299", "cta": "Shop on Myntra", "deal_url": "https://www.myntra.com", "verification_token": "MYNTRA-VERIFIED-2024"},
    {"advertiser": "Ajio Fashion", "brand": "Ajio", "cpm_base": 290,
     "title": "AJIO – Curated Fashion for Every Style", "description": "Exclusive brands & collections. Express delivery. Blue T-shirts XL starting ₹499.", "price": "From ₹499", "cta": "Explore AJIO", "deal_url": "https://www.ajio.com", "verification_token": "AJIO-VERIFIED-2024"},
    {"advertiser": "Flipkart Fashion", "brand": "Flipkart", "cpm_base": 260,
     "title": "Flipkart Fashion – Big Billion Deals", "description": "Top brands, unbeatable prices. T-shirts from ₹199. Same-day delivery available.", "price": "From ₹199", "cta": "Buy on Flipkart", "deal_url": "https://www.flipkart.com/clothing-and-accessories", "verification_token": "FK-VERIFIED-2024"},
    {"advertiser": "Amazon Fashion IN", "brand": "Amazon", "cpm_base": 310,
     "title": "Amazon Fashion – Prime Delivery", "description": "Millions of styles. Prime 1-day delivery. T-shirts in blue, XL – verified brands.", "price": "₹399–₹2,499", "cta": "Shop Amazon", "deal_url": "https://www.amazon.in/s?k=blue+tshirt+xl", "verification_token": "AMZ-VERIFIED-2024"},
]

_REAL_ESTATE_ADVERTISERS = [
    {"advertiser": "Sattva Group", "brand": "Sattva Group", "cpm_base": 580,
     "title": "Sattva Lumina – Premium 2/3 BHK, Varthur Bangalore", "description": "RERA-registered. 1500 sqft 3BHK from ₹1.2 Cr. Gated community, 30+ amenities. Possession 2026.", "price": "₹1.2 Cr onwards", "cta": "Book Site Visit", "deal_url": "https://www.sattva.co.in", "verification_token": "SATTVA-RERA-KA-2024"},
    {"advertiser": "99acres Sponsored", "brand": "99acres", "cpm_base": 450,
     "title": "1500 sqft Flats in Varthur – 120+ Listings", "description": "Verified listings from top builders. 2BHK & 3BHK. Compare prices, visit on weekend.", "price": "₹85L – ₹1.5 Cr", "cta": "View Listings", "deal_url": "https://www.99acres.com/property-in-varthur-bangalore", "verification_token": "99ACRES-VERIFIED-2024"},
    {"advertiser": "Prestige Estates", "brand": "Prestige Group", "cpm_base": 620,
     "title": "Prestige Smart City – Varthur, East Bangalore", "description": "RERA approved. 1480–1850 sqft 3BHK. Club house, pool, 24/7 security. Ready to move.", "price": "₹1.35 Cr onwards", "cta": "Get Brochure", "deal_url": "https://www.prestigeconstructions.com", "verification_token": "PRESTIGE-RERA-2024"},
    {"advertiser": "MagicBricks Ads", "brand": "MagicBricks", "cpm_base": 410,
     "title": "Varthur Flats – MagicBricks Verified", "description": "250+ verified flats near Varthur. Compare EMI, builder reputation, and locality.", "price": "₹80L – ₹2 Cr", "cta": "Search Flats", "deal_url": "https://www.magicbricks.com/flats-in-varthur", "verification_token": "MB-VERIFIED-2024"},
]

_MEDICAL_ADVERTISERS = [
    {"advertiser": "Apollo Pharmacy", "brand": "Apollo Pharmacy", "cpm_base": 280,
     "title": "Apollo Pharmacy – Migraine Medicines Delivered Fast", "description": "OTC & prescription medicines. Sumatriptan, Paracetamol, Aspirin. 2-hr delivery in Bangalore.", "price": "From ₹49", "cta": "Order Medicine", "deal_url": "https://www.apollopharmacy.in", "verification_token": "APOLLO-LICENSED-2024"},
    {"advertiser": "Practo Health", "brand": "Practo", "cpm_base": 310,
     "title": "Consult a Neurologist Online – Migraine Specialist", "description": "Video consult with top neurologists in Bangalore. First consult ₹299. Prescription included.", "price": "₹299 per session", "cta": "Book Consultation", "deal_url": "https://www.practo.com/bangalore/neurologist", "verification_token": "PRACTO-VERIFIED-2024"},
    {"advertiser": "Netmeds", "brand": "Netmeds", "cpm_base": 260,
     "title": "Migraine & Headache Medicines – Netmeds", "description": "Trusted medicines at lowest prices. COD available. Genuine products with batch verification.", "price": "Up to 30% off", "cta": "Buy Medicines", "deal_url": "https://www.netmeds.com", "verification_token": "NETMEDS-VERIFIED-2024"},
]

_LEARNING_ADVERTISERS = [
    {"advertiser": "Coursera Ads", "brand": "Coursera", "cpm_base": 230,
     "title": "AI & Multi-Agent Systems – Coursera Specialization", "description": "Learn LangGraph, AutoGen, and agentic AI from top universities. Certificate included. Free trial 7 days.", "price": "₹2,499/month", "cta": "Start Free Trial", "deal_url": "https://www.coursera.org/search?query=agentic+AI", "verification_token": "COURSERA-VERIFIED-2024"},
    {"advertiser": "Udemy India", "brand": "Udemy", "cpm_base": 190,
     "title": "LangGraph & Multi-Agent AI – Udemy Bestseller", "description": "Hands-on course: 40+ hours. Build real multi-agent systems with LangGraph. Lifetime access.", "price": "₹499 (limited offer)", "cta": "Enroll Now", "deal_url": "https://www.udemy.com/courses/search/?q=langgraph+agentic", "verification_token": "UDEMY-VERIFIED-2024"},
    {"advertiser": "Great Learning", "brand": "Great Learning", "cpm_base": 210,
     "title": "PG Program in AI & ML with Agentic Systems", "description": "Industry-accredited 6-month program. Build on LangChain, LangGraph, AutoGen. Job guarantee.", "price": "₹85,000", "cta": "Apply Now", "deal_url": "https://www.greatlearning.in", "verification_token": "GL-VERIFIED-2024"},
]

_GENERAL_ADVERTISERS = [
    {"advertiser": "Amazon IN", "brand": "Amazon India", "cpm_base": 200,
     "title": "Find What You're Looking For – Amazon India", "description": "Millions of products, fast delivery, easy returns. Prime members get 1-day delivery.", "price": "Prime from ₹999/yr", "cta": "Shop Now", "deal_url": "https://www.amazon.in", "verification_token": "AMZ-GEN-2024"},
    {"advertiser": "Flipkart General", "brand": "Flipkart", "cpm_base": 180,
     "title": "Flipkart – India's Largest Marketplace", "description": "Best deals across electronics, fashion, home & more. Supercoins on every purchase.", "price": "Great prices daily", "cta": "Explore Flipkart", "deal_url": "https://www.flipkart.com", "verification_token": "FK-GEN-2024"},
]

_GAMING_ADVERTISERS = [
    {"advertiser": "Croma Electronics", "brand": "Croma", "cpm_base": 420,
     "title": "Gaming Laptops – Best Deals at Croma", "description": "RTX 4060 laptops under ₹80,000. ASUS ROG, MSI, Lenovo Legion. EMI at 0% interest.", "price": "From ₹64,990", "cta": "View Gaming Laptops", "deal_url": "https://www.croma.com/gaming-laptops", "verification_token": "CROMA-VERIFIED-2024"},
    {"advertiser": "Vijay Sales", "brand": "Vijay Sales", "cpm_base": 390,
     "title": "Gaming Laptops Under ₹80K – Vijay Sales", "description": "Asus ROG Strix G15, Lenovo IdeaPad Gaming. Trusted since 1979. Free gaming headset.", "price": "₹64,990 – ₹79,990", "cta": "Shop Online", "deal_url": "https://www.vijaysales.com/laptops", "verification_token": "VS-VERIFIED-2024"},
]

_ACCOMMODATION_ADVERTISERS = [
    {"advertiser": "NestAway", "brand": "NestAway", "cpm_base": 180,
     "title": "PG & Apartments near Koramangala – NestAway", "description": "Furnished PG rooms from ₹8,000/mo. WiFi, food, laundry included. Verified properties.", "price": "From ₹8,000/month", "cta": "Find PG", "deal_url": "https://www.nestaway.com", "verification_token": "NESTAWAY-VERIFIED-2024"},
    {"advertiser": "Stanza Living", "brand": "Stanza Living", "cpm_base": 195,
     "title": "Premium PG near Koramangala – Stanza Living", "description": "All-inclusive PG ₹10,000/mo. AC rooms, gym, high-speed wifi, housekeeping.", "price": "₹10,000–₹14,000/mo", "cta": "Book a Room", "deal_url": "https://www.stanzaliving.com", "verification_token": "STANZA-VERIFIED-2024"},
]

_CATEGORY_MAP = {
    IntentCategory.FASHION: _FASHION_ADVERTISERS,
    IntentCategory.REAL_ESTATE: _REAL_ESTATE_ADVERTISERS,
    IntentCategory.MEDICAL: _MEDICAL_ADVERTISERS,
    IntentCategory.LEARNING: _LEARNING_ADVERTISERS,
    IntentCategory.GENERAL: _GENERAL_ADVERTISERS,
}

_KEYWORD_EXTRA = {
    "gaming": _GAMING_ADVERTISERS,
    "laptop": _GAMING_ADVERTISERS,
    "pg ": _ACCOMMODATION_ADVERTISERS,
    "paying guest": _ACCOMMODATION_ADVERTISERS,
    "accommodation": _ACCOMMODATION_ADVERTISERS,
}


class ProgrammaticAuctionEngine:
    """PAX Second-price real-time auction engine."""

    @classmethod
    def run(cls, bid_request: BidRequest, query: str = "", logs: Optional[list] = None) -> Tuple[List[BidResponse], Optional[WinningAd], float]:
        logs = logs or []
        t0 = time.time()
        logs.append(f"⚡ [PAX AUCTION] Starting auction {bid_request.auction_id[:8]} | floor=₹{bid_request.floor_cpm_inr:.0f} CPM")

        token = bid_request.intent_token
        advertisers = list(_CATEGORY_MAP.get(token.category, _GENERAL_ADVERTISERS))
        q_lower = query.lower()
        for kw, extras in _KEYWORD_EXTRA.items():
            if kw in q_lower:
                advertisers = extras + advertisers
                break

        bids: List[BidResponse] = []
        for adv in advertisers:
            jitter = random.uniform(-0.12, 0.12)
            cpm = adv["cpm_base"] * (1 + jitter)
            if token.budget_max:
                cpm *= min(max(token.budget_max / 100_000, 0.5), 2.0)
            if cpm < bid_request.floor_cpm_inr:
                logs.append(f"   📉 [{adv['advertiser']}] Below floor — no bid")
                continue
            bids.append(BidResponse(
                advertiser=adv["advertiser"], brand=adv["brand"],
                cpm_bid_inr=round(cpm, 2), title=adv["title"],
                description=adv["description"], price=adv["price"],
                cta=adv["cta"], deal_url=adv["deal_url"],
                verification_token=adv["verification_token"],
                creative_type="text_ad", category=token.category,
            ))
            logs.append(f"   💰 [{adv['advertiser']}] Bid: ₹{cpm:.0f} CPM")

        if not bids:
            logs.append("⚠️  [PAX AUCTION] No bids above floor.")
            return [], None, (time.time() - t0) * 1000

        bids.sort(key=lambda b: b.cpm_bid_inr, reverse=True)
        clearing = bids[1].cpm_bid_inr + 1.0 if len(bids) > 1 else bid_request.floor_cpm_inr + 1.0
        winner = bids[0]
        passed = bool(winner.verification_token and winner.category == token.category)
        winning_ad = WinningAd(
            bid=BidResponse(**{**winner.model_dump(), "cpm_bid_inr": round(clearing, 2)}),
            auction_rank=1, verification_passed=passed,
            verification_reason="Category+token verified" if passed else "Verification failed",
        )
        dur = (time.time() - t0) * 1000
        logs.append(f"✅ [PAX AUCTION] Winner: {winner.advertiser} | CPM: ₹{clearing:.0f} | {dur:.0f}ms")
        return bids, winning_ad, dur

