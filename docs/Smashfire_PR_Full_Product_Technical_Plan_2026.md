**SMASHFIRE PR**

Full Product, Technical Architecture & Economics Plan

Independent multi-tenant platform → Buddy Magazine Tenant #001 →
multi-publisher WordPress network → paid niche press-release wire

Prepared September 5, 2026

  -----------------------------------------------------------------------
  **Core thesis: the plugin is the publisher workflow; the Hub is the
  controlled intelligence, metering and future distribution network.
  Build Buddy as the first network node, even while the first release
  only supports a private-by-distribution web form.**
  -----------------------------------------------------------------------

  -----------------------------------------------------------------------

# Executive recommendation

![Smashfire PR workflow
flowchart](/home/claude/smashfire-pr/docs/media/media/image9.png){width="6.8in"
height="2.3175754593175855in"}

Build Smashfire PR v0.1 as an independent, multi-tenant platform with
Buddy Magazine as Publisher/Tenant #001 and its first WordPress client.
The Hub and primary database are separate from Buddy from day one. Do
not put LLM provider keys or canonical network data in the plugin. The
public submission page should be unlisted/noindexed but treated as a
public attack surface. The Hub owns model access, tenant isolation,
quotas, prompt templates, usage metering, sender/network identity,
provenance and versioned draft generation from day one.

> **•** Prototype intake first through a Buddy submission page; add
> email ingestion only after the form-to-editor workflow is proven.
>
> **•** Use one canonical Submission object that can originate from
> pasted text, structured fields, DOCX/PDF, and later email/API/network
> delivery.
>
> **•** Give editors two queue views: Pre-Writer (headlines/source
> packets) and Finished Drafts (ready to
> review/edit/rewrite/approve/publish).
>
> **•** Store every rewrite as a new version. Rewrite should accept
> optional editor instructions and always incorporate the publisher\'s
> persistent editorial profile.
>
> **•** Treat images, embeds, URLs, social handles and rights metadata
> as structured assets, not content pasted into an article body.
>
> **•** Meter every AI call centrally and enforce hard
> publisher/user/action caps at the Hub, with account-level dollar
> safety ceilings.
>
> **•** Architect the future wire as one canonical release delivered to
> many publisher endpoints; generate publisher-specific drafts only when
> selected or automatically qualified by publisher rules.
>
> **•** Use Stripe at the Hub level for paid quotas/subscriptions later;
> do not make WooCommerce the billing system.

## What v0.1 must prove

  -----------------------------------------------------------------------
  **Hypothesis**                      **Evidence to capture**
  ----------------------------------- -----------------------------------
  Publicists will use a submission    Submission completion rate; repeat
  page instead of only email          senders; abandoned submissions

  AI can make an editor-ready Buddy   Editor acceptance rate; rewrites
  draft                               per draft; edit distance;
                                      time-to-publish

  Headline-first triage saves         \% of submissions rejected before a
  money/time                          full draft; cost avoided

  The queue is faster than email →    Median minutes from intake to
  editor → AI → WordPress             editorial decision

  Media/metadata extraction is useful \% of published posts using
                                      supplied image/embed/link

  Usage is cheap enough to subsidize  Actual model cost per generated and
  a free publisher tier               published story
  -----------------------------------------------------------------------

# Architecture boundary: Smashfire PR is independent from Buddy Magazine

![Smashfire PR workflow
flowchart](/home/claude/smashfire-pr/docs/media/media/image1.png){width="6.8in"
height="4.834633639545057in"}

*Conceptual workflow diagram*

Smashfire PR must be deployed, named and modeled as a separate
product/backend from Buddy Magazine. Buddy is the first publisher tenant
and test client---not the database boundary, authentication authority,
billing authority, sender-reputation authority or AI control plane.

• The Hub and its PostgreSQL database are independently deployed and
tenant-aware from the first migration.

• Buddy Magazine is Publisher/Tenant #001. Buddy-specific voice,
categories, branding, intake rules and automation preferences are tenant
configuration, never hard-coded platform behavior.

• Every publisher-scoped Hub record carries publisher_id / tenant_id,
and authorization must enforce tenant isolation on every read, write,
job and asset access.

• The Hub is the canonical system of record for submissions, canonical
releases, assets/provenance, AI jobs and draft versions, sender
identity/reputation, quotas, metering, billing, distribution and audit
history.

• The WordPress plugin is a thin publisher-side client for intake
presentation, editorial workflow and final WordPress publishing.
Buddy\'s WordPress database is not the primary network database.

• Sender and network objects are reusable across publishers. A PR
organization, sender identity or canonical release must not be modeled
as belonging exclusively to Buddy.

• Adding publisher #002 must mean creating another isolated tenant and
connecting its WordPress installation---not extracting Buddy-specific
backend code into a new platform.

• Architectural shorthand: You aren\'t really building \'a Buddy
plugin.\' You\'re building a publisher editorial intake and AI workflow
platform, with a Buddy WordPress connector as its first client.

# Product definition

## Publisher-side product

**Smashfire PR is an AI newsroom intake and editorial queue inside
WordPress. It receives structured press-release packages, normalizes
them, optionally transforms them into the publication\'s editorial
voice, and lets an editor scan, rewrite, edit, approve, schedule and
publish with minimal context switching.**

## Future PR-side product

**Smashfire PR Wire is a targeted press-release distribution service
whose endpoints are WordPress editorial dashboards. A paid sender
distributes a canonical release to relevant participating publishers;
publishers retain editorial control; the network records delivery, view,
selection, draft generation and publication.**

# v0.1 Buddy user journeys

![](/home/claude/smashfire-pr/docs/media/media/image10.png){width="6.8in"
height="0.9647189413823272in"}

*Conceptual workflow diagram*

## Publicist submission

> **1.** Selected publicist receives the Buddy submission URL. The page
> is noindexed/unlisted but does not require login in v0.1.
>
> **2. Publicist enters contact/company details and either pastes a
> release, uploads DOCX/PDF, or provides structured facts from which
> Smashfire PR can generate a canonical release.**
>
> **3.** Publicist can upload approved image types and add
> YouTube/Spotify/other media links, source URLs and social handles.
>
> **4.** Publicist provides image credit/rights data and affirmatively
> confirms ownership or authorization for editorial use.
>
> **5.** Turnstile, rate limits, file validation and size caps run
> before the submission is accepted.
>
> **6. Smashfire PR returns a submission ID and places the item into
> Buddy\'s queue.**

## Editor workflow

