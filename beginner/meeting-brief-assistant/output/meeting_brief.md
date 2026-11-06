# Meeting Cheat-Sheet: Flipkart | 2 PM
**Topic:** AI integration  |  **Prepared:** 2026-11-05

## 1. Intro (30-second read)
You are meeting the Flipkart team at 2 PM to discuss AI integration. Goal: understand where it fits in their plans, what limits them, and leave with one concrete next step.

**Flipkart tech snapshot**
- Microservices and event-driven backend (Kafka-style streaming), engineered around huge sale-day traffic spikes such as Big Billion Days.
- Very low-latency data layer (engineers publicly mention Aerospike), with most backend compute reported around Bengaluru and Chennai.
- Platform-first direction: one unified stack behind Flipkart, Minutes and Shopsy, with AI reported in logistics, fraud detection and pricing/offers.
_Source: public sources, checked 2026-11: dev.to (Big Billion Days architecture write-up), digit.in (Flipkart Tech Day 2025 coverage), public Flipkart job listings. Verify before quoting._

## 2. Questions to ask
1. **Which one or two workflows at Flipkart should AI improve first, and how will you measure success (cost, speed, conversion)?**
   _Why: Forces a concrete, measurable first use case instead of vague AI ambition._
2. **How ready is your data for this: where does it live, who owns it, and how fresh is it?**
   _Why: Most AI projects stall on data access and quality, not on the model._
3. **How would AI features plug into your existing services and event pipelines without hurting latency or reliability at peak load?**
   _Why: Shows whether the integration is a quick add-on or a deep re-architecture._
4. **Build vs buy: will you use hosted model APIs, open-source models or in-house ones, and what are your privacy and compliance limits?**
   _Why: Decides cost, control, and what data is allowed to leave their systems._
5. **Who owns rollout and monitoring (accuracy, hallucinations, cost per request), and what is the fallback when the model is wrong?**
   _Why: Reveals whether there is an owner and a safety net, which predicts success._

## 3. Before you hang up
- Confirm the owner and date of the next step.
