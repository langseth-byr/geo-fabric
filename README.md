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

## Security

All uploaded files and request data are treated as untrusted. The project has a
[threat model](docs/threat-model/THREAT-MODEL-REPORT.md) that was produced
against the full architecture; the V1-relevant findings are integrated into
[ARCHITECTURE.md](ARCHITECTURE.md) and
[CODING-CONVENTIONS.md](CODING-CONVENTIONS.md).

Key V1 security controls:

- Content-based file validation (magic bytes, not extension)
- Upload size limits and streaming uploads
- ZIP archive path traversal and zip bomb protection for Shapefiles
- Native GIS library isolation in subprocesses (GDAL, GEOS, PROJ)
- Parameterized database queries via SQLAlchemy
- PostgreSQL statement timeout for expensive spatial queries
- Per-IP rate limiting
- CORS, CSP, and security headers
- GeoJSON property sanitization to prevent stored XSS
- Structured audit logging (no credentials, PII, or internal paths)
- Dependency vulnerability scanning in CI

Authentication and authorization are deferred until multi-user deployment.

## Docs

- [INITIAL-PLAN.md](INITIAL-PLAN.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [CODING-CONVENTIONS.md](CODING-CONVENTIONS.md)
- [REQUIREMENT-TEMPLATE.md](REQUIREMENT-TEMPLATE.md)
- [Threat Model](docs/threat-model/THREAT-MODEL-REPORT.md)
- [CLAUDE.md](CLAUDE.md)
