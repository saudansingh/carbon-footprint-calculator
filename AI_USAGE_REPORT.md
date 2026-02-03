# AI Usage Report

Project: Carbon Footprint Calculator & Tracker with AI-Powered Recommendations

Author: Cascade (Senior Full-Stack & AI Engineer)
Date: 2026-02-02

## Objectives of AI Integration
- Provide actionable, personalized sustainability recommendations based on a user’s recent emissions history.
- Complement deterministic analytics (emission factors and aggregations) with adaptive advice that reflects the user’s unique patterns across transport, energy, and food.
- Maintain safe operation under API errors, missing keys, or rate limits via deterministic heuristics.

## Model and Provider
- Primary: OpenAI Chat Completions (configurable model, default `gpt-4o-mini`).
- Integration: Server-side API calls from Flask to reduce key exposure and centralize rate limits.
- Fallbacks: Deterministic heuristic engine when API is unavailable, errors occur, or rate limits are hit.

## Prompt Design
- System prompt persona: “Sustainability coach” requiring concise, high-impact, personalized recommendations.
- Output format: Strict JSON: `{ items: [{ category, advice }] }` where category ∈ {transport, energy, food, general}. This structure simplifies parsing and rendering on the frontend.
- User content payload: A compact JSON-like string containing:
  - User profile: name, email (email is not required for reasoning but can improve personalization; consider redaction for strict privacy policies).
  - Summary: total and by-category emissions over a recent window (default 30 days).
  - Recent activities (max 50): date, type, category, emission_kg, normalized activity data.
- Sampling parameters: Low temperature (0.4) encourages consistent, pragmatic advice.

Sample system directive (abridged):
“Analyze recent carbon emissions and provide 6 concise, high-impact, personalized recommendations. Tailor across transport, energy, and food. Each item must be a single sentence. Output JSON with `items` [{category, advice}]. Categories limited to: transport, energy, food, general.”

## Personalization Logic
- The model receives normalized, categorized emissions and recent activities. This enables:
  - Targeting the dominant category (e.g., transport-heavy patterns → mode-shift and trip-chaining suggestions).
  - Contextual electricity advice based on sustained high kWh usage trends.
  - Dietary nudges when food-related emissions spike (e.g., frequent beef consumption).
- The deterministic heuristic fallback mirrors this logic at a simpler level so users always receive value, even without the AI model.

## Rate Limiting and Abuse Prevention
- Server maintains a per-user timestamp in `ai_usage` and enforces a minimum interval (`AI_RATE_LIMIT_SECONDS`, default 30s) between requests.
- If a request arrives too soon, the endpoint returns heuristic recommendations and `source: "rate_limit"`.
- This avoids unnecessary API calls, controls cost, and reduces the risk of hammering the model.

## Reliability & Fallback Strategy
- If no `OPENAI_API_KEY` is configured or the SDK/client errors, the system returns fallback/heuristic output with `source: "heuristic"` or `"fallback"`.
- The parser attempts to extract JSON from the model response safely. If parsing fails, it gracefully reverts to heuristic advice.

## Privacy & Security Considerations
- Keys are handled via environment variables and never committed into the repo.
- API calls originate from the backend to shield the key from the client.
- Profile shape is minimal (name/email). If stricter privacy is required:
  - Remove email entirely from the payload.
  - Pseudonymize profile and avoid personally identifying information (PII).
- Data retention: This reference implementation does not store model outputs. If you choose to log AI outputs, redact sensitive fields and comply with data policies.

## Cost Management
- Rate limiting significantly reduces redundant calls.
- Payloads are compact (50 recent records cap) to minimize tokens.
- Low temperature reduces retries due to malformed output.
- Optional: Add daily quotas per user/org and an admin-configurable toggle to disable AI when costs exceed budgets.

## Evaluation and Quality
- Qualitative checks: Advice specificity, variety across categories, and feasibility for an average user.
- Quantitative proxy: Click-through or acknowledgment on the frontend when users apply suggestions (future enhancement).
- A/B test opportunity: Compare AI vs. heuristic outcomes (user satisfaction, activity logging frequency, trend improvements).

## Risks & Mitigations
- Hallucination or generic advice: Constrained categories and JSON format reduce drift; low temperature encourages consistent actionable items.
- Out-of-scope recommendations: The frontend labels each recommendation with its category and source, allowing users to interpret and trust appropriately.
- API downtime: Heuristic fallback ensures continuous service.

## Deployment & Operations
- Configure environment variables: `OPENAI_API_KEY`, `AI_MODEL`, `AI_RATE_LIMIT_SECONDS`.
- Monitor: Track 500s on `/api/recommendations`, distribution of `source` values, and average latency.
- Observability: Add structured logs (not included by default) to analyze prompt, response size, and parse outcomes (ensure redaction for privacy).

## Future Enhancements
- Multi-provider failover (e.g., Gemini or local LLM when available).
- Fine-grained per-category prompts to increase specificity.
- User goal setting: let users prioritize “reduce transport” or “reduce energy” and bias recommendations accordingly.
- Reinforcement feedback loop: thumbs up/down on each suggestion to improve future recommendations.

## Summary
This AI layer augments deterministic emissions analytics with personalized, actionable guidance. It is built with safety (rate limits, fallbacks), privacy (backend-only key usage), and cost control (windowed data, capped history) in mind. The system delivers consistent value even in degraded modes, and is structured for iterative improvement as usage insights accumulate.
