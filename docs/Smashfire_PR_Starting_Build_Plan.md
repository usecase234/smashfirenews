# Smashfire PR — Starting Build Plan

**Goal of this doc:** get from zero to a working local environment with the right
architectural bones in place, structured as a sequence of small, well-scoped phases
you can hand to Claude Code one at a time. Each phase ends in something runnable.

The plan follows the doc's core boundary: **the Hub and the WordPress plugin are
two separate codebases from day one**, even though Buddy Magazine is the only
tenant/client at first. Do not let that boundary blur for convenience — it's the
whole point of the architecture.

---

## Phase 0 — Repo & local environment scaffolding

**Objective:** two repos (or one monorepo with two clearly separated apps), a
docker-compose stack for local Postgres/Redis, and environment variable
templates. Nothing product-specific yet.

### Repo layout (monorepo recommended for v0.1, since one person/team is building both sides)

```
smashfire-pr/
├── hub/                      # Python FastAPI control plane
│   ├── app/
│   │   ├── api/               # REST routes
│   │   ├── core/              # config, security, tenancy middleware
│   │   ├── db/                # models, migrations (alembic)
│   │   ├── services/          # submission, prompt, ai_router, usage, billing
│   │   ├── workers/           # queue consumers
│   │   └── main.py
│   ├── tests/
│   ├── alembic/
│   ├── pyproject.toml
│   └── Dockerfile
├── plugin/                   # WordPress plugin (Buddy's first client)
│   ├── smashfire-pr.php       # bootstrap
│   ├── includes/              # CPT registration, REST client, admin pages
│   ├── admin-ui/               # React admin app (queue views)
│   ├── composer.json
│   └── package.json
├── infra/
│   ├── docker-compose.yml     # postgres, redis, hub, (optional wordpress+mysql for local plugin dev)
│   └── .env.example
└── docs/
    └── Smashfire_PR_Full_Product_Technical_Plan_2026.md   # this source plan, kept as living reference
```

Keep the source plan doc in `docs/` — Claude Code should be pointed at it as
context for every phase below, since it encodes the actual decisions (tenant
isolation, versioning rules, model routing, etc.) that the code needs to match.

### docker-compose (local dev)

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: smashfire
      POSTGRES_PASSWORD: smashfire
      POSTGRES_DB: smashfire_hub
    ports: ["5432:5432"]
    volumes: ["pgdata:/var/lib/postgresql/data"]

  redis:
    image: redis:7
    ports: ["6379:6379"]

  wordpress:            # optional, for plugin dev only
    image: wordpress:php8.2-apache
    depends_on: [mysql]
    ports: ["8080:80"]
    volumes:
      - "./plugin:/var/www/html/wp-content/plugins/smashfire-pr"

  mysql:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: wordpress
      MYSQL_DATABASE: wordpress

volumes:
  pgdata:
```

### Env template (`infra/.env.example`)

```
# Hub
DATABASE_URL=postgresql://smashfire:smashfire@postgres:5432/smashfire_hub
REDIS_URL=redis://redis:6379/0
HUB_JWT_SECRET=change-me
AI_PROVIDER_KEYS=          # never present in plugin env, only Hub
STRIPE_SECRET_KEY=
CLOUDFLARE_TURNSTILE_SECRET=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
RESEND_API_KEY=

