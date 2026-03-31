# GeoFabric

Full-stack geospatial platform for ingesting, validating, processing, and
visualizing polygon-based GIS datasets at scale. Upload polygon data in common
formats, normalize it to a canonical model backed by PostGIS, and explore it
interactively on a web map.

## Why GeoFabric?

Working with polygon-based GIS data at scale is hard. Datasets arrive in
different formats, coordinate reference systems vary, geometries are often
invalid, and rendering millions of high-vertex polygons in a browser requires
careful architecture. GeoFabric provides a single pipeline that ingests raw
polygon datasets, validates and repairs geometry, normalizes everything to
EPSG:4326, stores it in PostGIS with full provenance, and serves it through
a web map with feature inspection and filtering. The goal is to make the
entire lifecycle — upload, validate, store, explore — reliable and traceable.

## Architecture

```
                    [CDN / Edge Cache]
                           |
[React + TypeScript + MapLibre GL JS]
        |
   -----+------------------
   |                       |
[GraphQL API]     [Martin tile server]
 (Strawberry/       (REST, binary MVT)
  FastAPI)                 |
   |                       |
   +-----------+-----------+
               |
        [PgBouncer]
               |
          [PostGIS]
               |
          [Redis]
               |
       [Celery workers + DuckDB]
               |
       [Object Storage]
```

- **React + MapLibre GL JS** — Browser-based map UI with feature inspection
  and filtering.
- **GraphQL API (Strawberry / FastAPI)** — All data operations: upload,
  query, mutate. Code-first schema with Pydantic integration.
- **Martin** — Standalone Rust-based vector tile server. Reads directly from
  PostGIS and serves binary MVT tiles over REST.
- **PgBouncer** — Connection pooling to multiplex thousands of user
  connections to PostgreSQL.
- **PostGIS** — Spatial data storage, indexing, and query engine.
- **Redis** — Caching for expensive spatial queries and job state management.
- **Celery + DuckDB** — Background job processing for ingestion, spatial
  operations, and exports. DuckDB handles batch spatial processing with
  larger-than-memory streaming.
- **Object Storage** — Raw uploaded files preserved with provenance metadata.
- **CDN** — Edge caching for tile requests, absorbing repeat loads from
  concurrent users.

## Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React, TypeScript, MapLibre GL JS, deck.gl (optional) |
| **Backend** | Python 3.12+, FastAPI, Strawberry (GraphQL), Pydantic v2, Uvicorn |
| **Geospatial** | Shapely 2.x, DuckDB + spatial extension, Fiona, pyproj, GDAL/OGR |
| **Storage** | PostGIS, SQLAlchemy 2.x + GeoAlchemy2, Alembic, Redis, S3-compatible object storage |
| **Tile Serving** | Martin (Rust), CDN (CloudFront / Cloudflare) |
| **Job Processing** | Celery + Redis, DuckDB (within workers), Python asyncio |
| **Infrastructure** | Docker Compose (local development) |

## Key Capabilities

- **Ingestion formats:** GeoJSON, Shapefile, GeoParquet, WKT
- **Spatial operations:** CRS detection and reprojection, geometry validation
  and repair, buffer, union, intersection, simplification
- **Analysis:** Area computation, bounding box calculation, validation
  summaries, attribute filtering, spatial intersection queries
- **Export formats:** GeoParquet (via DuckDB)
- **Visualization:** Interactive web map with zoom-based simplification,
  feature inspection on click, attribute-based filtering, progressive detail
  loading from continental to field-level zoom

## Getting Started

### Prerequisites

- **Docker** and **Docker Compose** — for PostGIS, Redis, Martin, and other
  services
