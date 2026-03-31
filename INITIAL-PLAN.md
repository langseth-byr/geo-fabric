# GeoFabric: Geospatial Polygon Processing and Visualization Platform

## Overview

Full-stack geospatial platform for ingesting, validating, processing, analyzing, and visualizing polygon-based GIS datasets at scale.

The system focuses on vector polygon data: administrative boundaries, parcels, agricultural fields, zoning regions, and custom overlays. It provides a deterministic and auditable pipeline from raw GIS ingestion through spatial processing to interactive visualization.

The platform prioritizes correctness, traceability, performance, and safe handling of untrusted geospatial inputs.

> **Related documents:**
> - [ARCHITECTURE.md](ARCHITECTURE.md) — Tech stack, library versions, architecture diagram, scale/performance requirements, risks
> - [CODING-CONVENTIONS.md](CODING-CONVENTIONS.md) — Coding standards, security requirements, testing strategy, development principles

---

## Goals

- Ingest real-world GIS polygon datasets (including agriculture machine data from John Deere and similar)
- Normalize all data into a canonical spatial model
- Provide robust geometry validation and repair
- Support spatial processing and analysis workflows
- Render large datasets efficiently in a web-based map UI (similar in spirit to QGIS, but not constrained to that design)
- Maintain full auditability of transformations
- Safely process untrusted geospatial files
- Scale to large datasets (millions of polygons)

---

## Data Ingestion

### Supported Formats

- GeoParquet
- GeoJSON
- Shapefile
- WKT

### Pipeline Responsibilities

- Detect and validate file type (content-based, not extension)
- Parse geometry and attributes
- Normalize coordinate reference system (CRS)
- Validate geometry integrity
- Detect malformed or self-intersecting polygons
- Preserve metadata and provenance (source of each polygon)
- Generate ingestion diagnostics

### CRS Handling

- Preserve source CRS
- Normalize to internal CRS (EPSG:4326)
- Track all transformations
- Fail safely on ambiguity
- Never silently reproject

### Geometry Validation

Detect and handle:

- Self-intersections
- Invalid rings
- Duplicate vertices
- Winding order issues
- Zero-area polygons
- Empty geometries
- CRS mismatches

All repairs must be explicit and traceable.

---

## Canonical Data Model

### SpatialFeature

| Field | Description |
|---|---|
| id | Unique feature identifier |
| dataset_id | Parent dataset reference |
| geometry_type | Polygon or MultiPolygon |
| raw_geometry | Original geometry as ingested |
| normalized_geometry | Geometry after CRS normalization and validation |
| bbox | Bounding box |
| centroid | Computed centroid |
| area | Computed area |
| perimeter | Computed perimeter |
| source_crs | Original coordinate reference system |
| normalized_crs | Internal CRS after normalization |
| properties | Arbitrary key-value attributes from source |
| validation_status | Pass, fail, or repaired |
| validation_errors | List of detected issues |
| provenance | Source file, ingestion timestamp, pipeline version |
| created_at | Record creation timestamp |
| updated_at | Last modification timestamp |

### Dataset

| Field | Description |
|---|---|
| id | Unique dataset identifier |
| name | Human-readable name |
| source_format | Original file format |
| source_file_uri | Location of raw uploaded file |
| declared_crs | CRS declared by the source file |
| normalized_crs | Internal CRS after normalization |
| feature_count | Number of features |
| extent | Spatial extent (bounding box) |
| ingestion_status | Pending, processing, complete, failed |
| validation_summary | Aggregate validation results |
| processing_history | Ordered list of operations applied |
| created_at | Record creation timestamp |
| updated_at | Last modification timestamp |

### ProcessingJob

| Field | Description |
|---|---|
| id | Unique job identifier |
| dataset_id | Target dataset |
| operation_type | Type of spatial operation |
| parameters | Operation parameters |
| status | Queued, running, complete, failed |
| result_artifact_uri | Location of output artifact |
| error_log | Error details if failed |
| created_at | Job creation timestamp |
| completed_at | Job completion timestamp |

