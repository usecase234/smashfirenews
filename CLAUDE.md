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
- `DATABASE_URL` must use the `postgresql+psycopg://` scheme, not plain
  `postgresql://`. The project depends on psycopg 3
  (`psycopg[binary]>=3.1` in `hub/pyproject.toml`), and SQLAlchemy defaults
  a bare `postgresql://` URL to psycopg2, which isn't installed — the app
  crashes at startup with `ModuleNotFoundError`. Railway supplies the bare
  scheme by default, so it must be overridden.
- `SMASHFIRE_HUB_URL` and `SMASHFIRE_SITE_CREDENTIAL` go in dv7's
  `wp-config.php` as `define()` constants, never in a plugin settings
  screen. `Smashfire_Hub_Client` (`plugin/includes/class-hub-client.php`)
  only ever reads them via `defined()`/constant lookup — there is no
  options-table path for the site credential, so it can't leak through a
  WordPress export/backup or be edited by anyone with only `edit_posts`.
- Windows-built plugin zips cannot be installed through WordPress's
  Add Plugin uploader on dv7.com's host: `Compress-Archive` writes
  backslash (`\`) path separators, which this host's zip extraction
  doesn't accept, so the upload silently fails to lay out files
  correctly. Deploy by uploading files individually through cPanel File
  Manager, or upload the zip and extract it via cPanel's own extractor —
  never via WordPress's plugin uploader.

## Where we are

**Phases 0–3 complete, committed, deployed, and verified end to end.**
Phase 3 (thin vertical slice) had been built locally but was never
committed until commit `04df2b5` — that gap is now closed, and the
dv7.com smoke test below confirms the whole loop works in production.

**Phase 4 is now in progress**: the Redis-backed queue worker, prompt
service, AI router (DeepSeek V4 Flash and GPT-5.6 Luna as initial
candidates), usage ledger, and rewrite-with-versioning (Draft V2 without
touching V1) that replace the Phase 3 stub. See "Phase 4 decisions"
below for the constraints this work must hold to.

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
screens are still Phase 0 placeholders.

Infra: the Hub moved from the Railway project `intelligent-wonder` to
`industrious-intuition`, so the Hub, Postgres, and Redis now all live in
one project on private networking. The old service in `intelligent-wonder`
still exists and needs to be deleted. New Hub URL:
`https://smashfirenews-production-8575.up.railway.app`. Verified working in
production: `/health` returns `ok`, `/docs` lists all Phase 3 routes, and
`GET /submissions` with the installation credential returns `[]`.

**The dv7.com smoke test is complete and verified end to end**: public
submission form (`?smashfire_pr_submit=1`) → Hub intake → Generate Draft
from the Incoming screen → Draft V1 (`stub-v1`) appears in Finished
Drafts → Publish Now creates a live WordPress post — all driven through
the wp-admin UI, not curl, with a clean debug log. Getting there also
surfaced and fixed real bugs, not just config: `register_post_type()`
silently failed because `smashfire_pr_submission` (23 chars) was over
WordPress's 20-char post-type-name limit, now `smashfire_submission`; a
duplicate `add_submenu_page()` registration for Incoming; and the
temporary `error_log` calls added to `enqueue_admin_ui()` while
diagnosing an earlier blank-screen issue (root cause was a missing
`admin-ui/build/` on the server, unrelated to any of the above) have been
removed now that the screen renders correctly.

Next: finish Phase 4 (see below), then Phase 5 security/quota hardening.

Update this section as phases complete — it's the one thing worth keeping
current instead of re-explaining status every session.

## Phase 4 decisions

- Exactly five constrained AI actions, each its own service function:
  `analyze_submission`, `generate_publisher_draft`, `rewrite_draft`,
  `generate_headlines`, `classify_relevance`. No generic
  prompt-passthrough endpoint under any circumstances.
- Each action gets its own prompt template, versioned in code.
- Per-publisher voice profiles are a deliberate addition to the build
  plan's Phase 4 scope — not called for by name in the build plan's Phase
  4 section, but added on purpose so `generate_publisher_draft` and
  `rewrite_draft` have a persistent voice to read from rather than
  landing later as a retrofit.
- The queue worker runs as a separate Railway service inside the
  `industrious-intuition` project (alongside the Hub, Postgres, and
  Redis). It must import `hub/app/core/config.py` rather than reading
  env vars independently, so the `postgresql+psycopg://` DATABASE_URL
  normalization (see hard rules above) applies to the worker too, not
  just the API process.
- Model pricing lives in a config table, not inline constants — so
  rate changes and new model candidates don't require a code deploy.

## Repo layout

- `hub/` — Python FastAPI control plane (multi-tenant, owns AI/billing/data)
- `plugin/` — WordPress plugin, thin client, Buddy Magazine's connector
- `infra/` — docker-compose + env templates for local dev
- `docs/` — source plan + build plan (read these, don't duplicate them here)
