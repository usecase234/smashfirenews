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

**Currently on: Phase 3 (thin vertical slice) — complete.**
Hub: `submissions` and `draft_versions` tables (both `TenantScopedMixin`,
migration `8f2a6c9d1b30`); `POST /submissions`, `GET /submissions`,
`GET /submissions/{id}`, `POST /submissions/{id}/generate-draft` (the
`generate_publisher_draft` action — a stub that echoes the original text
back tagged `stub-v1`, never overwriting a prior version), and
`POST /submissions/{id}/publish` (records wp_post_id/live_url/published_at;
409s if no draft exists yet). All reads go through `tenant_scoped_select`;
`hub/tests/test_submissions.py` covers the end-to-end flow, the
no-draft-no-publish rule, immutable-original/versioned-draft behavior, and
cross-tenant isolation on the new tables.

Plugin: `Smashfire_Hub_Client` grew typed methods (`submit_release`,
`list_queue`, `list_drafts`, `get_submission`, `generate_draft`,
`mark_published`) — `request()` now also turns a non-2xx Hub response into
a `WP_Error` instead of returning the error body as if it were success.
`Smashfire_PR_Public_Submission` serves an unlisted, noindexed submission
form at `?smashfire_pr_submit=1` via `admin-post.php` (no Turnstile/rate
limiting — that's Phase 5). `Smashfire_PR_Rest_Routes` exposes an
`edit_posts`-gated `smashfire-pr/v1` REST proxy (`/queue`, `/drafts`,
generate-draft, publish) that the Incoming/Drafts admin screens
(`admin-ui/src/index.js`) call live — there is still no local mirror of Hub
data. `Smashfire_PR_Publisher::publish_submission()` is the one place that
isn't a pure Hub proxy: it pulls the latest draft, creates a real
`wp_insert_post`, stores provenance in underscore-prefixed (private)
postmeta, then reports the post back to the Hub. Published/Senders/Settings
screens are still Phase 0 placeholders. Next: Phase 4 (replace the stub
with a real Redis-backed queue worker and the AI router).

Update this section as phases complete — it's the one thing worth keeping
current instead of re-explaining status every session.

## Repo layout

- `hub/` — Python FastAPI control plane (multi-tenant, owns AI/billing/data)
- `plugin/` — WordPress plugin, thin client, Buddy Magazine's connector
- `infra/` — docker-compose + env templates for local dev
- `docs/` — source plan + build plan (read these, don't duplicate them here)
