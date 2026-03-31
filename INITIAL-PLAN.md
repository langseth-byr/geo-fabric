# GeoFabric — Practical Initial Plan

## Purpose

GeoFabric is a geospatial web application for uploading polygon datasets,
validating them, storing them with provenance, and visualizing them on a map.

The first version should prove one complete path:

1. Upload a dataset
2. Parse polygon features safely
3. Normalize CRS to EPSG:4326
4. Validate geometry and record issues
5. Store the dataset in PostGIS
6. Render the dataset in a web map
7. Inspect features and filter by basic attributes

If that loop works well on a real dataset, the project is viable. Everything
else is secondary.

## V1 Goals

- Accept one or two common polygon formats first: GeoJSON and Shapefile
- Preserve the raw uploaded file and provenance metadata
- Normalize geometries into a canonical PostGIS model
- Record validation warnings and repairs explicitly
- Render stored features in a browser map
- Support feature inspection and simple filtering
- Keep the system understandable enough for one engineer to build and maintain

## V1 Non-Goals

These are deferred until the first end-to-end slice is stable:

- GraphQL
- Celery
- Redis
- Martin
- CDN strategy
- Multi-tenant scaling work
- Temporal animation
- Multi-dataset comparison workflows
- GeoParquet support
- WKT import/export
- Advanced spatial analysis tools

## Primary User Flow

### 1. Upload

The user uploads a polygon dataset and provides a dataset name.

### 2. Ingestion

The backend:

- Detects the input format
- Parses features and properties
- Detects or reads CRS
- Reprojects to EPSG:4326 when possible
- Validates polygon and multipolygon geometry
- Stores the raw file plus ingestion results

### 3. Review

The user can see:

- Dataset status
- Feature count
- Bounding box
- Validation summary
- Any warnings or repairs performed

### 4. Explore

The user can:

- View the dataset on a map
- Click a feature to inspect properties
- Filter features by a small set of attributes
- Zoom and pan without loading the whole world into the client at once

## Minimal Data Model

### Dataset

| Field | Description |
|---|---|
| id | Dataset identifier |
| name | User-provided name |
| source_format | Detected input format |
| source_filename | Original filename |
| source_crs | CRS declared or detected from source |
| normalized_crs | Internal CRS, always EPSG:4326 |
| feature_count | Number of stored features |
| extent | Dataset bounding box |
| ingestion_status | pending, complete, failed |
| validation_summary | Aggregate counts of errors and repairs |
| raw_file_path | Stored raw upload location |
| created_at | Creation timestamp |
| updated_at | Last update timestamp |

### Feature

| Field | Description |
|---|---|
| id | Feature identifier |
| dataset_id | Parent dataset |
| geometry | Normalized polygon or multipolygon |
| properties | Source attributes as JSON |
| area_m2 | Computed area |
| validation_status | valid, repaired, invalid |
| validation_messages | Validation or repair notes |
| created_at | Creation timestamp |

### IngestionRun

| Field | Description |
|---|---|
| id | Ingestion run identifier |
| dataset_id | Related dataset |
| started_at | Start time |
| finished_at | Finish time |
| status | running, complete, failed |
| message | Human-readable outcome |

## Security Requirements

All uploaded files are untrusted. These requirements are derived from the
[threat model](docs/threat-model/THREAT-MODEL-REPORT.md), scoped to the lean V1
stack (no GraphQL, Celery, Redis, Martin, or DuckDB).

### File Upload And Ingestion

- Validate file content by magic bytes and structure, not file extension
- Enforce a configurable upload size limit (e.g. 500 MB)
- Stream uploads — do not buffer entire files in memory
- Reject unsupported geometry types in V1 (only Polygon and MultiPolygon)
- Sanitize GeoJSON feature properties at ingestion to prevent stored XSS
  (CT-14)

### Shapefile Archive Safety

- Reject ZIP entries containing path traversal sequences (`..`, absolute paths)
  (CT-04)
- Allow only Shapefile extensions (.shp, .shx, .dbf, .prj, .cpg)
- Enforce maximum extraction size and reject compression ratios above 100:1
  (CT-13)
- Limit ZIP entry count to a reasonable maximum (Shapefiles have 4-7 files)

### Native Library Isolation

- Run GIS parsing (Fiona, Shapely, pyproj) in isolated subprocesses with
  memory and CPU limits (CT-03)
- A crash in a native library must not take down the API process

### API Protection

- Apply per-IP rate limiting on all endpoints; stricter on upload (CT-09)
- Configure CORS to allow only the frontend origin (CT-16)
- Set security headers: CSP, X-Content-Type-Options, X-Frame-Options, HSTS
  (CT-16)
- Set PostgreSQL `statement_timeout` to prevent expensive spatial queries from
  blocking the database (CT-08)

### Error Handling And Logging

- Return structured error responses — never expose internal paths, stack traces,
  or database details
- Log security-relevant events (uploads, validation failures, rejected requests)
  in structured JSON (CT-15)
- Never log credentials, PII, or internal file paths

### Secrets And Storage

- No secrets in code or version control — use environment variables (CT-19)
- Keep raw uploads outside the web root
- Store database credentials in environment variables

### Dependency Management

- Audit third-party packages for known CVEs before adoption
- Run pip-audit and npm audit in CI (CT-25)

### Authentication And Authorization (Pre-Deployment)

V1 is single-user and local-first. Before any networked or multi-user
deployment, the following must be implemented:

- OAuth2/OIDC authentication with a proven identity provider (CT-01)
- Dataset-level ownership and RBAC (CT-02)
- Audit logging with user identity attribution (CT-15)

## Success Criteria For V1

The project is successful when all of the following are true:

- A real GeoJSON dataset can be uploaded, normalized, stored, and viewed
- A real Shapefile dataset can be uploaded, normalized, stored, and viewed
- Invalid polygon cases produce explicit validation output
- The map can display dataset features and inspect a clicked feature
- The codebase remains small enough that new work can be added without a major
  redesign

## Suggested Delivery Order

### Phase 1

- Repo scaffold
- PostGIS-backed backend
- GeoJSON upload and ingestion
- Basic map view for stored data

### Phase 2

- Shapefile ingestion
- Validation reporting
- Feature detail view
- Basic server-side filtering

### Phase 3

- One large real-world dataset test
- Performance tuning based on measured bottlenecks
- Decide whether vector tiles or background jobs are actually needed

## Deferred Expansion

Only after V1 is proven should the project consider:

- GeoParquet
- Background processing
- Vector tiles
- Export workflows
- Temporal analysis
- Dataset comparison
- Advanced spatial operations
