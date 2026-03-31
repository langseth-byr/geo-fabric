# GeoFabric — Project Memory

## Project Overview
Full-stack geospatial platform for ingesting, validating, processing, analyzing, and visualizing polygon-based GIS datasets at scale.

## Key Documents
- [INITIAL-PLAN.md](INITIAL-PLAN.md) — Full system design, data model, API, UX
- [ARCHITECTURE.md](ARCHITECTURE.md) — Tech stack
- [CODING-CONVENTIONS.md](CODING-CONVENTIONS.md) — Coding standards, security, testing

## Workspace Setup
1. Clone the repo
2. Use Docker Compose for local services (PostGIS, Redis)
3. Frontend and backend live in separate directories within the monorepo

## Issue Creation

When creating new GitHub issues, **always** use the structure defined in [REQUIREMENT-TEMPLATE.md](REQUIREMENT-TEMPLATE.md). Every issue must include:

- Summary and motivation with spec references
- Numbered, testable requirements (no subjective language)
- Data model and API changes (or "None")
- Security considerations (mandatory for untrusted input)
- Step-by-step development plan with file paths
- Test plan mapping each requirement to a test with tier
- Concrete acceptance criteria checklist

Do not create issues that skip sections or use vague requirements. If a requirement cannot be traced to INITIAL-PLAN.md, ARCHITECTURE.md, or CODING-CONVENTIONS.md, update the spec first.

## Branching Strategy
- `main` is the stable branch — always deployable
- Create feature branches from `main`: `issue-<number>-<short-description>`
- One branch per issue, one PR per branch
- PRs require review before merge
- Delete branches after merge
- Multiple contributors can work in parallel on separate issue branches

