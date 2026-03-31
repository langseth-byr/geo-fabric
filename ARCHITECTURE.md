# GeoFabric — Architecture

## Tech Stack

### Frontend
- **React + TypeScript**
- **MapLibre GL JS** for map rendering
- Optional **deck.gl** for advanced visualization

### Backend API
- **Python 3.12+**
- **FastAPI** — ASGI framework hosting GraphQL and the tile REST endpoint
- **Strawberry** — GraphQL library with async support, Pydantic integration, code-first schema
- **Pydantic v2** — validation and settings
- **Uvicorn** — ASGI server

### Geospatial Libraries
- **Shapely 2.x** — geometry operations (union, intersection, buffer, simplify, validate). Wraps GEOS (C++), vectorized ufuncs for batch ops.
- **DuckDB + spatial extension** — tabular geospatial data processing via SQL. Larger-than-memory streaming, native GeoParquet read/write, spatial functions (ST_Area, ST_Intersects, etc.), zero-copy Parquet/CSV reads.
- **Fiona** — Shapefile, GeoJSON, GeoPackage I/O (wraps GDAL/OGR)
- **pyproj** — CRS detection, transformation, reprojection (wraps PROJ)
- **GDAL/OGR** (via Fiona) — 200+ format support, content-based detection

### Storage
- **PostGIS** — spatial data storage and indexing
- **PgBouncer** — connection pooling
- **SQLAlchemy 2.x + GeoAlchemy2** — ORM with PostGIS geometry column support
- **Alembic** — database migrations
- **Redis** — caching and job state
- **Object storage** (S3-compatible or local) — raw uploaded files

### Tile Serving
- **Martin** (Rust, MapLibre team) — standalone vector tile server reading directly from PostGIS
- **CDN** (CloudFront, Cloudflare, or similar) — edge caching for tile requests
- Serves `GET /{layer}/{z}/{x}/{y}` as binary MVT over REST

### Job Processing
- **Celery + Redis** — persistent background jobs (ingestion, spatial processing, exports). Retries, monitoring via Flower, task routing.
- **DuckDB** used within Celery workers for batch spatial processing
- **Python asyncio** — lightweight async within the API process

### Infrastructure
- **Docker Compose** — local development (PostGIS, Redis, Martin, API, frontend)

### Ingestion Formats
- GeoParquet
- GeoJSON
- Shapefile
- WKT

---

## Architecture Diagram

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

---

## API Design

### GraphQL (all data operations)
- **Mutations**: dataset upload (via multipart GraphQL upload spec), validate, reproject, simplify, intersect, export, delete
- **Queries**: dataset metadata, paginated features with spatial/attribute filters, job status and results, spatial intersection queries
- **Subscriptions** (future): job progress, live processing updates
- Strawberry integrates with FastAPI and supports multipart file uploads

### REST (tile serving only)
- `GET /{layer}/{z}/{x}/{y}` — binary MVT tiles served by Martin directly from PostGIS
- Tiles must be REST: binary format, HTTP caching, CDN-friendly GET requests, MapLibre expects standard tile URLs

---

## Library Versions

| Library | Version | Purpose |
|---|---|---|
| FastAPI | 0.115+ | ASGI framework |
| Strawberry | 0.250+ | GraphQL server |
| Pydantic | 2.x | Validation |
| SQLAlchemy | 2.x | ORM |
| GeoAlchemy2 | 0.15+ | PostGIS geometry columns |
| Shapely | 2.x | Geometry operations |
| DuckDB | 1.2+ | Spatial data processing, GeoParquet I/O |
| Fiona | 1.10+ | Format I/O (Shapefile, GeoJSON, etc.) |
| pyproj | 3.7+ | CRS management |
| Celery | 5.x | Background jobs |
| Martin | 0.15+ | Vector tile server |
| PgBouncer | 1.23+ | PostgreSQL connection pooling |

---

## Scale and Performance Requirements

### Spatial Resolution
- 3m x 3m minimum resolution for polygon boundaries
- A 2,000-hectare field at 3m resolution can produce 50,000+ vertices per polygon

### Polygon Size
- Up to 2,000+ hectares per individual polygon (20 km²)
- Must support the largest agricultural fields globally:
  - Brazil (Mato Grosso, MATOPIBA): single soy/cotton fields routinely 1,000+ ha, some 5,000+ ha
  - Argentina (Pampas): 1,000-3,000 ha
  - Australia: pastoral holdings exceeding 10,000 ha
  - United States (Midwest): consolidated operations reaching 1,000+ ha

### Concurrency
- 10,000 concurrent users performing map interactions, spatial queries, and data exploration

### Dataset Scale
- Millions of polygons per dataset (validated against USDA CSB)
- Billions of vertices across all datasets

### Performance Implications
- **Tile serving**: CDN in front of Martin absorbs repeat tile requests from 10K users. Martin handles cache misses from PostGIS.
- **Connection pooling**: PgBouncer required to multiplex 10K user connections to PostGIS.
- **Query caching**: Redis caches expensive spatial query results.
- **Large polygon ops**: 50K+ vertex polygons are CPU-intensive for buffer/union/intersection — run in Celery workers with appropriate timeouts.
- **Zoom-based simplification**: At continental zoom a 2,000 ha field is a single pixel (simplify to bbox). At field zoom render full 3m-resolution boundary. Progressive detail loading mandatory.
- **DuckDB streaming**: Larger-than-memory processing essential for datasets with millions of high-vertex polygons.

---

## Risks and Mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| 10K concurrent users overwhelm tile serving | HIGH | CDN edge caching in front of Martin. Tiles are highly cacheable. |
| Large polygon processing timeouts | MEDIUM | Celery workers with configurable timeouts. Pre-simplify where appropriate. Shapely 2.x vectorized ops. |
| GIL limits Python concurrency | MEDIUM | Shapely releases GIL during C ops. DuckDB runs its own threads. Heavy work in Celery (separate processes). FastAPI async for I/O. |
| DuckDB spatial extension maturity | LOW | PostGIS is authoritative for serving. DuckDB for batch only. Convert to Shapely for edge cases. |
| GraphQL file uploads | LOW | Strawberry supports multipart spec. Size limits at ASGI layer. |
