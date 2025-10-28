## Output template for Clickbait Agent

This folder contains a strict JSON output template the LLM must conform to when returning analysis results.

Files
- `output_template.json` — schema-shaped template with all required keys. Values are intentionally empty or null to avoid anchoring.

**Note:** As of version 1.2.3 (2025-10-28), the output schema now includes a **required `summary` field** that contains an objective 2-4 sentence summary of the article's content (not the clickbait analysis).

Guidelines for integrators and prompts
1. Always pass the template schema to the LLM as an *empty* template (keys present, values empty). Do NOT include example values for `score`, `label`, `rationale`, `signals` or other result fields in the prompt.
2. Before calling the LLM, sanitize the article input payload to remove any prefilled output fields (for example: `score`, `label`, `rationale`, `rationale_user_friendly`, `signals`, `suggestions`, `diagnostics`, `summary`). See the recommended sanitization function in codebase.
3. If you need to show examples to the LLM for offline calibration, keep those examples outside production prompts. Use a separate offline dataset (e.g., `tests/fixtures/examples.json`) and never include it in production calls.
4. Require the LLM to output EXACTLY the JSON structure of `output_template.json`. Use strict schema validation after generation and reject outputs that omit required fields or return additional top-level analysis values.
5. For semantic hits, require LLM to populate `title_semantic_hits` and `content_semantic_hits` entries as objects with `text` and `confidence` fields and keep `confidence` >= `counting_policy.semantic_confidence_threshold`.
6. **Summary field**: The LLM must generate a `summary` field (2-4 sentences, max 400 chars) describing what the article is about - its main topic and key facts. The summary must be objective, neutral, and informative. It should NOT describe the clickbait analysis or scoring.
7. Enforce deterministic mode: set `seed` in the system and apply post-processing rounding rules (nearest 5) as described in the spec.

Sanitization checklist (pre-LM)
- Remove: `score, label, rationale, rationale_user_friendly, signals, suggestions, diagnostics, summary` from input article.
- Replace any sample analysis blocks with the empty `output_template.json` if you need to show structure.

Validation checklist (post-LM)
- Verify required fields exist: `id, source, url, score, label, rationale, rationale_user_friendly, signals, suggestions, summary`.
- Validate types and bounds: e.g., `score` in [0,100], `label` one of allowed enums, `summary` is non-empty string with max 400 chars.
- For each field in `signals`, ensure that regex hits are present when claimed and semantic hits include `confidence`.

Why this matters
- Providing an empty, enforced template prevents anchoring and ensures the LLM returns all required fields in a consistent format. Prefilled or example-filled templates can bias outputs.

If you want, I can add a small helper `tools/sanitize_input.py` and update `tools/enforce_output_schema.py` to accept a `--template` flag and reject outputs that diverge from the template. Ask and I'll implement both (with tests).

