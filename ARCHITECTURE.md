# GeoFabric — Lean Architecture

## Architectural Principle

Start with the smallest stack that can prove the core workflow. Add complexity
only after a measured bottleneck or a missing product need appears.

## V1 Stack

### Frontend

- React
- TypeScript
- Vite
- MapLibre GL JS

### Backend

- Python 3.12+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x

### Geospatial

- PostGIS for storage and spatial queries
- Shapely for geometry validation and repair
- pyproj for CRS handling
- Fiona for GeoJSON and Shapefile parsing

### Storage

- PostgreSQL with PostGIS
- Local filesystem storage for raw uploads in development

### Local Development

- Docker Compose for PostGIS
- API and frontend can run directly on the host for faster iteration

## Why This Is Enough

This stack supports the full V1 loop without introducing distributed-system
overhead:

- Upload files
- Parse and validate features
- Normalize and store geometries
- Query data back out
- Render it in a map client

## Explicitly Deferred

These can be added later if evidence justifies them:

- GraphQL
- Celery
- Redis
- Martin
- PgBouncer
- CDN integration
- DuckDB
- deck.gl

## System Shape

```
[React + MapLibre]
        |
     [FastAPI]
        |
 [PostgreSQL + PostGIS]
        |
   [Raw Upload Storage]
```

## API Direction

Use REST for V1. Keep it boring.

Suggested endpoints:

- `POST /datasets` to upload a dataset
- `GET /datasets` to list datasets
- `GET /datasets/{id}` to fetch dataset metadata and validation summary
- `GET /datasets/{id}/features` to fetch features in the current viewport or by
  filter
- `GET /datasets/{id}/features/{feature_id}` to inspect one feature

If GraphQL becomes useful later, add it after the object model and frontend
needs are stable.

## Data Access Strategy

- Store canonical geometry in PostGIS as `MULTIPOLYGON`
- Store source attributes as JSONB
- Use GIST indexes for geometry
- Keep raw source files for audit and reprocessing

## Performance Strategy For V1

Do not design around speculative 10K-user load before a working product exists.

Start with:

- Bounding-box queries
- Pagination or feature limits
- Server-side filtering
- Geometry simplification only if map rendering proves slow

Then measure.

## Upgrade Triggers

Only add more infrastructure when one of these happens:

- Request latency is consistently unacceptable under real usage
- Upload or processing tasks block the API long enough to hurt the product
- Large dataset rendering cannot be solved with query limits and simplification
- Deployment traffic requires connection pooling or edge caching

## Security Architecture

The [threat model](docs/threat-model/THREAT-MODEL-REPORT.md) was written against
the full architecture. With the lean V1 scope many components (GraphQL, Celery,
Redis, Martin, DuckDB, CDN, PgBouncer) are deferred, so the threats targeting
those components are also deferred. The threats below apply to the V1 stack.

### Authentication And Authorization

V1 is a single-user, local-first application. There is no multi-user
authentication or authorization in V1. Before any networked or multi-user
deployment, OAuth2/OIDC and dataset-level ownership must be designed and
implemented (threat model CT-01, CT-02).

### Trust Boundaries

```
[Browser]  ──  untrusted  ──>  [FastAPI]  ──  trusted  ──>  [PostGIS]
                                   |
                            [Raw Upload Storage]
```

All data crossing the browser-to-API boundary is untrusted: uploaded files,
query parameters, and request bodies. The API is the sole enforcement point.

### Upload And Ingestion Security

These controls must be enforced at the API layer before any file reaches the
geospatial parsing libraries:

- **Upload size limit** — reject files above a configured maximum (CT-07)
- **Content-based format detection** — validate magic bytes and structure, not
  file extension
- **ZIP archive safety** — reject entries with path traversal sequences (`..`,
  absolute paths), enforce maximum extraction size and compression ratio to
  block zip bombs, allow only Shapefile extensions (.shp, .shx, .dbf, .prj,
  .cpg) (CT-04, CT-13)
- **Streaming uploads** — do not buffer entire files in memory

### Native Library Isolation

Fiona (GDAL/OGR), Shapely (GEOS), and pyproj (PROJ) are C/C++ libraries with
historical CVE exposure. All file parsing through these libraries should run
in isolated subprocesses with memory and CPU limits so that a crafted input
cannot compromise the API process (CT-03).

### API Hardening

- **Rate limiting** — per-IP request rate limits on all endpoints, stricter
  limits on upload (CT-09)
- **CORS** — restrict allowed origins to the frontend origin (CT-16)
- **Security headers** — Content-Security-Policy, X-Content-Type-Options,
  X-Frame-Options, Strict-Transport-Security (CT-16)
- **Structured error responses** — never expose internal paths, stack traces,
  or database details to clients

### Database Security

- **Parameterized queries only** — via SQLAlchemy; never interpolate user input
  into SQL
- **Statement timeout** — set `statement_timeout` on the PostgreSQL connection
  to prevent expensive spatial queries from locking the database (CT-08)
- **Credentials from environment** — no secrets in code or version control
  (CT-19)
- **Raw uploads outside the web root** — stored on the local filesystem in a
  directory that is not served by the frontend

### Output Encoding And XSS Prevention

GeoJSON feature properties are stored as JSONB and rendered in the frontend
inspector. Properties must be treated as untrusted:

- Never use `dangerouslySetInnerHTML`
- Sanitize or encode properties before rendering in DOM attributes
- Rely on React JSX auto-escaping as a baseline, not as the only defense
  (CT-14)

### Audit Logging

Log security-relevant events in structured JSON format: upload attempts,
ingestion results, validation failures, and any rejected requests. Include
request metadata (IP, user-agent) but never log credentials, PII, or internal
file paths (CT-15).

### Dependency Management

- Audit all third-party packages for known CVEs before adoption
- Enable automated dependency scanning (pip-audit, npm audit) in CI (CT-25)

### Deferred Security Work

These controls become necessary when the corresponding infrastructure is added:

- Redis AUTH and TLS (when Redis is introduced)
- Celery JSON serialization and message signing (when Celery is introduced)
- Martin layer restrictions and read-only DB user (when Martin is introduced)
- Inter-service TLS and per-service DB credentials (when the system becomes
  multi-service)
- Encryption at rest (before handling regulated data)

## First Build Checklist

- One backend service
- One frontend app
- One PostGIS database
- Seed fixture or sample dataset
- End-to-end ingestion and visualization test
