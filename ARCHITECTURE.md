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

## First Build Checklist

- One backend service
- One frontend app
- One PostGIS database
- Seed fixture or sample dataset
- End-to-end ingestion and visualization test
