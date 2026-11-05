"""Built-in research notes (offline 'search' results).

The Flipkart notes were gathered from public web sources on 2026-11-03
(engineering write-ups, press coverage of Flipkart Tech Day, public job listings).
They are NOT official statements. Re-check before quoting them in a meeting.
Add more companies here, or replace `lookup` with a real search API call.
"""
import re

PROFILES = {
    "flipkart": {
        "as_of": "2026-11",
        "points": [
            "Microservices and event-driven backend (Kafka-style streaming), engineered around "
            "huge sale-day traffic spikes such as Big Billion Days.",
            "Very low-latency data layer (engineers publicly mention Aerospike), with most backend "
            "compute reported around Bengaluru and Chennai.",
            "Platform-first direction: one unified stack behind Flipkart, Minutes and Shopsy, with "
            "AI reported in logistics, fraud detection and pricing/offers.",
        ],
        "sources": [
            "dev.to (Big Billion Days architecture write-up)",
            "digit.in (Flipkart Tech Day 2025 coverage)",
            "public Flipkart job listings",
        ],
    },
}


def _key(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def lookup(company: str):
    return PROFILES.get(_key(company))