# Plugin (no provider keys here, ever)
SMASHFIRE_HUB_URL=http://hub:8000
SMASHFIRE_SITE_CREDENTIAL=
```

**Claude Code task for this phase:** "Scaffold the repo layout above, add the
docker-compose file and .env.example, initialize `pyproject.toml` for the Hub
with FastAPI + SQLAlchemy + Alembic + Redis client, and initialize
`composer.json`/`package.json` for the plugin. No business logic yet — just a
`GET /health` route in the Hub and a plugin bootstrap file that registers an
empty admin menu page."

---

## Phase 1 — Hub foundations: tenancy, not features

**Objective:** the multi-tenant skeleton the doc insists on — before any
submission/draft/AI logic exists. This is the phase most likely to get skipped
under time pressure, and it's the one the doc says not to skip.

- Alembic migration #1: `tenants` / `publishers` table, plus a Postgres
  convention that **every subsequent table gets a `publisher_id` FK from its
  first migration**, not retrofitted later.
- Tenant-resolution middleware: every authenticated request resolves to exactly
  one `publisher_id`; no query path is allowed to omit the tenant filter.
- Seed one row: Buddy Magazine as `publisher_id = 1` / Tenant #001.
- Per-installation credential model (plugin auth token → publisher_id), issued
  by the Hub, never an LLM provider key.

**Claude Code task:** "Implement the tenancy layer described in Phase 1: base
`Tenant`/`Publisher` model, a SQLAlchemy mixin or base class that all future
tables inherit for `publisher_id`, auth middleware that resolves and injects
the current tenant, and a seed script creating Buddy as Tenant #001. Write a
test that proves a request scoped to one tenant cannot read another tenant's
rows, even before any other tenant exists — assert on query construction, not
just current data."

This test is worth writing now, even with one tenant, because it's the thing
that silently breaks if someone later takes a shortcut for tenant #2.

---

## Phase 2 — WordPress plugin skeleton (Buddy connector)

**Objective:** a thin plugin that can talk to the Hub, with no business logic
of its own beyond CPT registration and REST proxying.

- Register `smashfire_pr_submission` and `smashfire_pr_asset` as CPTs (or
  decide now if assets go in dedicated tables per the doc's suggestion for
  high-volume records).
- REST client wrapper (`wp_remote_request`) that calls the Hub with the signed
  site credential — this is the *only* way the plugin reaches the Hub.
- Empty admin screens: Incoming / Drafts / Published / Senders / Settings,
  matching the doc's screen list, with placeholder React components.

**Claude Code task:** "Build the plugin skeleton in Phase 2: CPT registration,
a `SmashfireHubClient` PHP class wrapping `wp_remote_request` with the signed
credential header, and five empty admin submenu pages under Posts → Smashfire
PR, each rendering a placeholder React root. No submission form yet."

---

## Phase 3 — Thin vertical slice: one submission end to end

**Objective:** prove the loop, not the product. One hardcoded-simple path:
paste-text submission → Hub stores it → editor sees it in Pre-Writer queue →
manual "generate draft" call → Draft V1 stored → editor publishes to WordPress.

No AI yet — stub `generate_publisher_draft` to echo the input text back as a
"draft" so the *pipes* are proven before the *model* is.

- Submission endpoint on the Hub (pasted-text only; DOCX/PDF/media wait).
- `Submission` and `DraftVersion` tables (Original → Draft V1, immutable
  source per the doc).
- Queue table + a synchronous stub instead of Redis/worker for now — swap in
  Phase 4.
- Plugin: submission form (unlisted URL, no Turnstile/rate-limit yet — Phase
  5), Pre-Writer view pulling from Hub, Publish action creating a real
  WP post.

**Claude Code task:** "Implement the vertical slice in Phase 3 end to end,
using a synchronous stub for draft generation (return the input text
unmodified, tagged `stub-v1`). Confirm manually: submit → appears in queue →
generate → appears in Finished Drafts → publish creates a WordPress post with
the source provenance stored but not publicly displayed."

This is the milestone worth demoing before going further — it validates the
architecture boundary works before any AI cost is spent.

---

## Phase 4 — Queue + AI pipeline

**Objective:** replace the Phase 3 stub with the real pipeline: Redis/queue
worker, prompt service, AI router with DeepSeek/GPT-5.6 Luna as initial
candidates, usage ledger.

- Worker process consuming from Redis, calling the constrained action set
  (`analyze_submission`, `generate_publisher_draft`, `rewrite_draft`,
  `generate_headlines`, `classify_relevance`) — never a raw prompt passthrough.
- Usage ledger table: tokens, model, cost, status per job.
- Rewrite action: takes editor notes, creates Draft V2 without touching V1.

**Claude Code task:** "Wire the Phase 3 stub into a real Redis-backed queue
worker. Implement the five constrained AI actions as separate service
functions, each with its own prompt template versioned in code. Add the usage
ledger and wire cost estimation using the pricing table in the source plan.
Do not add a generic prompt-passthrough endpoint under any circumstance."

---

## Phase 5 — Security, quotas, abuse prevention

Layer this in once the happy path works, not before:

- Cloudflare Turnstile server-side validation on the public submission form.
- Honeypot, IP/email rate limits, duplicate fingerprinting, file allowlist +
  MIME/signature checks, randomized storage names, uploads outside executable
  paths.
- Hard per-publisher/user/action quotas enforced at the Hub (works even if the
  plugin is modified) plus an account-level dollar ceiling.

**Claude Code task:** "Add the security layer from Phase 5 to the existing
submission endpoint and worker, without changing the Phase 3/4 data model.
Write a test that a request exceeding the quota is rejected at the Hub even
when the plugin-side check is bypassed."

---

## Phase 6 — Billing, storage, observability

- Cloudflare R2 for asset storage (swap out local disk from earlier phases).
- Stripe Checkout + Billing at the Hub level only.
- Sentry + structured logging; a dashboard on job failures, cost anomalies,
  latency, auth abuse.

---

## Phase 7 — Validate the v0.1 hypotheses

Once Buddy is live, instrument for the metrics the source plan names:
submission completion rate, editor acceptance rate, edit distance,
time-to-publish, % rejected at triage, actual cost per published story. Don't
build new features in this phase — build the measurement.

---

## How to run this with Claude Code

- Keep `docs/Smashfire_PR_Full_Product_Technical_Plan_2026.md` (the source
  plan) in the repo and reference it explicitly in prompts — it has the actual
  constraints (tenant isolation, versioning, constrained AI actions) that
  generic scaffolding won't know to enforce.
- Work one phase per session/PR. Each phase above is scoped to end in
  something you can run and check by hand.
- Ask for a test alongside every phase that encodes an architectural rule from
  the source doc (tenant isolation, immutable original + versioned drafts, hard
  quota enforcement) — these are the rules most likely to erode under later
  time pressure, and a test catches that early.
- Don't let Phase 3's synchronous stub quietly become production — Phase 4
  exists specifically to replace it.
