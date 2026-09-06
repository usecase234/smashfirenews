# Smashfire PR

Read `docs/Smashfire_PR_Full_Product_Technical_Plan_2026.md` and
`docs/Smashfire_PR_Starting_Build_Plan.md` before proposing architecture or
starting a new phase. The first is the source of truth for product/architecture
decisions; the second is the phase sequence we're executing against.

## Hard rules from the source plan — do not violate these for convenience

- The Hub and the WordPress plugin are separate systems. The plugin never
  holds an LLM provider key and never calls a provider directly.
- Every Hub table carries `publisher_id` from its first migration. No
  tenant-scoped query path is allowed to omit the tenant filter.
- Original submissions are immutable. AI/editorial outputs are versioned
  derivatives (Draft V1, V2, ...) — never overwritten in place.
- No generic prompt-passthrough endpoint, ever. Only the named actions:
  `analyze_submission`, `generate_canonical_release`,
  `generate_publisher_draft`, `rewrite_draft`, `generate_headlines`,
  `classify_relevance`.
- Publisher quotas are enforced at the Hub, even if a local plugin
  installation is modified.

## Where we are

**Currently on: Phase 2 (WordPress plugin skeleton) — complete.**
`smashfire_pr_submission` registered as a non-public CPT (no native edit
screen — editorial workflow lives entirely under the plugin's own admin
menu); `smashfire_pr_asset` deliberately kept out of the CPT system and
given its own dbDelta-created table instead, per the doc's high-volume
guidance. `Smashfire_Hub_Client::request()` is now the single choke point
for every Hub call — nothing else may call `wp_remote_request` against the
Hub. The five admin screens (Incoming/Drafts/Published/Senders/Settings)
were already scaffolded in Phase 0 and still render placeholder React
roots — no submission form yet. Next: Phase 3 (thin vertical slice: one
submission end to end).

Update this section as phases complete — it's the one thing worth keeping
current instead of re-explaining status every session.

## Repo layout

- `hub/` — Python FastAPI control plane (multi-tenant, owns AI/billing/data)
- `plugin/` — WordPress plugin, thin client, Buddy Magazine's connector
- `infra/` — docker-compose + env templates for local dev
- `docs/` — source plan + build plan (read these, don't duplicate them here)
