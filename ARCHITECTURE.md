# GeoFabric — Tech Stack

## Frontend
- **React** + **TypeScript**
- **MapLibre GL JS** (primary map renderer) or OpenLayers
- Optional **deck.gl** for advanced rendering

## Backend API
- **FastAPI** (Python) or **Node.js** (TypeScript) — TBD in Phase 1
- **GDAL/OGR** for GIS format handling
- **Shapely/GeoPandas** (Python) or **Turf/JSTS** (Node) for spatial operations
- **PostGIS** for spatial storage and queries

## Storage
- **Object storage** for raw uploaded files
- **PostGIS** (PostgreSQL + PostGIS extension) for normalized spatial data
- **Redis** for caching and job state

## Processing Workers
- Dedicated background workers for:
  - Reprojection
  - Topology repair
  - Overlay operations (union, intersection, difference)
  - Geometry simplification
  - Vector tile generation
  - Batch exports

## Ingestion Formats
- GeoParquet
- GeoJSON
- Shapefile
- WKT
