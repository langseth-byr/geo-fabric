# GeoFabric - Geospatial Polygon Processing and Visualization Platform

## Project Overview

Full-stack geospatial platform for ingesting, validating, processing, analyzing, and visualizing polygon-based GIS datasets at scale. Focuses on vector polygon data (administrative boundaries, parcels, agricultural fields, zoning regions, custom overlays).

## Architecture

### Frontend
- React + TypeScript
- MapLibre GL JS (primary) or OpenLayers
- Optional deck.gl for advanced rendering

### Backend API
- FastAPI (Python) or Node.js (TypeScript) — TBD in Phase 1
- GDAL/OGR for format handling
- Shapely/GeoPandas (Python) or Turf/JSTS (Node) for spatial ops
- PostGIS for spatial storage and queries

### Storage
- Object storage for raw files
- PostGIS for normalized spatial data
- Redis for caching and job state

### Processing
- Dedicated workers for reprojection, topology repair, overlay ops, simplification, tile generation, batch exports

## Canonical Data Model

### SpatialFeature
Core entity: id, dataset_id, geometry_type, raw_geometry, normalized_geometry, bbox, centroid, area, perimeter, source_crs, normalized_crs, properties, validation_status, validation_errors, provenance, timestamps.

### Dataset
Container: id, name, source_format, source_file_uri, declared_crs, normalized_crs, feature_count, extent, ingestion_status, validation_summary, processing_history, timestamps.

### ProcessingJob
Async task: id, dataset_id, operation_type, parameters, status, result_artifact_uri, error_log, timestamps.

## Ingestion Formats
- GeoParquet, GeoJSON, Shapefile, WKT
- Content-based type detection (not extension)
- CRS normalization, geometry validation, provenance preservation

## Key Use Case: USDA Crop Sequence Boundaries (CSB)
- Millions of agricultural field polygons with multi-year crop sequence data
- Extended model: crop_sequence, primary_crop, acreage, year_range, classification_tags
- Temporal exploration, crop rotation analysis, regional aggregation

## API Endpoints
- POST /datasets/upload
- GET /datasets/:id
- GET /datasets/:id/features
- POST /datasets/:id/validate
- POST /datasets/:id/reproject
- POST /datasets/:id/simplify
- POST /datasets/:id/intersect
- POST /datasets/:id/export
- GET /jobs/:id
- GET /tiles/:layer/:z/:x/:y

## Security Requirements
All inputs are untrusted:
- Validate file content, not just extension
- Enforce size limits
- Safely parse GIS formats (isolate native tooling)
- Prevent path traversal during extraction
- Constrain long-running operations
- Parameterized database queries
- No shell execution with user input
- Safe logging (no internal leaks)

## Development Principles
- Preserve raw data always
- Make transformations explicit and traceable
- Correctness over performance initially
- Fail safely on ambiguity
- Separate processing from rendering
- Design for extensibility
- All AI-generated code must be test-gated

## Testing Strategy
- Geometry parsing, CRS transformation, topology repair tests
- API contract tests
- Large dataset performance tests
- Rendering smoke tests
- Regression tests with malformed inputs
- Test fixtures: valid polygons, multipolygons, holes, invalid geometries, mixed CRS, large datasets

## Phases
1. **Phase 1**: Project scaffold, GeoJSON ingestion, canonical model, basic validation, map rendering
2. **Phase 2**: PostGIS integration, reprojection, simplification, filtering, export
3. **Phase 3**: CSB dataset ingestion, large dataset handling, vector tiles, background processing, advanced analysis