> **1. Editor opens Posts → Smashfire PR.**
>
> **2.** Pre-Writer view shows incoming headline, source/sender,
> received date, category/relevance indicators and quick preview of the
> source package.
>
> **3.** Editor may select one or more items and request AI drafts,
> reject/archive items, or mark a sender as trusted/watch/block.
>
> **4.** Finished Drafts view shows editor-ready headlines and body
> previews. Editors can review without opening the full WordPress
> editor.
>
> **5.** Primary actions: Preview, Rewrite, Edit, Approve, Publish Now,
> Schedule, Reject.
>
> **6.** Rewrite opens a small prompt-notes field (for example: \'lead
> with the Dallas date; shorten biography\') and creates Draft V2 rather
> than replacing V1.
>
> **7. On publish, Smashfire PR creates/updates a normal WordPress post
> with selected image/embed/link metadata and retains source provenance
> privately.**

# Functional requirements --- v0.1

## Submission form

  -----------------------------------------------------------------------
  **Area**                            **Required fields / behavior**
  ----------------------------------- -----------------------------------
  Identity                            Contact name, email,
                                      company/label/agency, optional
                                      phone; capture source URL/referral
                                      token if used.

  Release content                     Headline; pasted release text; OR
                                      DOCX/PDF; OR structured fact fields
                                      sufficient to generate a canonical
                                      release.

  Structured facts                    Artist/entity; announcement type;
                                      genre/category; location;
                                      announcement date; event/release
                                      date; embargo date/time; quotes;
                                      optional editor note.

  Media                               JPG/JPEG, PNG, WEBP initially;
                                      photo caption, photographer/credit,
                                      copyright owner/rights status per
                                      image.

  Documents                           DOCX and text-based PDF initially.
                                      Flag scanned/image-only PDF for
                                      manual handling in v0.1 rather than
                                      expensive OCR.

  Links                               Official site/source URL, press
                                      kit, tickets, YouTube, Spotify,
                                      Vimeo, SoundCloud, Bandcamp, social
                                      profile URLs/handles.

  Rights                              Mandatory representation that
                                      submitter owns the media rights or
                                      is authorized by the rights holder
                                      to provide media for editorial use.

  Confirmation                        Submission ID; receipt message; no
                                      guarantee of publication;
                                      duplicate-submission warning.

  Live-post notification              On publish, email the submitter the
                                      final headline, live URL and
                                      configured social-share links. Log
                                      notification status separately.
  -----------------------------------------------------------------------

## File limits

**Recommended v0.1 defaults:** 10 MB per document; 10 MB per image; 30
MB total submission. Permit configuration at the publisher level later.
Keep an allowlist rather than a denylist, verify MIME/type server-side,
sanitize names, and never execute or directly serve untrusted uploads
from an executable path.

**Source:** [[WordPress
wp_check_filetype_and_ext()]{.underline}](https://developer.wordpress.org/reference/functions/wp_check_filetype_and_ext/)
--- WordPress provides real-file-type checks, although validation
behavior varies by type.

**Source:** [[OWASP File Upload Cheat
Sheet]{.underline}](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
--- Use allowlisted extensions, type/signature checks, size limits,
randomized storage names and malware scanning where feasible.

## Media and embedding

> **•** Extract URLs from pasted text and parsed DOCX/PDF content.
>
> **•** Normalize supported media into typed assets: youtube, spotify,
> vimeo, soundcloud, bandcamp, social, source_url, press_kit,
> ticket_url.
>
> **•** Auto-embed only trusted provider URLs. Never accept arbitrary
> iframe/embed HTML from submitters.
>
> **•** For Buddy, recommended default: auto-insert the first valid
> official YouTube URL into the generated draft; make Spotify and other
> embeds editor-toggleable.

**Source:** [[WordPress sanctioned oEmbed
providers]{.underline}](https://developer.wordpress.org/reference/hooks/oembed_providers/)
--- WordPress supports trusted providers including YouTube, Vimeo,
SoundCloud and Spotify.

## Rights & provenance

> **•** Every uploaded image gets its own asset record, credit, rights
> status and usage note.
>
> **•** Store rights attestation version, submitting email/user
> identity, timestamp and submission ID.
>
> **•** Keep original files and original submission text immutable;
> generated drafts are separate versioned editorial artifacts.
>
> **•** If rights confirmation is missing or inconsistent, mark the
> asset \'Do not publish\' even if the text submission is accepted.

**Legal note:** The final rights language, terms of submission, privacy
policy and network-distribution terms should be reviewed by counsel
before commercial rollout.

# WordPress plugin architecture

## Recommended stack

  -----------------------------------------------------------------------
  **Layer**               **Recommendation**      **Why**
  ----------------------- ----------------------- -----------------------
  Plugin backend          PHP 8.1+ / WordPress    Native compatibility
                          Plugin APIs             and distribution.

  Admin UI                React using WordPress   Queue, previews and
                          packages/components     actions benefit from
                                                  app-like UI.

  Local storage           Custom post type for    CPT keeps WordPress
                          submissions/drafts +    visibility;
                          dedicated custom tables event/history tables
                          for high-volume         avoid bloating
                          events/usage mappings   postmeta.

  Publishing              Native                  Published content
                          posts/media/block       remains ordinary
                          editor APIs             WordPress content.

  Hub communication       Custom REST client      Keeps model keys out of
                          using                   WordPress.
                          wp_remote_request;      
                          signed site credentials 

  Async UI                REST endpoints +        Simple and reliable for
                          polling initially;      v0.1.
                          webhooks/server push    
                          later                   
  -----------------------------------------------------------------------

**Source:** [[WordPress Custom Post
Types]{.underline}](https://developer.wordpress.org/plugins/post-types/registering-custom-post-types/)
--- WordPress recommends custom content types live in plugins.

**Source:** [[WordPress REST
API]{.underline}](https://developer.wordpress.org/rest-api/) ---
Designed for custom admin experiences and external applications.

**Source:** [[REST route
permissions]{.underline}](https://developer.wordpress.org/reference/functions/register_rest_route/)
--- Custom REST routes require explicit permission callbacks.

## Suggested local entities

> **• smashfire_pr_submission --- source package and local editorial
> state.**
>
> **• smashfire_pr_draft_version --- preferably Hub-owned canonical
> version record, mirrored locally as needed.**
>
> **• smashfire_pr_sender --- lightweight local sender status/cache; Hub
> becomes authoritative when network launches.**
>
> **• smashfire_pr_asset --- media/links/rights metadata; can be custom
> table or structured JSON referenced by submission.**
>
> **• smashfire_pr_event --- audit trail: received, opened, rejected,
> generated, rewritten, edited, approved, published.**

## Admin screens

  -----------------------------------------------------------------------
  **Screen**                          **Purpose**
  ----------------------------------- -----------------------------------
  Smashfire PR → Incoming             Headline/pre-writer queue; bulk
                                      select for Generate Draft / Reject
                                      / Archive.

  Smashfire PR → Drafts               Finished drafts; preview pane;
                                      rewrite with notes; bulk
                                      publish/schedule.

  Smashfire PR → Published            Items published through Smashfire
                                      PR; provenance and campaign/source
                                      visibility.

  Smashfire PR → Senders              Sender history,
                                      trusted/watch/blocked controls;
                                      later synchronized with Hub
                                      reputation.

  Smashfire PR → Settings             Publisher voice, AI mode,
                                      auto-embed preferences, file
                                      limits, Hub connection/usage.
  -----------------------------------------------------------------------

# Hub architecture

The Hub is an independently deployed, multi-tenant control plane and the
canonical backend for Smashfire PR. It is not a Buddy Magazine service.
It owns tenant/publisher identity, submissions, canonical releases, AI
prompts/model routing, assets/provenance, sender identity/reputation,
quotas, usage/cost accounting, billing, distribution and audit history.
Buddy connects to this Hub exactly as future publishers will.

## Recommended Hub stack

  -----------------------------------------------------------------------
  **Component**           **Recommended choice**  **Prototype / scale
                                                  notes**
  ----------------------- ----------------------- -----------------------
  API/application         Python FastAPI OR       Python is especially
                          TypeScript              convenient for PDF/DOCX
                          Fastify/NestJS          parsing and AI SDKs;
                                                  keep a modular
                                                  monolith.

  Database                PostgreSQL --- Supabase Both give managed
                          Pro or Neon Launch      Postgres; Supabase adds
                                                  auth/storage
                                                  conveniences, Neon is
                                                  lean usage-based
                                                  Postgres.

  Queue                   Upstash Redis + worker  Use a queue for AI
                          queue, or Cloudflare    work; don\'t block
                          Queues                  WordPress requests
                                                  while a model runs.

  Workers                 Railway/Render          Needed for robust
                          container worker        document parsing,
                                                  optional ClamAV
                                                  scanning and
                                                  long-running jobs.

  Object storage          Cloudflare R2           Cheap storage and no
                                                  egress fee; suitable
                                                  for release assets and
                                                  originals.

  Edge/bot protection     Cloudflare Turnstile +  Turnstile is free for
                          optional Workers        most use; server-side
                          endpoint                validation is
                                                  mandatory.

  Transactional email     Resend initially; SES   Resend is fast to
                          later for very high     integrate; SES is
                          volume                  cheaper at scale.

  Payments                Stripe Checkout +       Central
                          Billing                 subscriptions/top-ups
                                                  and future usage tiers.

  Observability           Sentry + structured     Track job failures,
                          logs; provider          cost anomalies,
                          dashboards initially    latency, auth abuse.
  -----------------------------------------------------------------------

**Source:** [[Supabase
pricing]{.underline}](https://supabase.com/pricing) --- Pro starts at
\$25/month; free tier is suitable for experimentation.

**Source:** [[Neon pricing]{.underline}](https://neon.com/pricing) ---
Launch is usage-based with a typical intermittent-load example around
\$15/month.

**Source:** [[Railway pricing]{.underline}](https://railway.com/pricing)
--- Hobby \$5 minimum; Pro \$20 minimum plus usage.

**Source:** [[Cloudflare R2
pricing]{.underline}](https://developers.cloudflare.com/r2/pricing/) ---
\$0.015/GB-month standard storage with no egress bandwidth charge.

**Source:** [[Upstash Redis
pricing]{.underline}](https://upstash.com/pricing/redis) --- Free
prototype tier; PAYG \$0.20 per 100K commands.

**Source:** [[Cloudflare Queues
pricing]{.underline}](https://developers.cloudflare.com/queues/platform/pricing/)
--- 1M operations/month included on Workers Paid, then \$0.40/million.

**Source:** [[Cloudflare Turnstile
plans]{.underline}](https://developers.cloudflare.com/turnstile/plans/)
--- Free plan supports unlimited challenges with plan-level
widget/hostname limits.

## Hub request flow

> **1.** Plugin authenticates to Hub using a per-installation
> credential; no LLM provider credential is ever returned to WordPress.
>
> **2.** Hub authorizes publisher, installation, user/action and
> submission ownership.
>
> **3.** Usage service checks monthly/daily/hourly/action caps plus a
> hard account dollar ceiling.
>
> **4.** Submission service retrieves canonical source and assets.
>
> **5.** Prompt service combines locked system rules, publisher voice
> and optional editor rewrite notes.
>
> **6.** AI router selects the cheapest approved model for the
> action/tier and can fail over to another provider.
>
> **7.** Job runs through a queue worker; malformed/empty/oversized
> outputs are rejected or retried under strict retry caps.
>
> **8.** Usage ledger records input/output tokens, provider/model,
> duration, cost, status and draft version.
>
> **9.** Result is stored as a new version and returned to the plugin;
> WordPress renders preview or publishes a normal post.

## Why the queue matters

> **•** Protects WordPress from model latency and provider outages.
>
> **•** Allows retries, dead-letter handling and rate-limit backoff
> without duplicate drafts.
>
> **•** Enables priority: editor-waiting jobs \> selected drafts \>
> background extraction/classification \> batch jobs.
>
> **•** Provides a natural place to enforce per-publisher concurrency
> caps.

# AI pipeline and model routing

![Smashfire PR workflow
flowchart](/home/claude/smashfire-pr/docs/media/media/image2.png){width="6.8in"
height="1.0817727471566054in"}

*Conceptual workflow diagram*

## Actions should be constrained

**Never expose a generic \'prompt\' API to the plugin.** Expose
operations such as analyze_submission, generate_canonical_release,
generate_publisher_draft, rewrite_draft, generate_headlines and
classify_relevance. The Hub owns prompt construction so a stolen site
credential cannot become a free general-purpose LLM proxy.

## Recommended processing stages

  -----------------------------------------------------------------------------------
  **Stage**               **Output**                          **Model class**
  ----------------------- ----------------------------------- -----------------------
  Normalize/extract       Clean text, entities, dates,        Low-cost
                          quotes, URLs, media candidates      structured-output model

  Safety/relevance        Spam/off-topic/relevance/category   Low-cost model +
                          scores                              deterministic rules

  Canonical release       Only when input is structured       Low-cost writing model
  generation              facts/incomplete source             

  Publisher draft         Headline, lede, body, tags, media   Primary writing model
                          suggestions                         

  Rewrite with notes      New version using source +          Primary writing model;
                          publisher voice + editor notes      premium model optional

  Premium escalation      Difficult/long/important copy       Higher-quality model by
                                                              plan/action
  -----------------------------------------------------------------------------------

## Current API economics

  ------------------------------------------------------------------------
  **Model**               **Current text pricing  Best Smashfire PR role
                          per 1M tokens**         
  ----------------------- ----------------------- ------------------------
  DeepSeek V4 Flash       Off-peak \$0.22 input / Very low-cost drafting,
                          \$0.66 output; peak     extraction,
                          \$0.44 / \$1.32         classification; schedule
                                                  background jobs off-peak
                                                  where practical.

  OpenAI GPT-5.6 Luna     \$0.20 input / \$1.20   Strong cost-sensitive
                          output                  fallback/primary
                                                  candidate; benchmark
                                                  against DeepSeek for
                                                  Buddy voice.

  OpenAI GPT-5.6 Terra    \$2 input / \$12 output Premium
                                                  rewrite/escalation tier.

  Gemini 2.5 Flash-Lite   \$0.10 input / \$0.40   Cheap
                          output                  structured/extraction
                                                  tasks; confirm model
                                                  stability/availability
                                                  before production
                                                  dependency.
  ------------------------------------------------------------------------

**Source:** [[DeepSeek Models &
Pricing]{.underline}](https://api-docs.deepseek.com/quick_start/pricing/?article_id=article_1779470751466_8)
--- Peak/off-peak V4 pricing effective August 2026; pricing can change.

**Source:** [[OpenAI GPT-5.6
Luna]{.underline}](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
--- \$0.20/M input, \$1.20/M output.

**Source:** [[OpenAI GPT-5.6
Terra]{.underline}](https://developers.openai.com/api/docs/models/gpt-5.6-terra)
--- \$2/M input, \$12/M output.

**Source:** [[Google Gemini API
pricing]{.underline}](https://ai.google.dev/gemini-api/docs/pricing) ---
Current Flash/Flash-Lite pricing and availability.

## Working unit-cost assumption

**For budgeting, assume one completed draft consumes \~7,875 input
tokens and \~2,000 output tokens** across extraction/classification +
draft generation + a 25% probability of one rewrite. This is
intentionally more conservative than a single one-shot article request.

  --------------------------------------------------------------------------
  **Model        **Approx. AI   **20 drafts**  **150 drafts** **500 drafts**
  route**        cost /                                       
                 completed                                    
                 draft**                                      
  -------------- -------------- -------------- -------------- --------------
  DeepSeek V4    \$0.0061       \$0.12         \$0.92         \$3.05
  Flash --- peak                                              

  DeepSeek V4    \$0.0031       \$0.06         \$0.46         \$1.53
  Flash ---                                                   
  off-peak                                                    

  OpenAI GPT-5.6 \$0.0040       \$0.08         \$0.60         \$1.99
  Luna                                                        

  Gemini 2.5     \$0.0016       \$0.03         \$0.24         \$0.79
  Flash-Lite                                                  
  --------------------------------------------------------------------------

**Interpretation:** AI cost is unlikely to be the primary cost driver at
publisher volumes of tens or hundreds of drafts per month. Benchmark
quality before selecting the cheapest model.

# Publisher voice & rewrite versioning

> **•** Publisher profile is persistent: AP/news style, tone, preferred
> length, headline rules, geography/genre emphasis, prohibited
> promotional language, SEO/tag rules, embed preferences.
>
> **•** Editor Rewrite action adds one-time instructions to the
> persistent profile and immutable source release.
>
> **•** Never overwrite: Original → Draft V1 → Draft V2 → Draft V3 →
> Published Version.
>
> **•** Track model, prompt-template version and editor instructions for
> each generation.
>
> **•** Later: detect repeated editor instructions and suggest --- never
> silently apply --- a Publisher Voice update.

# Security, abuse prevention & quotas

![Smashfire PR workflow
flowchart](/home/claude/smashfire-pr/docs/media/media/image3.png){width="6.8in"
height="3.3919531933508313in"}

*Conceptual workflow diagram*

## Public Buddy form

> **•** noindex/no-follow and unlisted distribution are discoverability
> controls, not security controls.
>
> **•** Use Cloudflare Turnstile and validate every token server-side;
> tokens are short-lived and single-use.
>
> **•** Honeypot + IP/email rate limits + request-size limits +
> duplicate fingerprinting.
>
> **•** Reject unsupported extensions/MIME types; randomize storage
> names; keep uploads outside executable web paths.
>
> **•** Optional next step: antivirus scan in a container worker before
> files are made available to editors.

**Source:** [[Cloudflare Turnstile server-side
validation]{.underline}](https://developers.cloudflare.com/turnstile/get-started/server-side-validation/)
--- Client-side widgets alone are not sufficient; server verification is
mandatory.

## Hub credential separation

  -----------------------------------------------------------------------
  **Credential**          **Purpose**             **If compromised**
  ----------------------- ----------------------- -----------------------
  PR sender credential    Submit authenticated    Revoke one sender/org;
  (future)                releases                no LLM access.

  Publisher account       Plan/network identity   Suspend account; does
                                                  not expose provider
                                                  key.

  WP installation secret  Plugin ↔ Hub requests   Rotate per site; scope
                                                  to defined Smashfire PR
                                                  actions.

  Editor session/nonce    Local admin actions     WordPress capability
                                                  boundary.

  LLM provider secret     Hub → model provider    Never shipped to
                          only                    plugins; rotate
                                                  centrally.
  -----------------------------------------------------------------------

## Quota controls

> **•** Monthly draft allowance per publisher.
>
> **•** Daily generation cap; hourly burst cap; concurrent-job cap.
>
> **•** Maximum source/input bytes and maximum output tokens.
>
> **•** Rewrite count cap per submission.
>
> **•** Action-specific limits: classification can be generous; full
> generation is metered tightly.
>
> **•** Hard account spend ceiling in dollars in addition to product
> quotas.
>
> **•** Global provider/day spend ceiling and emergency kill switch.
>
> **•** When a publisher reaches quota, intake and Pre-Writer queue
> continue; only full generation is paused.

# Billing and packaging

**Sell completed-draft capacity, not LLM tokens.** Tokens are an
internal cost metric; publishers understand drafts/rewrites. Keep the
publisher-facing product useful after quota exhaustion by continuing
intake and headline triage.

  -------------------------------------------------------------------------
  **Illustrative    **Monthly price   **Included full   **Notes**
  plan**            idea**            drafts**          
  ----------------- ----------------- ----------------- -------------------
  Network / Starter \$0               20                Free while building
                                                        network; editor
                                                        queue and basic
                                                        submission form.

  Publisher         \$19              150               Custom publisher
                                                        voice, rewrite
                                                        notes/versioning,
                                                        scheduling, email
                                                        intake when
                                                        available.

  Publisher Pro     \$39--\$49        500               Advanced
                                                        automation, team
                                                        controls,
                                                        analytics, priority
                                                        model access.

  Agency /          Custom            Pooled            Multiple publisher
  Multi-site                                            sites; centralized
                                                        reporting and quota
                                                        pools.
  -------------------------------------------------------------------------

**Pricing is intentionally illustrative.** Use Buddy and the first 3--5
external sites to establish real generation rate, support burden and
willingness to pay before locking tiers.

## Stripe economics

  -----------------------------------------------------------------------
  **Charge**              **Card + Billing        **Approx. %**
                          estimate\***            
  ----------------------- ----------------------- -----------------------
  \$9                     \$0.62                  6.9%

  \$19                    \$0.98                  5.2%

  \$29                    \$1.34                  4.6%

  \$49                    \$2.06                  4.2%

  \$99                    \$3.86                  3.9%
  -----------------------------------------------------------------------

*\*Assumes standard U.S. card processing at 2.9% + \$0.30 plus Stripe
Billing pay-as-you-go at 0.7% of Billing volume; excludes taxes,
international/currency fees and other products.*

**Source:** [[Stripe standard payment
pricing]{.underline}](https://stripe.com/pricing) --- 2.9% + \$0.30 for
domestic cards.

**Source:** [[Stripe Billing
pricing]{.underline}](https://stripe.com/billing/pricing) ---
Pay-as-you-go Billing is 0.7% of Billing volume.

> **•** Avoid tiny \$2--\$5 top-ups because the fixed \$0.30 transaction
> fee becomes inefficient.
>
> **•** If selling top-ups, package them as meaningful draft bundles
> (for example 100 or 250 drafts).
>
> **•** Keep Stripe customer/subscription state in the Hub; the plugin
> only displays plan and usage.

# Submitter live-post alerts & social sharing

When a Smashfire PR-originated story is published, the system should
automatically notify the original submitter that the story is live. The
notification should include the final headline, publication name, live
URL, publication timestamp, and configurable social-sharing
buttons/links so the submitter can amplify the pickup immediately.

• Trigger: a WordPress post linked to a Smashfire PR submission
transitions to published status, whether published immediately or by
schedule.

• Recipient: the captured submission contact email in v0.1; later,
authorized PR users attached to the submission or campaign according to
notification preferences.

• Email content: publisher name/logo, final published headline, live
URL, short confirmation message, publication date/time, and optional
featured-image thumbnail.

• Social sharing actions: configurable URL-based share buttons/links for
Facebook, X, LinkedIn, Bluesky and email; \'View live story\' is the
primary CTA.

• Tracking: record notification queued, sent, delivered/bounced where
available, and social-share link clicks when routed through Smashfire PR
tracking URLs.

• Failure handling: notification failure must never affect publication.
Failed messages enter a retry queue and appear in the Hub/admin event
log.

• Publisher control: enable/disable alerts, customize sender
name/reply-to, choose enabled social networks, and edit the default
notification template.

• Network future state: a campaign dashboard aggregates all live pickups
and gives the PR sender a running list of publisher URLs with
per-placement sharing controls.

# Future email intake

![Smashfire PR workflow
flowchart](/home/claude/smashfire-pr/docs/media/media/image4.png){width="6.8in"
height="0.9974956255468066in"}

*Conceptual workflow diagram*

**Add only after web-form workflow is validated. The Hub should support
centrally managed intake aliases and/or connections to existing
publisher mailboxes. A public Buddy editor address can be monitored or
forwarded, with authenticated sender keys and reputation checks deciding
which messages are promoted into Smashfire PR.**

> **•** Do not require each publisher to create a vanity mailbox.
>
> **•** Offer: Google/Microsoft connection, forwarding alias, advanced
> IMAP fallback, and the private upload portal.
>
> **•** Email, web form and future API/network delivery must all
> normalize into the same Submission object.

## Smashfire-managed publisher intake addresses

The preferred scalable email option is for Smashfire PR to issue each
participating publisher a unique inbound address on a
Smashfire-controlled domain. The publisher gives that address directly
to selected publicists, labels, artists and PR contacts. The address is
a routing alias, not a conventional mailbox: inbound email is parsed by
the Smashfire PR Hub and converted into the same canonical Submission
object used by the web form.

• Example: buddy-k7x4@inbound.smashfirepr.com. The non-guessable suffix
reduces unsolicited discovery and identifies the destination publisher
before content processing begins.

• No publisher mail-server setup is required. The publisher does not
need to create a vanity mailbox, change MX records, share IMAP
credentials or maintain a separate hosted inbox.

• The publisher onboarding screen should display the assigned intake
address with Copy Address, Rotate Address, Pause Email Intake and View
Recent Email Activity controls.

• The Hub maps each active alias to publisher_id/tenant_id, validates
the inbound provider webhook, parses MIME/body/attachments, extracts
URLs/media, runs sender/reputation/spam checks, and creates the
publisher delivery/submission.

• Aliases must be rotatable. If an address leaks or attracts excessive
spam, issue a new alias, place the old alias into a configurable grace
period, then retire it without changing the publisher\'s WordPress
installation.

• Support multiple aliases per publisher later for categories, desks or
campaigns, but keep one primary intake alias per publisher in the
initial email release.

• A publisher may still use its existing public editorial address and
create a forwarding rule to the Smashfire-managed alias. This allows
either model: give publicists the Smashfire address directly, or keep
the publisher\'s existing address as the public-facing entry point.

• Future authenticated sender keys can be included in
subject/body/headers in addition to the publisher alias. Alias
identifies destination; sender credential identifies
authorization/reputation.

• Email delivery is transport only. It must normalize into the same
Submission/Asset/Rights/Delivery schema as the web portal so the editor
workflow is identical regardless of intake channel.

## Recommended email intake options by priority

1\. Smashfire-managed inbound alias --- default network option and
lowest-friction publisher onboarding.

2\. Existing publisher mailbox → forwarding rule → Smashfire alias ---
preserves the publisher\'s established public email address.

3\. Google Workspace / Microsoft 365 OAuth connector --- future
convenience/premium option for publishers that want Smashfire to watch a
dedicated folder/mailbox.

4\. IMAP connection --- advanced fallback for unusual mail hosts; avoid
making this the default because of credential and support complexity.

5\. Web submission portal --- remains available alongside email and is
the v0.1 intake method.

# Future sender reputation

> **•** Statuses: Trusted, Normal, Watch, Restricted, Suspended, Banned.
>
> **•** Signals: verified identity/domain, accepted/published rate,
> off-topic frequency, spam flags, excessive frequency, invalid
> credentials, duplicate patterns.
>
> **•** Off-topic legitimate submissions receive a theme reminder;
> obvious spam should generally not receive autoresponses.
>
> **•** Credential/key rotation and disposable intake aliases can be
> added once email/network intake is active.

# Future Smashfire PR Wire / distribution hub

![Smashfire PR workflow
flowchart](/home/claude/smashfire-pr/docs/media/media/image5.png){width="6.8in"
height="1.7178433945756781in"}

*Conceptual workflow diagram*

**One canonical release; many WordPress dashboard deliveries.** The
customer pays for targeted distribution to relevant publishers, not
guaranteed coverage. Publishers retain editorial choice.

## Network objects

> **•** Canonical Release --- immutable source package.
>
> **•** Distribution Campaign --- category/geography/tier/target rules
> purchased by sender.
>
> **•** Delivery --- release X offered to publisher Y.
>
> **•** Publisher Match --- relevance and eligibility score.
>
> **•** Editorial State --- delivered, notified, viewed, selected, draft
> generated, rejected, published.
>
> **•** Publisher Draft Version --- publication-specific editorial
> treatment derived from the canonical release.

## Network workflow

> **1.** PR sender submits canonical package and purchases/chooses a
> category network campaign.
>
> **2.** Distribution engine filters by publisher opt-in profile,
> category, geography, exclusions, sender status and campaign rules.
>
> **3.** Release appears inside qualified WordPress dashboards.
>
> **4. Publisher receives immediate or digest notification; notification
> points to Smashfire PR rather than attaching the entire release.**
>
> **5.** Publisher selects the release; only then does the Hub normally
> incur a full draft-generation cost.
>
> **6.** Publisher-specific voice/profile produces a distinct editorial
> draft; editor reviews and publishes or rejects.
>
> **7.** Campaign reporting shows delivery, views, selection, drafts and
> pickups without presenting paid distribution as guaranteed editorial
> placement.

# Future paid-pickup marketplace

![Smashfire PR workflow
flowchart](/home/claude/smashfire-pr/docs/media/media/image6.png){width="6.8in"
height="1.028607830271216in"}

*Conceptual workflow diagram*

A later Smashfire PR revenue model can add an optional
publisher-incentive marketplace. A buyer funds a distribution campaign
and sets a maximum campaign budget and/or per-pickup economics. Eligible
publishers can see a specific payout attached to a release --- for
example, "Publish this release and receive \$5.33." The buyer is charged
only when a qualifying publication event is verified, Smashfire PR
retains its platform percentage, and the remaining amount is credited to
the publisher.

• This must be a separate campaign type from ordinary earned-media
distribution. A publisher\'s acceptance of a paid pickup is a
compensated placement and should be handled under the publisher\'s
advertising/sponsored-content policy and applicable disclosure
requirements.

• The buyer-facing campaign can be funded from a deposit/preauthorized
payment method or campaign wallet. Internally, Smashfire PR maintains a
hidden gross pickup price and platform fee calculation; the publisher
sees only the payout offered to that publisher unless product policy
calls for greater transparency.

• Example economics: buyer gross pickup price \$8.00; Smashfire PR
platform share 33.375% (\$2.67); publisher payout \$5.33. Percentages
and payout floors/ceilings should be configurable by campaign, publisher
tier and category.

• The buyer pays for verified pickup/publish rather than merely for
delivery to a dashboard. Distribution, impressions in the queue and
editor views do not by themselves trigger the pickup charge unless a
campaign is explicitly priced that way.

• A qualifying pickup should require a unique Smashfire PR delivery
record, an approved publisher, a live public URL, matching
publication/submission IDs, and a minimum live period or verification
window before payout becomes withdrawable.

• The system should prevent self-dealing, duplicate payouts, rapid
publish/delete behavior, duplicate-domain claims, bot-created publisher
sites and other incentive fraud. Suspicious payouts should enter review
rather than settle automatically.

• Publisher onboarding for incentives requires payout information and
tax/KYC information as required by the payment provider and
jurisdiction. Smashfire PR should avoid storing raw bank/card details
itself and use a marketplace payout provider such as Stripe Connect.

• Publisher dashboard fields: eligible payout, disclosure
requirement/status, payout pending, payout available, payout paid, and
any verification hold. Publisher can opt out of paid releases entirely
or set minimum payout/category rules.

• Buyer campaign fields: campaign budget, maximum paid pickups, eligible
categories/geographies, gross pickup price or pricing rule, platform
percentage, publisher payout pool, remaining budget, verified pickups
and spend.

• When the budget/pickup cap is exhausted, the paid incentive disappears
automatically. The underlying release may remain available for ordinary
unpaid editorial consideration if the publisher/network rules permit.

• The live-post alert to the submitter should distinguish paid pickup
from organic pickup in campaign reporting so the buyer can see exactly
which placements were compensated and which were earned.

• For SEO integrity, compensated articles/links should follow current
search-engine guidance for paid placements, including appropriate
sponsored link attributes where applicable; the product should not
market paid pickups as a mechanism for buying undisclosed editorial
links.

## Illustrative payout ledger

![Smashfire PR workflow
flowchart](/home/claude/smashfire-pr/docs/media/media/image7.png){width="6.8in"
height="0.7360728346456693in"}

*Conceptual workflow diagram*

  -----------------------------------------------------------------------
  Field                               Purpose
  ----------------------------------- -----------------------------------
  campaign_id                         Identifies the paid distribution
                                      campaign.

  delivery_id                         Ties the payout to one release →
                                      publisher delivery.

  gross_pickup_price                  Amount charged/allocated to buyer
                                      for a verified pickup.

  platform_fee                        Smashfire PR revenue retained from
                                      the pickup.

  publisher_payout                    Amount displayed/owed to publisher,
                                      e.g. \$5.33.

  verification_status                 pending → verified → hold/review →
                                      payable → paid/reversed.

  live_url                            Verified public publication URL.

  published_at / verified_at          Timing used for verification and
                                      payout hold.

  payout_account_id                   Payment-provider connected account
                                      reference; not raw bank data.
  -----------------------------------------------------------------------

# Data model --- Hub

  ---------------------------------------------------------------------------
  **Entity**                          **Key fields**
  ----------------------------------- ---------------------------------------
  organizations                       type (publisher/PR/label), status,
                                      billing customer, reputation

  users                               organization, role, email verification,
                                      status

  publishers                          name, site, network status,
                                      category/geography profile

  publisher_installations             site_id, site_url, credential hash,
                                      last_seen, plugin version

  publisher_profiles                  voice prompt settings, categories,
                                      embeds, automation rules

  submissions                         canonical text, source type, sender,
                                      dates, topic/relevance, status

  assets                              submission, type, storage key, MIME,
                                      credit, rights status, extracted URL

  deliveries                          submission/campaign → publisher,
                                      status, scores, timestamps

  draft_versions                      delivery/submission, model, prompt
                                      version, instructions, content, version

  ai_jobs                             action, provider/model, state,
                                      retry_count, latency

  ai_usage                            tokens, estimated/actual cost,
                                      publisher/user/submission/action

  plans/quotas                        allowances, caps, overage behavior,
                                      dollar ceiling

  events                              append-only editorial/distribution
                                      audit trail

  payments                            Stripe customer/subscription/payment
                                      refs; do not store raw card data

  reputation_events                   sender/publisher abuse and quality
                                      signals

  publication_notifications           submission/delivery, publisher,
                                      recipient, live_post_url, final
                                      headline, template version,
                                      queued/sent/delivered/bounced/clicked
                                      timestamps, retry_count

  paid_campaigns                      buyer, release, budget, gross pickup
                                      price/rule, platform fee %, pickup cap,
                                      eligibility, disclosure policy, status

  publisher_payout_accounts           publisher, payment-provider
                                      connected-account ID, onboarding/KYC
                                      status, payout eligibility

  pickup_incentives                   delivery/publisher, displayed payout,
                                      gross price, platform fee, expiration,
                                      acceptance state

  pickup_verifications                delivery, live URL, publish timestamp,
                                      verification checks, hold/review state,
                                      reversal reason

  payout_ledger                       campaign, delivery, buyer charge,
                                      Smashfire PR fee, publisher payable,
                                      provider transaction refs, status

  publisher_intake_aliases            publisher/tenant, alias/local-part,
                                      inbound domain, status, created_at,
                                      grace_until, retired_at, category/desk
                                      optional

  inbound_messages                    provider message ID, recipient alias,
                                      sender, subject, raw-message storage
                                      key, parse status, spam/reputation
                                      signals, submission ID
  ---------------------------------------------------------------------------

# API surface --- recommended

  ------------------------------------------------------------------------------------
  **Endpoint family**     **Examples**                         **Notes**
  ----------------------- ------------------------------------ -----------------------
  Plugin registration     POST /v1/installations/register;     Per-installation
                          rotate                               credentials; never
                                                               expose LLM secrets.

  Submission              POST /v1/submissions; GET /{id};     Idempotency keys
                          assets                               required.

  Generation              POST /v1/submissions/{id}/draft;     Controlled action enum,
                          /rewrite                             not arbitrary prompt.

  Jobs                    GET /v1/jobs/{id}                    Plugin polls initially;
                                                               webhook later.

  Usage                   GET /v1/usage                        Current plan, drafts
                                                               remaining, spend/caps.

  Publisher profile       GET/PUT /v1/publishers/{id}/profile  Authorized admin only.

  Network                 POST campaign; list deliveries       Future state.

  Webhook to WP           POST                                 Signed timestamp +
                          /wp-json/smashfire-pr/v1/hub-event   nonce/HMAC; narrow
                                                               permissions.
  ------------------------------------------------------------------------------------

# Cost model

**Important: these are infrastructure estimates, not labor or
development budgets.** They assume a lean managed stack, modest media
retention and the conservative AI token model above. Costs can vary
materially with asset sizes, support requirements, backups, logging,
malware scanning and model choice.

## Per-publisher variable AI cost

  -----------------------------------------------------------------------
  **Publisher       **Full drafts /   **Approx.         **Approx. GPT-5.6
  usage**           month**           DeepSeek peak     Luna AI**
                                      AI**              
  ----------------- ----------------- ----------------- -----------------
  Low               20                \$0.12            \$0.08

  Medium            150               \$0.92            \$0.60

  High              500               \$3.05            \$1.99
  -----------------------------------------------------------------------

## Per-publicist / campaign-side variable cost

**Illustrative assumptions:** the canonical release is normalized once;
distribution itself is database/email work; full AI drafts are generated
only for publishers that select/qualify for them.

  -----------------------------------------------------------------------------
  **Publicist    **Releases/mo**   **Avg target   **10% generate **Approx.
  use**                            publishers**   drafts**       DeepSeek peak
                                                                 AI\***
  -------------- ----------------- -------------- -------------- --------------
  Low            5                 25             13             \~\$0.08

  Medium         20                75             150            \~\$0.92

  High           100               150            1,500          \~\$9.16
  -----------------------------------------------------------------------------

\*Draft-generation estimate only, excluding a small canonical extraction
cost and notification email. At current pricing those ancillary AI/email
costs are minor relative to the retail value of a paid distribution
campaign.

## Whole-network operating scenarios

  ----------------------------------------------------------------------------------------------
  **Scenario**      **Workload assumption**   **Likely monthly      **What drives it**
                                              service cost range**  
  ----------------- ------------------------- --------------------- ----------------------------
  Pilot             1--10 publishers; \~200   \~\$20--\$75          Small Hub compute/DB,
                    drafts; \<1,000                                 optional paid email,
                    submissions; \<20 GB                            negligible AI/storage.
                    assets                                          

  Early network     50--100 publishers;       \~\$100--\$350        Production DB/worker, email
                    \~10,000 drafts; 25k--50k                       plan, logs/monitoring; AI
                    submissions/deliveries;                         roughly tens of dollars.
                    100--300 GB assets                              

  Growth            \~500 publishers;         \~\$750--\$1,800      AI hundreds/month, resilient
                    \~100,000 drafts; large                         compute/workers, email
                    distribution activity;                          volume,
                    \~1 TB assets                                   monitoring/backups/support
                                                                    tooling.

  Large network     1,000+ publishers; 250k+  \~\$2,000--\$6,000+   Model mix, HA/observability,
                    drafts; multi-million                           staff/support, email
                    events/deliveries                               reputation, scanning and
                                                                    retention dominate.
  ----------------------------------------------------------------------------------------------

**These are planning ranges rather than vendor quotes.** The low-end
assumes aggressive use of managed/free allowances; the upper end assumes
production redundancy and more logging/support. Labor, legal, insurance,
development and sales are excluded.

## Reference infrastructure prices

  -----------------------------------------------------------------------
  **Service**                         **Current reference price**
  ----------------------------------- -----------------------------------
  Cloudflare Workers Paid             \$5/month includes 10M
                                      requests/month and 30M CPU ms;
                                      overage per published rates.

  Cloudflare R2                       \$0.015/GB-month standard storage;
                                      no egress bandwidth fee.

  Cloudflare Queues                   1M operations/month included with
                                      Workers Paid; \$0.40/million
                                      beyond.

  Upstash Redis                       Free prototype tier; PAYG
                                      \$0.20/100K commands.

  Supabase Pro                        From \$25/month.

  Neon Launch                         Usage based; provider example says
                                      typical intermittent 1 GB workload
                                      \~ \$15/month.

  Railway                             Hobby \$5 minimum; Pro \$20 minimum
                                      plus resource usage.

  Resend                              Free 3,000 emails/month; Pro \$20
                                      for 50,000; Scale \$90 for 100,000.

  Amazon SES                          Essentials starts at \$0.16/1,000
                                      outbound emails in first volume
                                      tier under current plan pricing.
  -----------------------------------------------------------------------

**Source:** [[Cloudflare Workers
pricing]{.underline}](https://developers.cloudflare.com/workers/platform/pricing/)
--- Paid plan baseline and included request/CPU usage.

**Source:** [[Resend pricing]{.underline}](https://resend.com/pricing/)
--- Free/Pro/Scale email quotas.

**Source:** [[Amazon SES
pricing]{.underline}](https://aws.amazon.com/ses/pricing/) --- Current
pay-as-you-go plan pricing.

# Recommended staging roadmap

![Smashfire PR workflow
flowchart](/home/claude/smashfire-pr/docs/media/media/image8.png){width="6.8in"
height="0.6924540682414698in"}

*Conceptual workflow diagram*

  ---------------------------------------------------------------------------------
  **Stage**               **Scope**                  **Exit criteria**
  ----------------------- -------------------------- ------------------------------
  0.1 --- Buddy form      Submission page,           At least 50 real submissions;
  prototype               files/media/rights,        editor can process queue
                          normalization, Hub AI,     reliably; cost/story
                          Pre-Writer + Draft queues, measured.; submitter reliably
                          rewrite/versioning,        receives the live URL after
                          publish, usage logging;    publication
                          automatic submitter        
                          live-post email with       
                          social sharing links       

  0.2 --- Editorial       Bulk actions, scheduling,  Buddy workflow replaces
  hardening               sender management,         meaningful portion of manual
                          duplicate detection,       release handling.
                          better media handling,     
                          quarantine, analytics      

  0.3 --- Email intake    Smashfire-managed          Email and web submissions
                          per-publisher inbound      normalize to the same object;
                          aliases; optional          a new publisher can activate
                          forwarding from existing   email intake without creating
                          publisher mailboxes;       or exposing mailbox
                          MIME/attachment parsing;   credentials; aliases can be
                          sender keys/reputation;    rotated without breaking the
                          alias rotation/retirement; WordPress connection.
                          Google/Microsoft and IMAP  
                          connectors retained as     
                          future options.            

  0.4 --- Multi-site beta 3--5 music sites,          Each site produces distinct
                          publisher profiles, site   acceptable drafts; quotas
                          registration/credential    enforced centrally.
                          rotation, shared Hub       

  0.5 --- Commercial      Stripe, plan/usage UI,     Paid quota upgrade works
  publisher tier          draft packs, billing       without plugin-side secrets.
                          webhooks, support/admin    
                          console                    

  1.0 --- Music network   20--50 participating       Demonstrable
                          sites, publisher matching, delivery/view/select/publish
                          PR account model, campaign funnel.
                          delivery and reporting     

  1.x --- Paid wire       Category/niche             First repeat paying PR
                          distribution packages,     customers and defensible
                          sender billing, digests,   pickup/engagement metrics.
                          campaign analytics;        
                          automatic pickup alerts    
                          and social amplification   
                          from each live placement   

  2.0 --- Network         Reputation, routing        Network routing measurably
  intelligence            optimization,              improves relevance/acceptance
                          cross-publisher insights,  without sacrificing publisher
                          higher-volume API partners control.

  2.x --- Paid pickup     Optional                   Verified end-to-end buyer
  marketplace             compensated-release        charge → live URL verification
                          campaigns; publisher       → Smashfire PR fee → publisher
                          payout onboarding;         payout works reliably, with
                          per-release incentive      compensated placements clearly
                          offers; buyer              separated from earned pickup.
                          pay-on-verified-publish;   
                          platform commission;       
                          payout ledger; fraud       
                          controls; paid/organic     
                          reporting and disclosure   
                          controls.                  
  ---------------------------------------------------------------------------------

# Development work breakdown --- v0.1

  -----------------------------------------------------------------------
  **Workstream**                      **Key tasks**
  ----------------------------------- -----------------------------------
  Plugin shell                        Plugin bootstrap,
                                      activation/migrations,
                                      capabilities, admin menu, settings,
                                      CPT/custom tables.

  Submission UI                       Noindexed page/shortcode/block,
                                      Turnstile, validation, upload UX,
                                      confirmation/ID.

  Hub registration                    Site registration, per-installation
                                      secret, credential rotation,
                                      connectivity test.

  Submission API                      Idempotent create, upload session,
                                      canonical IDs, status lifecycle.

  Document parsing                    DOCX text/links; text PDF
                                      extraction; fail gracefully on
                                      scanned/image-only PDF.

  Asset pipeline                      R2 storage, image metadata/rights,
                                      URL normalization, oEmbed
                                      classification.

  AI pipeline                         Structured extraction, canonical
                                      generation when needed, Buddy
                                      publisher profile, draft
                                      generation, rewrite notes.

  Queue                               Pre-Writer table, Draft table,
                                      quick preview/side panel, bulk
                                      generation, statuses.

  Versioning                          V1/V2 restore/compare metadata,
                                      prompt/model provenance.

  Publishing                          Create/update normal WP post;
                                      media/embed blocks;
                                      schedule/publish; retain private
                                      source link.

  Usage                               Token/cost ledger, publisher caps,
                                      action caps, admin usage widget.

  Security                            Turnstile server validation, rate
                                      limits, MIME/type checks, upload
                                      isolation, REST permissions,
                                      logging.

  QA                                  Unit/API tests, plugin integration
                                      tests, malformed files,
                                      replay/duplicate tests, failed
                                      model/provider cases.

  Submitter notifications             Hook WordPress publish transition,
                                      queue transactional email, render
                                      final headline/live URL/featured
                                      image, add social-share links,
                                      retries, delivery logging, and
                                      publisher-level notification
                                      preferences.

  Paid pickup marketplace (future)    Marketplace payment
                                      provider/connected accounts,
                                      campaign wallet/preauthorization,
                                      incentive calculation, publisher
                                      payout UI, live URL verification,
                                      payout holds/reversals, fraud
                                      rules, disclosure flags,
                                      ledger/reconciliation.

  Managed email intake (future)       Inbound-domain/provider
                                      integration; unique per-publisher
                                      aliases; alias → tenant routing;
                                      raw MIME/attachment handling;
                                      rotation/grace/retirement;
                                      forwarding compatibility;
                                      sender-key and reputation checks;
                                      email activity/admin UI.
  -----------------------------------------------------------------------

# Acceptance criteria --- Buddy v0.1

> **•** A selected publicist can submit a valid release package without
> a WordPress login.
>
> **•** A malformed or over-limit file cannot enter the editorial queue.
>
> **•** Every accepted submission has an immutable canonical source
> record and submission ID.
>
> **•** Editor can view only headlines/source metadata without
> generating a full draft.
>
> **•** Editor can generate one or multiple selected drafts.
>
> **•** Finished draft can be previewed quickly, rewritten with custom
> notes, edited and published.
>
> **•** Rewrite never destroys previous draft versions.
>
> **•** Valid YouTube URLs can be inserted as native/sanctioned
> WordPress embeds; arbitrary iframe code is rejected.
>
> **•** Every uploaded image includes rights/credit state before it can
> be auto-selected for publication.
>
> **•** No LLM provider secret exists in plugin code or WordPress
> options.
>
> **•** Hub rejects generation after quota or dollar ceiling and intake
> continues working.
>
> **•** Every AI request is auditable by publisher, submission, action,
> model, tokens, cost and status.

• Publishing a Smashfire PR-originated post automatically queues a
submitter notification containing the final headline, live URL and
configured social-sharing links; notification failure cannot block or
roll back publication.

# Metrics to instrument from day one

  -----------------------------------------------------------------------
  **Metric family**                   **Metrics**
  ----------------------------------- -----------------------------------
  Intake                              Submissions/day, sender repeats,
                                      completion rate, file/source types,
                                      invalid/rejected uploads.

  Editorial                           Viewed %, selected-for-draft %,
                                      rejected %, publish %, median
                                      decision time.

  AI quality                          First-draft acceptance %, rewrites
                                      per draft, editor edit distance,
                                      failure/retry rate.

  Economics                           AI cost/submission, cost/draft,
                                      cost/published story, storage per
                                      submission, email cost.

  Network-ready                       Sender topicality, category match,
                                      publisher acceptance by topic,
                                      assets used.

  Product                             Weekly active editors, drafts
                                      generated/user, time saved
                                      estimates, quota exhaustion/upgrade
                                      intent.
  -----------------------------------------------------------------------

# Key design decisions to lock now

**0. Smashfire PR is a standalone multi-tenant platform from v0.1; Buddy
Magazine is Tenant #001 and the first WordPress client.**

> **1.** Hub owns LLM credentials and metering; plugin never calls
> provider directly in commercial architecture.
>
> **2.** Submission is a first-class object separate from a published
> WordPress post.
>
> **3.** Original source is immutable; AI/editorial outputs are
> versioned derivatives.
>
> **4.** Assets and rights metadata are structured records.
>
> **5.** Pre-Writer triage is allowed to avoid unnecessary generation
> cost.
>
> **6.** Rewrite accepts editor notes and creates a new version.
>
> **7.** All intake channels normalize into the same schema.
>
> **8.** Network distribution creates Delivery records rather than
> copying independent source releases.
>
> **9.** Paid distribution buys targeted delivery/editorial
> consideration, not guaranteed publication.
>
> **10.** Publisher quotas are enforced at the Hub even if a local
> plugin is modified.

# Recommended first implementation choices

  -----------------------------------------------------------------------
  **Choose now**                      **Recommendation**
  ----------------------------------- -----------------------------------
  **Plugin**                          PHP + React admin UI

  **Hub language**                    Python FastAPI for v0.1 (document
                                      parsing + AI convenience)

  **DB**                              PostgreSQL; Supabase Pro when
                                      moving beyond prototype, or Neon
                                      Launch for leaner usage-based DB

  **Queue**                           Upstash Redis initially; Cloudflare
                                      Queues is a strong alternative if
                                      the API edge moves heavily to
                                      Workers

  **Worker hosting**                  Railway Pro once external
                                      publishers depend on it; Hobby is
                                      enough for the Buddy prototype

  **Storage**                         Cloudflare R2

  **Bot protection**                  Cloudflare Turnstile

  **Transactional email**             Resend initially; evaluate SES when
                                      notification volume becomes
                                      material

  **AI primary**                      Benchmark DeepSeek V4 Flash vs
                                      GPT-5.6 Luna on 50--100 Buddy
                                      releases; route by quality/cost,
                                      not brand loyalty

  **Premium AI**                      GPT-5.6 Terra or another
                                      empirically better model only when
                                      editor requests premium/escalated
                                      rewrite

  **Billing**                         Stripe Checkout + Billing at Hub
                                      level
  -----------------------------------------------------------------------

# Research limitations / decisions requiring testing

> **•** Model writing quality is publication-specific; price tables do
> not determine whether DeepSeek, OpenAI or Gemini best matches Buddy\'s
> editorial voice. Run a blind editorial benchmark.
>
> **•** Scanned PDFs need OCR. For v0.1, reject/flag them for manual
> handling rather than adding OCR complexity until real submission data
> justifies it.
>
> **•** Malware scanning strategy depends on where uploads are
> processed. A container worker can run scanner tooling; pure
> edge/serverless designs are more constrained.
>
> **•** Final rights language, privacy disclosures, PR sender terms and
> paid-wire editorial-disclosure policy need legal review.
>
> **•** Infrastructure ranges exclude engineering labor, customer
> support, legal, accounting, insurance and sales/marketing.
>
> **•** API/vendor prices are current as of September 5, 2026 and can
> change; keep provider adapters and cost thresholds configurable.

## Email intake architecture

Default future email onboarding should be Smashfire-managed
per-publisher intake aliases. This keeps email infrastructure
centralized and decoupled from publisher hosting while requiring almost
no technical setup from a WordPress publisher. Forwarding,
Google/Microsoft connections and IMAP remain alternate connectors rather
than architectural dependencies.

## Paid pickup guardrail

Keep ordinary distribution and compensated pickup as distinct products
in the data model and UI. The first is editorial consideration/earned
pickup; the second is a marketplace transaction. This separation
protects publisher choice, buyer reporting, payout accounting,
disclosure compliance and the credibility of the network.

# Bottom line

The Buddy prototype should be intentionally small in user-facing scope
but should run on the same independently deployed, tenant-aware Hub
intended for the network. Buddy is Tenant #001, not the architectural
boundary. Build one excellent submission → triage → draft → rewrite →
publish loop while keeping canonical data, AI control,
assets/provenance, sender reputation, quotas, billing and distribution
Hub-owned. That avoids a future Buddy-to-network rewrite and makes
publisher #002 an onboarding exercise rather than a rearchitecture.

# Selected current sources

[[WordPress REST API
Handbook]{.underline}](https://developer.wordpress.org/rest-api/)

[[WordPress Custom Post
Types]{.underline}](https://developer.wordpress.org/plugins/post-types/registering-custom-post-types/)

[[WordPress REST
authentication]{.underline}](https://developer.wordpress.org/rest-api/using-the-rest-api/authentication/)

[[WordPress oEmbed
providers]{.underline}](https://developer.wordpress.org/reference/hooks/oembed_providers/)

[[DeepSeek API
pricing]{.underline}](https://api-docs.deepseek.com/quick_start/pricing/?article_id=article_1779470751466_8)

[[OpenAI GPT-5.6
Luna]{.underline}](https://developers.openai.com/api/docs/models/gpt-5.6-luna)

[[OpenAI GPT-5.6
Terra]{.underline}](https://developers.openai.com/api/docs/models/gpt-5.6-terra)

[[Google Gemini API
pricing]{.underline}](https://ai.google.dev/gemini-api/docs/pricing)

[[Cloudflare Workers
pricing]{.underline}](https://developers.cloudflare.com/workers/platform/pricing/)

[[Cloudflare R2
pricing]{.underline}](https://developers.cloudflare.com/r2/pricing/)

[[Cloudflare Queues
pricing]{.underline}](https://developers.cloudflare.com/queues/platform/pricing/)

[[Cloudflare Turnstile
plans]{.underline}](https://developers.cloudflare.com/turnstile/plans/)

[[Cloudflare Turnstile
validation]{.underline}](https://developers.cloudflare.com/turnstile/get-started/server-side-validation/)

[[Supabase pricing]{.underline}](https://supabase.com/pricing)

[[Neon pricing]{.underline}](https://neon.com/pricing)

[[Railway pricing]{.underline}](https://railway.com/pricing)

[[Upstash Redis pricing]{.underline}](https://upstash.com/pricing/redis)

[[Resend pricing]{.underline}](https://resend.com/pricing/)

[[Amazon SES pricing]{.underline}](https://aws.amazon.com/ses/pricing/)

[[Stripe pricing]{.underline}](https://stripe.com/pricing)

[[Stripe Billing
pricing]{.underline}](https://stripe.com/billing/pricing)

[[OWASP File Upload Cheat
Sheet]{.underline}](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