---

## Spatial Processing

### Polygon Operations

- Union
- Intersection
- Difference
- Clipping
- Dissolve by attribute
- Simplification
- Buffering
- Reprojection
- Topology repair

### Spatial Analysis

- Overlap detection
- Adjacency detection
- Point-in-polygon
- Spatial joins
- Bounding box queries

### Execution Modes

- Single feature operations
- Batch operations
- Large dataset workflows
- Asynchronous execution for heavy tasks (via Celery workers)

---

## Query and Analysis

Users can:

- Search by metadata
- Filter by attributes
- Query by spatial intersection
- Inspect polygon metrics (area, perimeter, derived properties)
- Compare layers
- Export subsets
- Run spatial analysis operations
- Navigate the globe (Google Earth-style exploration)

---

## Export

Supported export formats (same as ingestion):

- GeoParquet
- GeoJSON
- Shapefile
- WKT

Users can export:

- Full datasets
- Current filtered view
- Selected spatial region
- Analysis results

---

## API Design

### GraphQL (all data operations)

- **Mutations**: dataset upload, validate, reproject, simplify, intersect, export, delete
- **Queries**: dataset metadata, paginated features with spatial/attribute filters, job status, spatial intersection queries
- **Subscriptions** (future): job progress, live processing updates

### REST (tile serving only)

- `GET /{layer}/{z}/{x}/{y}` — binary MVT tiles served by Martin from PostGIS

> See [ARCHITECTURE.md](ARCHITECTURE.md) for full API and stack details.

---

## Visualization

### Map Interactions

- Pan and zoom
- Layer toggling
- Attribute-based styling
- Hover and click inspection
- Polygon highlighting
- Filtering
- Legend rendering
- Coordinate display
- Synchronized attribute table
- Multi-layer overlays

### Multi-Scale Rendering

#### High Zoom (Detail Mode)
- Full polygon geometry with 3m resolution boundaries
- Feature-level inspection with full metadata
- Precise selection

#### Medium Zoom (Simplified Mode)
- Simplified geometries with reduced vertex count
- Clustering or grouping where appropriate

#### Low Zoom (Aggregate Mode)
- Aggregated statistics (e.g., acreage totals)
- Heatmaps or choropleths
- Vector tiles instead of raw features

### Performance Strategies

- Vector tiling via Martin (CDN-cached)
- Viewport-based loading (fetch only visible features)
- Zoom-based geometry simplification
- Progressive rendering (load incrementally, refine on zoom)
- Redis caching of expensive query results

### Visual Consistency

- Consistent styling across zoom levels
- Stable feature identity across transformations
- Predictable color mapping for attributes

### Feedback and Transparency

Users should always understand:

- What data is currently shown
- What filters are applied
- What transformations are active
- Whether data is aggregated or raw

---

## User Workflows

### 1. Dataset Exploration

- Load one or more datasets
- Toggle layers on and off
- Zoom from national to field-level views
- Pan across the map seamlessly
- Inspect dataset metadata

### 2. Ad-Hoc Spatial Analysis

- Draw a region on the map and analyze intersecting polygons
- Filter features by attribute (e.g., crop type, year)
- Dynamically update results as filters change
- Compare datasets visually via overlay
- Isolate subsets of interest

All analysis operations should feel immediate or near real-time where possible.

### 3. Feature Inspection

On click or hover, display:

- Feature ID
- Attributes (e.g., crop history)
- Computed metrics (area, perimeter)
- Derived insights (classification, tags)

### 4. Filtering and Querying

- Filter by attribute values (e.g., crop = corn)
- Filter by time (e.g., year = 2022)
- Filter by spatial region (viewport or drawn polygon)
- Combine filters dynamically
- Server-side filtering for large datasets
- Incremental visualization updates

### 5. Derived Analysis Views

Switch between visualization modes:

- Raw polygon view
- Boundary-only view
- Choropleth (e.g., acreage by region)
- Heatmap (density of features or attributes)
- Clustered view (for large datasets)

