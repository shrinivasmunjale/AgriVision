# AgriVision AI — Recommended Tech Stack (2026)

> Evaluated against the AgriVision AI PRD (drone-based tomato leaf disease detection & treatment recommendation platform). This document proposes the stack I'd actually ship with in 2026, validates what the PRD already got right, and flags where the market has moved since the PRD's original picks (Vite+React, MySQL, hand-rolled JWT).

---

## TL;DR — Recommended Stack

| Layer | Recommendation | PRD's Original Choice | Verdict |
|---|---|---|---|
| Frontend | **Next.js 15 (App Router) + JavaScript + Tailwind CSS + TanStack Query + Framer Motion** | Vite + React + TS + Tailwind | Upgrade — same DX, adds SSR/edge/image optimization for free; JS instead of TS per your preference |
| Backend | **FastAPI (Python) + SQLAlchemy 2.0 + Pydantic v2**, ML inference in a separate worker service | FastAPI + SQLAlchemy | Confirmed — right call, refine the architecture |
| Auth | **Supabase Auth** (or Clerk) for MVP; self-hostable JWT (fastapi-users) as the enterprise/gov fallback | Custom JWT | Upgrade — don't hand-roll auth in 2026 |
| Database | **PostgreSQL** (via Neon or Supabase, serverless) | MySQL | Change — Postgres directly enables two features already in your Future Scope |
| Deployment | **Vercel** (frontend) + **Railway** (API + Postgres) + **Modal** (GPU model serving) + **Cloudflare R2** (image storage) | Not specified | New — filled in |

---

## 1. Frontend: Next.js 15 (App Router) + JavaScript + Tailwind CSS

**Recommendation:** Keep everything the PRD specified (Tailwind, TanStack Query, Axios, Framer Motion) but swap the build tool/framework from **Vite+React** to **Next.js**, and use plain **JavaScript** rather than TypeScript.

