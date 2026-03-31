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

All uploaded files are untrusted.

- Validate file content, not only file extension
- Enforce upload size limits
- Reject unsupported geometry types in v1
- Handle archive extraction carefully for Shapefile uploads
- Record failures without exposing internal paths or stack traces to users
- Keep raw uploads outside the web root

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