### 6. Comparison Workflows

- Overlay multiple datasets
- Compare attributes across layers
- Visualize differences (e.g., year-over-year changes)
- Quick layer visibility toggling

---

## Use Case: USDA Crop Sequence Boundaries (CSB)

The USDA NASS Crop Sequence Boundaries dataset serves as the primary real-world validation dataset.

Reference: https://www.nass.usda.gov/Research_and_Science/Crop-Sequence-Boundaries/index.php

### Dataset Characteristics

- Millions of polygon features (field boundaries)
- Multi-year crop sequence attributes
- Delivered as Shapefile or geodatabase
- Typically NAD83 or WGS84 CRS

### Objectives

- Validate the ingestion pipeline against large real-world data
- Support temporal agricultural data analysis
- Enable visualization of crop history and patterns
- Stress-test performance and scaling

### CSB Ingestion Pipeline

- Securely download and unpack dataset
- Detect and parse format
- Extract geometry, crop sequence attributes, and metadata
- Normalize CRS
- Validate geometry and repair topology where safe
- Store in PostGIS with spatial index

Requirements: chunked ingestion, streaming parsing, memory-safe handling, full provenance preservation.

### Data Model Extensions

Extend SpatialFeature with:

| Field | Description |
|---|---|
| crop_sequence | Ordered list of crops by year |
| primary_crop | Dominant crop type |
| acreage | Computed area in acres |
| year_range | Temporal coverage |
| classification_tags | Derived classification labels |

### CSB-Specific Processing

- Acreage aggregation by crop
- Temporal filtering
- Crop rotation detection
- Clustering by sequence
- Regional aggregation
- Intersection with external boundaries

### CSB Visualization

- Polygon rendering of fields
- Styling by crop, year, or rotation pattern
- Temporal slider for year-based exploration
- Animation of crop transitions
- Choropleth and heatmap views
- Click inspection (crop history, acreage)
- Filtering by crop or sequence

### Temporal Exploration

- Select a specific year
- Scrub through a timeline
- Animate changes over time
- Compare two time periods side-by-side

### Example Scenarios

**Agricultural analysis:** User zooms into a county, filters for "corn in 2022", views matching fields, clicks a field to inspect crop history and acreage.

**Multi-year comparison:** User selects 2020 and 2023, compares crop distribution changes via choropleth overlay.

**Regional aggregation:** User zooms to state level, sees total acreage by crop type as aggregated regions.

**Ad-hoc region analysis:** User draws a polygon over a custom area and requests total acreage, crop distribution, and dominant crop patterns.

---

## Milestones

### Phase 1 — Foundation

- Project scaffold (monorepo, Docker Compose, CI)
- GeoJSON ingestion pipeline
- Canonical data model in PostGIS
- Basic geometry validation
- Map rendering with MapLibre

### Phase 2 — Core Platform

- Full PostGIS integration with spatial indexing
- CRS reprojection
- Geometry simplification
- Attribute filtering and spatial queries
- Export to all supported formats

### Phase 3 — Scale and Analysis

- CSB dataset ingestion and processing
- Large dataset handling (streaming, chunked ingestion)
- Vector tile serving via Martin
- Background processing via Celery
- Advanced spatial analysis and temporal exploration

---

## Definition of Done

### Core Platform
- Dataset ingestion works for real GIS data in all supported formats
- Geometry validation is reliable with explicit, traceable repairs
- Polygons render correctly on map at all zoom levels
- Spatial queries function correctly
- Large datasets remain usable via tiling and aggregation
- Processing is traceable and auditable

### User Experience
- Users can smoothly zoom and pan across datasets
- Visualization adapts correctly to scale
- Filtering updates results dynamically
- Feature inspection is accurate and responsive
- Ad-hoc spatial analysis is intuitive and performant

### CSB Validation
- CSB dataset fully ingested and indexed
- Temporal exploration works interactively
- CSB-specific visualization and analysis functional