- **Node.js** — for the React frontend
- **Python 3.12+** — for the FastAPI backend

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/jmanico/geo-fabric.git
   cd geo-fabric
   ```

2. Start local services with Docker Compose:

   ```bash
   docker compose up -d
   ```

   This starts PostGIS, Redis, Martin, the API server, and the frontend.

3. Verify that the services are running:

   ```bash
   docker compose ps
   ```

4. Open the frontend in a browser at the URL shown in the Docker Compose
   output.

## Project Structure

```
geo-fabric/
├── INITIAL-PLAN.md          # Full system design, data model, API, milestones
├── ARCHITECTURE.md          # Tech stack, architecture diagram, scale requirements
├── CODING-CONVENTIONS.md    # Coding standards, security, testing conventions
├── REQUIREMENT-TEMPLATE.md  # Issue template for new work
├── CLAUDE.md                # AI contributor instructions
└── README.md                # This file
```

Frontend and backend live in separate directories within the monorepo. See
the spec documents for full details on the planned directory layout.

## Documentation Index

| Document | Description |
|---|---|
| [INITIAL-PLAN.md](INITIAL-PLAN.md) | Full system design: user flows, data model, security requirements, delivery phases |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Tech stack details, architecture diagram, library versions, scale and performance requirements |
| [CODING-CONVENTIONS.md](CODING-CONVENTIONS.md) | Code style, naming, error handling, security rules, testing tiers |
| [REQUIREMENT-TEMPLATE.md](REQUIREMENT-TEMPLATE.md) | Issue template ensuring every task is testable, traceable, and implementable without prior context |

## Development

### Linting

- **Python:** `ruff check .` and `ruff format --check .` — zero tolerance for
  lint warnings.
- **TypeScript:** ESLint and Prettier — zero tolerance for lint warnings.

### Testing

Tests use **pytest** with three tiers:

| Tier | Scope | Target |
|---|---|---|
| **Fast** | Unit tests, geometry correctness, input validation | Under 2 minutes, every commit |
| **Medium** | Integration tests, round-trip fidelity, API contracts | Under 10 minutes, every PR |
| **Slow** | Large dataset tests, performance benchmarks, fuzzing | Under 60 minutes, nightly |

Property-based testing with **Hypothesis** for geometry invariants. PostGIS
runs in Docker for integration tests — the database is never mocked for
integration-level concerns.

### Pre-Commit Hooks

Run all linters and formatters before committing. Configure pre-commit hooks
to enforce this automatically.

## Security

All inputs are untrusted. Key principles from the coding conventions:

- **File validation:** Validate file content (magic bytes, structure), not
  just the file extension.
- **Size limits:** Enforce upload size limits at the ASGI layer.
- **Archive extraction:** Prevent path traversal when extracting Shapefile
  archives.
- **Query parameterization:** All database queries use parameterized
  statements via SQLAlchemy and DuckDB. Never interpolate user input into SQL.
- **No shell execution:** Never pass user input to shell commands.
- **Safe logging:** No internal file paths, credentials, or PII in log
  output. Use structured JSON logging.
- **Secrets management:** No secrets or credentials in code. Use environment
  variables or a secrets manager.
- **GIS parsing isolation:** Isolate native GIS tooling (GDAL/OGR) in
  subprocesses.
- **Task timeouts:** All Celery tasks have explicit max runtime timeouts.
- **GraphQL limits:** Query depth and complexity limits enforced at the
  gateway layer.

## Contributing

1. **Branching:** Create feature branches from `main` using the naming
   convention `issue-<number>-<short-description>`. One branch per issue, one
   PR per branch.
2. **Issue template:** Every issue must follow the structure in
   [REQUIREMENT-TEMPLATE.md](REQUIREMENT-TEMPLATE.md). Requirements must be
   testable, traceable to the spec, and include a development plan and test
   plan.
3. **PR workflow:** PRs require review before merge. Delete branches after
   merge.
4. **Code quality:** Run linters and tests before submitting. Zero lint
   warnings tolerated.

## Data Model Overview

The system is built around three core entities:

- **Dataset** — Represents an uploaded polygon dataset. Tracks the source
  format, original filename, source and normalized CRS, feature count,
  bounding box extent, ingestion status, validation summary, and the path to
  the preserved raw file.

- **Feature** — An individual polygon or multipolygon within a dataset.
  Stores the normalized geometry (always EPSG:4326), source attributes as
  JSON, computed area in square meters, and per-feature validation status
  with messages describing any repairs.

- **IngestionRun** — Records the execution of an ingestion pipeline for a
  dataset. Tracks start time, finish time, status (running/complete/failed),
  and a human-readable outcome message.

A Dataset has many Features and many IngestionRuns. Each Feature and
IngestionRun belongs to exactly one Dataset.

## Use Case: USDA Crop Sequence Boundaries

The primary validation dataset is the USDA Crop Sequence Boundaries (CSB)
dataset, which contains millions of agricultural field polygons across the
United States. GeoFabric uses this dataset to validate that the platform can:

- Ingest and store millions of polygons with high vertex counts
- Handle polygons representing fields up to 2,000+ hectares (50,000+ vertices
  at 3-meter resolution)
- Serve interactive map views at scale with zoom-based simplification — from
  continental overview (polygons simplified to bounding boxes) down to
  field-level zoom (full 3-meter resolution boundaries)
- Compute spatial queries and analysis across large polygon collections

## Milestones

### Phase 1 — Foundation

Repository scaffold, PostGIS-backed backend, GeoJSON upload and ingestion,
basic map view for stored data.

### Phase 2 — Completeness

Shapefile ingestion, validation reporting, feature detail view, basic
server-side filtering.

### Phase 3 — Scale Validation

Test against one large real-world dataset, performance tuning based on
measured bottlenecks, decide whether vector tiles or background jobs are
needed based on actual data.
