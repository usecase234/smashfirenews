# Smashfire PR — Claude Code Setup + First Tech Stack

Companion to `Smashfire_PR_Starting_Build_Plan.md`. That doc is the phase
sequence; this one is "what do I actually install and sign up for this week."

---

## 1. Install and start Claude Code

**Requirements:** a Claude Pro, Max, Team, Enterprise, or Console account (the
free claude.ai plan doesn't include Claude Code access).

**Install (macOS/Linux/WSL):**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```
**Windows PowerShell:**
```powershell
irm https://claude.ai/install.ps1 | iex
```
Alternatives: `brew install --cask claude-code`, `winget install
Anthropic.ClaudeCode`, or `npm install -g @anthropic-ai/claude-code` (needs
Node 22+, avoid `sudo npm install -g`).

Verify and log in:
```bash
claude --version
claude          # launches the REPL, prompts you to authorize in the browser
```

### First session in the repo

```bash
mkdir smashfire-pr && cd smashfire-pr
git init
mkdir docs
cp /path/to/Smashfire_PR_Full_Product_Technical_Plan_2026.md docs/
cp /path/to/Smashfire_PR_Starting_Build_Plan.md docs/
claude
```

Inside the session, run `/init` — Claude Code will scan the (currently empty)
repo and draft a `CLAUDE.md`. Edit it to explicitly point at the two docs, e.g.:

```markdown
# Smashfire PR

Read docs/Smashfire_PR_Full_Product_Technical_Plan_2026.md and
docs/Smashfire_PR_Starting_Build_Plan.md before proposing architecture.

Hard rules from the source plan:
- Hub and WordPress plugin are separate systems. Never let the plugin hold
  an LLM provider key or call a provider directly.
- Every Hub table carries publisher_id from its first migration.
- Original submissions are immutable. Drafts are versioned, never overwritten.
- No generic prompt-passthrough endpoint, ever — only the named actions
  (analyze_submission, generate_publisher_draft, rewrite_draft,
  generate_headlines, classify_relevance).

We are currently on: Phase 0 (repo + local env scaffolding).
```

`CLAUDE.md` is read automatically at the start of every session in this repo,
so this is the one place worth keeping current — update the "currently on"
line as you move through phases instead of re-explaining context each time.

Then give it the actual Phase 0 task from the build plan verbatim as your
first prompt. Work phase by phase, one Claude Code session/PR per phase,
rather than asking for the whole system at once — the build plan is already
structured that way.

A couple of settings worth knowing about early:
- `claude doctor` — diagnoses install/config issues.
- Permissions: Claude Code asks before running commands or editing files by
  default; for a fast-moving prototype repo you can pre-approve safe
  categories (e.g. file edits, `git`, `npm`, `docker compose`) via `/config`
  or `.claude/settings.json` rather than confirming every single action —
  worth doing once Phase 0 is scaffolded and you trust the loop.

---

## 2. First tech setup — accounts and services

The source plan already names specific vendors. Here's what to actually
provision, mapped to what you need **this week** vs. what can wait.

### This week (prototype, cheap/free tiers)

| Service | Why | Tier to start on |
|---|---|---|
| **GitHub** (or GitLab) | Repo hosting, so Claude Code's commits/PRs live somewhere | Free |
| **Neon** — Postgres | Hub's canonical DB | Free tier for early dev; move to Launch (~$15/mo usage-based) once you deploy a persistent staging environment |
| **Upstash** — Redis | Queue for AI jobs | Free tier (enough for prototype volume) |
| **Railway** | Hosts the Hub API + worker process | Hobby ($5/mo minimum) — enough until an external publisher depends on uptime |
| **Cloudflare** account | R2 (object storage) + Turnstile (bot protection) | Free — R2 is pay-as-you-go and negligible at prototype scale; Turnstile is free |
| **Resend** | Transactional email (submission receipts, live-post notification) | Free tier |
| **Stripe** | Not needed yet — billing is a Phase 6 concern | Skip for now |
| **Sentry** | Error tracking | Free tier, add once Phase 3's vertical slice is live |

### Also needed this week, but not a new signup

- **A WordPress site to develop the plugin against.** Two options, not
  mutually exclusive:
  1. Local WordPress via the `docker-compose.yml` from the build plan (fast
     iteration, no network dependency).
  2. A real staging copy of Buddy Magazine's WordPress site (or a fresh
     staging WP install) once you need to test against real hosting,
     real plugins/theme conflicts, and a public-facing submission URL.
- **AI provider keys** (DeepSeek, OpenAI) — needed once you reach Phase 4, not
  Phase 0. Get API keys but don't wire them in until the queue/worker exist;
  the Hub is the only place that ever holds them.

### Order of operations for day 1

1. Create the GitHub repo, push the Phase 0 scaffold Claude Code just built.
2. Create Neon project → copy the connection string into `.env` (local) —
   don't put real credentials in git; keep `.env` gitignored and only commit
   `.env.example`.
3. Create Upstash Redis database → copy the REST/Redis URL.
4. Create a Railway project, connect it to the GitHub repo, but **don't
   deploy yet** — get through Phase 1 (tenancy) locally first so you're not
   debugging infra and data model at the same time.
5. Once Phase 1 passes its tenant-isolation test locally, deploy the Hub to
   Railway pointing at the *hosted* Neon/Upstash (not local docker) — this
   gives you a real public URL for the plugin to call.
6. Point the WordPress plugin's `SMASHFIRE_HUB_URL` at that Railway URL
   (local WP-in-docker can reach the internet fine; a real staging WP site
   needs it too).
7. Cloudflare: create the R2 bucket and Turnstile site key — wire both in
   around Phase 3 (assets) and Phase 5 (bot protection) respectively, not
   before, so you're not holding unused credentials.

### Why deploy the Hub early instead of staying fully local

Local docker-compose is great for iterating on the Hub in isolation, but the
WordPress plugin side needs a real, stable URL to call fairly early — even a
locally-run WordPress instance benefits from hitting a real staging Hub
rather than juggling tunnels. Get a bare-bones `/health` Hub onto Railway
right after Phase 0, then let Phase 1–3 deploy incrementally to that same
environment. Keep local docker-compose around for fast iteration and tests;
treat Railway staging as the integration environment the plugin actually
talks to.

---

## 3. Rough monthly cost at this stage

Everything above stays under **~$25–35/month** total while Buddy is the only
tenant (Railway Hobby $5, Neon free→~$15 once you outgrow free tier, Upstash
free, R2/Turnstile/Resend effectively free at this volume). This matches the
source plan's own framing: AI token cost is not the primary cost driver at
prototype volume — infra minimums are. Move to the "later" column (Supabase
Pro, Railway Pro, SES) only when a second tenant or real traffic justifies it.