**Justification:**
- **Image optimization is not optional here.** Your entire product is built around uploading and displaying high-res drone/leaf photos (up to 50MB per the Scan screen mockup). Next.js's `<Image>` component gives you automatic resizing, lazy-loading, and CDN-backed delivery out of the box — with Vite you'd hand-build this.
- **Mixed audience, mixed rendering needs.** Government departments and agribusiness buyers will look at a marketing/landing page before signing up (SEO matters there); the farmer dashboard and admin panel are fully authenticated SPA-style experiences (SEO doesn't matter there). Next.js's App Router lets you statically generate the marketing pages and client-render the authenticated dashboard in one codebase — Vite forces you to either bolt on a separate marketing site or ship everything as a client-only SPA with no SEO story.
- **Edge middleware for auth.** JWT/session validation can run at the edge before a request even reaches your React tree — useful for gating the Admin panel and Farmer dashboard cleanly.
- **API routes as a BFF (backend-for-frontend).** Useful for lightweight tasks (signed upload URLs, PDF proxy download) without round-tripping through FastAPI for everything.
- **Cost of switching is low.** Your component code, Tailwind config, TanStack Query hooks, and Framer Motion animations from the DESIGN.md are framework-agnostic — this is a build-tool swap, not a rewrite.

**When Vite+React is still the right call:** if you deprioritize the public marketing site entirely and this stays an internal tool behind a login wall with no SEO ambitions, plain Vite+React is simpler and has a faster local dev loop. Given the PRD explicitly targets investors and government departments (who will want a credible public-facing site), I'd still lean Next.js.

**On using JavaScript instead of TypeScript:** this trades away compile-time type checking on props, API response shapes, and form data — the main place bugs show up in a data-heavy app like this (e.g., a `confidence_score` silently coming back as a string instead of a number). Since you're skipping TS, two lightweight guardrails are worth keeping instead:
- **Zod or Yup for runtime validation** at the API boundary (validate the shape of `/predictions` and `/diseases` responses as they come in) — this catches the same class of bugs TS would have, just at runtime instead of compile time.
- **JSDoc type comments** (`/** @param {{confidence: number}} result */`) — gives you inline editor autocomplete in VS Code with zero build-step overhead, without committing to full TypeScript.

---

---

## 2. Backend: FastAPI (Python) + SQLAlchemy 2.0

**Recommendation:** Keep FastAPI as specified in the PRD — this is the correct choice and remains the dominant pattern for AI-integrated products in 2026. Refine the architecture into two services rather than one monolith.

**Justification:**
- **Same-language ML pipeline.** Your model (EfficientNetB0), preprocessing (OpenCV), and recommendation engine (TF-IDF/cosine similarity via scikit-learn) are all Python-native. Running FastAPI means your inference code and your API code share one language, one dependency tree, and one deploy artifact — no serialization boundary, no maintaining a Node.js API that calls out to a separate Python microservice over HTTP for every prediction.
- **Async by default.** Drone image batch uploads (the PRD's core differentiator over single-leaf mobile apps) are I/O-heavy — async FastAPI handles concurrent uploads/preprocessing far better than a sync WSGI framework.
- **Free, accurate API docs.** Pydantic v2 models generate OpenAPI/Swagger automatically — directly satisfies the PRD's API documentation requirement with zero extra work.
- **Split inference from the API process.** Don't run EfficientNetB0 inference inline inside your request handler. Batch drone uploads (the PRD explicitly calls out 50+ images) will block or starve your API workers if inference runs synchronously in the same process. Recommended split:
  - **`api` service** (FastAPI): auth, CRUD, orchestration, enqueues inference jobs.
  - **`inference` service** (separate FastAPI or plain Python worker, GPU-backed): loads the EfficientNetB0 model once, processes a queue (Redis/RQ or Celery), writes results back to Postgres, and the frontend polls or gets a websocket push when a batch finishes.
  - This also lets you scale the GPU-bound inference service independently of the cheap, CPU-bound API service — meaningful cost savings at farm-fleet scale.
- **ORM:** SQLAlchemy 2.0 (async engine) + Alembic for migrations, exactly as the PRD specified — still the standard pairing with FastAPI in 2026.

**Alternative considered — Django + DRF:** stronger "batteries-included" story (admin panel, auth, ORM all built-in), which is tempting since you need an Admin Panel anyway. I still recommend FastAPI because (a) you need real async performance for batch image handling, and (b) the auto-generated OpenAPI schema is materially better for a frontend team building against the API in parallel. If your team is more Django-fluent than FastAPI-fluent, Django+DRF is a defensible second choice.

---

## 3. Authentication: Supabase Auth (MVP) → self-hosted JWT (enterprise/gov)

**Recommendation:** Don't hand-roll JWT issuance/refresh/password-reset in 2026. Use **Supabase Auth** (or **Clerk** as a close alternative) for the MVP and pilot phase; keep a self-hosted fallback (**fastapi-users** + JWT, as SQLAlchemy-native as the PRD's original plan) ready for enterprise/government contracts that require full data residency.

**Justification:**
- **Security surface.** Password hashing, token rotation, session invalidation, and social login (Google/Apple — both shown in your Login mockup) are exactly the kind of code you don't want to be debugging in production. Managed auth providers are audited, patched continuously, and handle the edge cases (leaked password detection, rate-limited login attempts, MFA) that a hand-rolled JWT system typically skips in v1.
- **Matches your mockup exactly.** The Login screen already shows "Continue with Google / Apple" — Supabase Auth and Clerk both give you these as configuration, not custom OAuth-flow code.
- **Role-based access, out of the box.** Farmer vs Admin role checks map directly onto Supabase's row-level security (RLS) policies or Clerk's organization roles — less custom middleware than a DIY JWT + role-column setup.
- **Why not commit to it permanently:** government agriculture departments (an explicit target segment in the PRD) will often require data residency or on-prem deployment that a SaaS auth provider can't satisfy. Because Supabase Auth issues standard JWTs, you can validate them in FastAPI the same way you'd validate self-issued tokens — so migrating a specific enterprise/gov customer to a self-hosted auth flow (fastapi-users, same JWT validation code) later is a contained change, not a rewrite.

---

## 4. Database: PostgreSQL (not MySQL)

**Recommendation:** Move from the PRD's MySQL to **PostgreSQL**, served via a serverless provider (**Neon** or **Supabase**) rather than a traditional always-on instance.

**Justification — this is the highest-leverage change from the original PRD:**
- **Your own Future Scope section requires it.** The PRD explicitly lists two features that Postgres solves natively and MySQL does not:
  - *"Disease heatmap using GPS coordinates"* → **PostGIS**, Postgres's geospatial extension, is the industry-standard way to store field/farm coordinates and run proximity/heatmap queries. MySQL's spatial support is materially weaker.
  - *"AI chatbot for farming assistance"* → if/when this becomes a RAG-style chatbot over your disease/treatment knowledge base, **pgvector** lets you store embeddings directly alongside your relational disease/pesticide data and run similarity search with plain SQL — no separate vector database to operate. MySQL has no equivalent first-party option.
- **Your recommendation engine could live partly in the database.** The TF-IDF/cosine-similarity matching the PRD specifies today runs fine in Python/scikit-learn — but as your treatment catalog grows, pgvector gives you a natural upgrade path to embedding-based similarity search without re-architecting the data layer.
- **Serverless Postgres fits your usage pattern.** Farm activity is bursty (post-flight upload windows, as the PRD itself notes) rather than constant. Neon and Supabase both scale compute to zero between bursts and branch the database per environment (instant staging DB copies for testing migrations) — cheaper and safer than an always-on MySQL instance for a pre-revenue/pilot-stage product.
- **Ecosystem alignment.** SQLAlchemy, Alembic, and FastAPI all treat Postgres as the reference database; you'll find more first-party tooling and fewer edge-case bugs than with MySQL.

**When MySQL would still be defensible:** if a specific government/enterprise customer's existing infrastructure standardizes on MySQL and that's a hard procurement requirement. Otherwise there's no advantage MySQL offers here that Postgres doesn't match or beat.

---

## 5. Deployment & Infrastructure

| Component | Recommendation | Why |
|---|---|---|
| Frontend (Next.js) | **Vercel** | Native platform for Next.js; automatic edge network, image optimization, preview deployments per PR |
| API (FastAPI) | **Railway** | One-click Postgres + Redis + Python service in a shared network; per-minute billing suits pilot-stage unpredictable load; Docker-based so it's portable off Railway later if a gov contract requires self-hosting |
| ML inference service | **Modal** (or Replicate) | Serverless GPU — EfficientNetB0 inference is bursty (batch drone uploads, not constant traffic); paying for an always-on GPU instance is wasteful at pilot scale. Modal spins up GPU workers on demand and scales to zero between farm upload windows |
| Object storage (drone images, PDF reports) | **Cloudflare R2** | S3-compatible API (drop-in with existing S3 tooling) with zero egress fees — meaningful since drone images are large and farmers will re-view/download reports repeatedly |
| Database | **Neon** or **Supabase Postgres** | Serverless Postgres with branching; pick Supabase specifically if you're also using Supabase Auth, to keep auth + data in one platform during MVP |
| CI/CD | **GitHub Actions** | Standard, free for public/small private repos, integrates directly with Vercel/Railway deploy hooks |
| Containerization | **Docker** for the API and inference services regardless of host | Keeps you portable — critical given government customers may eventually require on-prem or VPC-isolated deployment; both Railway and a future self-hosted Kubernetes cluster can run the same images |

**Migration path for enterprise/government contracts:** because every piece above (Postgres, Docker containers, JWT-based auth) is either open-source or exports cleanly, moving a specific customer from the managed stack (Vercel/Railway/Modal) to a VPC or on-prem deployment later is a redeployment, not a rewrite.

---

## 6. Machine Learning Serving — Specific Note

The PRD specifies TensorFlow/Keras + EfficientNetB0. Two additions worth planning for now rather than later:

- **Model versioning from day one.** Store model artifacts in object storage (R2/S3) with a clear version tag (`efficientnet-b0-v1.2.keras`), and log which model version produced each prediction in the `predictions` table. This is a one-line schema addition now vs. a painful migration later when you need to explain why historical predictions used a different model than today's.
- **Batch endpoint, not N single-image calls.** Since the PRD's core differentiator is bulk drone imagery (vs. competitors' single-photo mobile apps), build the inference service's primary interface as `POST /infer/batch` (accepts N images, returns N results) rather than looping single-image calls — this is both a better UX (one progress bar, not N requests) and meaningfully cheaper on serverless GPU billing (fewer cold starts).

---

## 7. Summary — What Changed From the PRD and Why

1. **Vite → Next.js, TypeScript → JavaScript:** same frontend stack otherwise (Tailwind, TanStack Query, Framer Motion); gains image optimization and a public-facing SEO story for investor/government audiences, at low switching cost. JS keeps the build simpler and removes a compile step — pair it with Zod/JSDoc (see Section 1) to keep the type-safety benefits TS would have given you.
2. **MySQL → PostgreSQL:** directly unlocks two features already listed in the PRD's own Future Scope (GPS heatmaps via PostGIS, AI chatbot via pgvector) that MySQL can't do natively.
3. **Custom JWT → Supabase Auth (with self-hosted fallback):** removes a class of security bugs from your MVP timeline while preserving a clean path to self-hosted auth for data-residency-sensitive government customers.
4. **FastAPI monolith → FastAPI (API) + separate GPU inference service:** prevents batch drone-image inference from blocking your API, and lets you pay for GPU only when a batch is actually running.
5. **Deployment fully specified:** Vercel + Railway + Modal + Cloudflare R2 + Neon/Supabase — chosen for pilot-stage cost efficiency (scale-to-zero everywhere) with a clear, low-friction path to self-hosted/on-prem for enterprise and government contracts later.
