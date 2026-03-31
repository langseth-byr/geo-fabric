# GeoFabric

GeoFabric is a geospatial web application for uploading polygon datasets,
validating them, storing them in PostGIS, and visualizing them on a map.

## Current Direction

The project is intentionally scoped to a practical V1:

1. Upload a dataset
2. Parse polygon features safely
3. Normalize CRS to EPSG:4326
4. Validate geometry and record issues
5. Store the dataset in PostGIS
6. Render the dataset in a web map
7. Inspect features and apply basic filters

## V1 Stack

- React + TypeScript + Vite + MapLibre
- FastAPI + Pydantic + SQLAlchemy
- PostgreSQL + PostGIS
- Shapely, pyproj, and Fiona for geospatial handling

## Docs

- [INITIAL-PLAN.md](INITIAL-PLAN.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [CODING-CONVENTIONS.md](CODING-CONVENTIONS.md)
- [REQUIREMENT-TEMPLATE.md](REQUIREMENT-TEMPLATE.md)
- [CLAUDE.md](CLAUDE.md)
