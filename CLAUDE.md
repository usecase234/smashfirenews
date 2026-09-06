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

**Currently on: Phase 1 (Hub tenancy skeleton) — complete.**
`publishers`/`publisher_installations` migration applied, `TenantScopedMixin`
+ `tenant_scoped_select` are the only sanctioned way to query tenant-owned
tables, `TenantResolutionMiddleware` resolves bearer credentials to a
`TenantContext` (401 before any route runs), and Buddy Magazine seeds
idempotently as `publisher_id=1`. Isolation is tested at the query-
construction level, not just on current data. Next: Phase 2 (WordPress
plugin skeleton).

Update this section as phases complete — it's the one thing worth keeping
current instead of re-explaining status every session.

## Repo layout

- `hub/` — Python FastAPI control plane (multi-tenant, owns AI/billing/data)
- `plugin/` — WordPress plugin, thin client, Buddy Magazine's connector
- `infra/` — docker-compose + env templates for local dev
- `docs/` — source plan + build plan (read these, don't duplicate them here)
