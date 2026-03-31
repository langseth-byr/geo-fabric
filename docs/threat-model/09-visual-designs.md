# GeoFabric Threat Model — Visual Design (PlantUML)

---

## Figure 1: System Context (C4 — Executive View)

```plantuml
@startuml
!include <C4/C4_Context>

title GeoFabric — System Context (Executive View)

Person(user, "End User", "Uploads GIS datasets, views maps, inspects features")
Person(apiClient, "API Consumer", "Programmatic access to GIS data")
System(geofabric, "GeoFabric Platform", "Ingests, validates, stores, and visualizes polygon-based GIS datasets at scale")
System_Ext(cdn, "CDN", "Edge caching for map tiles")

Rel(user, geofabric, "Uploads datasets, queries data, views maps", "HTTPS / GraphQL")
Rel(user, cdn, "Requests map tiles", "HTTPS")
Rel(apiClient, geofabric, "Queries and mutates GIS data", "HTTPS / GraphQL")
Rel(cdn, geofabric, "Forwards cache misses", "HTTP / MVT tiles")

LAYOUT_WITH_LEGEND()
@enduml
```

---

## Figure 2: Container Architecture (C4)

```plantuml
@startuml
!include <C4/C4_Container>

title GeoFabric — Container Architecture

Person(user, "End User", "Browser")
Person(apiClient, "API Consumer", "Programmatic")

System_Boundary(geofabric, "GeoFabric Platform") {
    Container(frontend, "React Frontend", "TypeScript, MapLibre GL JS", "SPA for map visualization and dataset management")
    Container(api, "GraphQL API", "Python 3.12+, FastAPI, Strawberry, Pydantic v2", "All data operations: upload, query, mutate")
    Container(martin, "Martin Tile Server", "Rust 0.15+", "Vector tile serving from PostGIS")
    Container(pgbouncer, "PgBouncer", "1.23+", "Connection pooling")
    ContainerDb(postgis, "PostGIS", "PostgreSQL + PostGIS", "Spatial data: datasets, features, ingestion runs")
    ContainerDb(redis, "Redis", "Redis", "Query cache + Celery broker")
    Container(celery, "Celery Workers", "Python 3.12+, Celery 5.x", "Background: ingestion, spatial ops, exports")
    Container(duckdb, "DuckDB", "DuckDB 1.2+ spatial", "Batch GeoParquet processing (within workers)")
    ContainerDb(objstore, "Object Storage", "S3 / Local", "Raw uploaded files")
}

System_Ext(cdn, "CDN", "CloudFront / Cloudflare")

Rel(user, frontend, "Uses", "HTTPS")
Rel(user, cdn, "Tile requests", "HTTPS")
Rel(apiClient, api, "GraphQL", "HTTPS")
Rel(frontend, api, "GraphQL + uploads", "HTTPS")
Rel(cdn, martin, "Cache miss", "HTTP")
Rel(api, pgbouncer, "SQL", "PostgreSQL protocol")
Rel(martin, pgbouncer, "Tile queries", "PostgreSQL protocol")
Rel(pgbouncer, postgis, "Pooled connections", "PostgreSQL protocol")
Rel(api, redis, "Cache + dispatch", "Redis protocol")
Rel(celery, redis, "Broker", "Redis protocol")
Rel(celery, pgbouncer, "Feature writes", "PostgreSQL protocol")
Rel(api, objstore, "Store raw files", "S3 API")
Rel(celery, objstore, "Read raw files", "S3 API")
Rel_R(celery, duckdb, "Batch processing", "In-process")

LAYOUT_WITH_LEGEND()
@enduml
```

---

## Figure 3: Data Flow — Upload and Ingestion (Sequence)

```plantuml
@startuml
title Dataset Upload and Ingestion Flow

actor "End User" as user
participant "React\nFrontend" as fe
box "Application Zone" #LightBlue
    participant "GraphQL API\n(FastAPI)" as api
end box
box "Data Zone" #LightYellow
    database "Object\nStorage" as obj
    database "PostGIS" as db
    queue "Redis" as redis
end box
box "Processing Zone" #LightGreen
    participant "Celery\nWorker" as worker
    participant "Fiona\n(GDAL)" as gdal
    participant "Shapely\n(GEOS)" as shapely
    participant "pyproj\n(PROJ)" as pyproj
end box

== Upload ==
user -> fe : Select file + name
fe -> api : GraphQL multipart upload
note right of api #Red : !! No authentication !!
api -> api : Validate file size\n(ASGI layer)
api -> api : Validate file content\n(not just extension)
api -> obj : Store raw file
api -> db : Create dataset\n(status: pending)
api -> redis : Dispatch ingestion task
api --> fe : Upload accepted

== Ingestion ==
redis -> worker : Pick up task
worker -> obj : Read raw file
note right of worker #Orange : Untrusted data enters\nnative C/C++ code
worker -> gdal : Parse features
gdal --> worker : Features + properties
worker -> pyproj : Detect CRS
pyproj --> worker : CRS info
worker -> pyproj : Reproject to EPSG:4326
worker -> shapely : Validate geometry
shapely --> worker : Validation results
worker -> db : Write normalized features
worker -> db : Update dataset status

@enduml
```

---

## Figure 4: Threat-Annotated Architecture (C4 — Security View)

```plantuml
@startuml
!include <C4/C4_Container>

title GeoFabric — Threat-Annotated Architecture (Security View)

AddElementTag("critical", $bgColor="#FF0000", $fontColor="white", $borderColor="#CC0000")
AddElementTag("high", $bgColor="#FF6600", $fontColor="white", $borderColor="#CC5500")
AddElementTag("medium", $bgColor="#FFCC00", $fontColor="black", $borderColor="#CC9900")

Person(user, "End User", "Untrusted")
Person(attacker, "Attacker", "Untrusted") #Red

System_Boundary(geofabric, "GeoFabric Platform") {
    Container(frontend, "React Frontend", "MapLibre GL JS", "CT-14: Stored XSS\nCT-16: No CSP/CORS", $tags="high")
    Container(api, "GraphQL API", "FastAPI + Strawberry", "CT-01: No auth (!!!)\nCT-02: No authz (!!!)\nCT-06: No depth limit\nCT-07: No size limit\nCT-09: No rate limit\nCT-15: No audit log\nCT-17: Introspection", $tags="critical")
    Container(martin, "Martin", "Rust", "CT-11: No access control", $tags="high")
    Container(pgbouncer, "PgBouncer", "1.23+", "CT-20: Pool exhaustion", $tags="medium")
    ContainerDb(postgis, "PostGIS", "PostgreSQL", "CT-08: Spatial DoS\nCT-18: No EAR", $tags="high")
    ContainerDb(redis, "Redis", "", "CT-05: No AUTH", $tags="high")
    Container(celery, "Celery Workers", "Python", "CT-03: Native lib exploit\nCT-04: Path traversal\nCT-12: Pickle RCE\nCT-13: Zip bomb\nCT-21: Full DB privs", $tags="high")
    ContainerDb(objstore, "Object Storage", "S3/Local", "CT-18: No EAR", $tags="medium")
}

Rel(user, api, "No auth", "HTTPS")
Rel(attacker, api, "Anonymous access", "HTTPS")
Rel(api, pgbouncer, "No TLS (CT-10)", "")
Rel(martin, pgbouncer, "No TLS (CT-10)", "")
Rel(api, redis, "No TLS, No AUTH", "")
Rel(celery, redis, "Pickle (CT-12)", "")

LAYOUT_WITH_LEGEND()
@enduml
```

---

## Figure 5: Attack Surface Map (PlantUML)

```plantuml
@startuml
title GeoFabric — Attack Surface Map

skinparam rectangle {
    BorderColor Black
    BackgroundColor White
}

rectangle "**EXTERNAL ATTACK SURFACE**" as ext {
    rectangle "GraphQL Mutations\n(upload, delete, reproject, etc.)\n---\nAuth: NONE | Authz: NONE\n**7 threats | CRITICAL**" as mutations #FF0000
    rectangle "GraphQL Queries\n(datasets, features, spatial)\n---\nAuth: NONE | Authz: NONE\n**4 threats | HIGH**" as queries #FF6600
    rectangle "GraphQL Introspection\n(__schema, __type)\n---\nAuth: NONE\n**1 threat | MEDIUM**" as introspection #FFCC00
    rectangle "File Upload (Multipart)\n(GeoJSON, Shapefile ZIP,\nGeoParquet, WKT)\n---\nAuth: NONE | Size: TBD\n**5 threats | CRITICAL**" as upload #FF0000
    rectangle "Tile Endpoint\nGET /{layer}/{z}/{x}/{y}\n(via CDN -> Martin)\n---\nAuth: NONE\n**3 threats | HIGH**" as tiles #FF6600
}

rectangle "**INTERNAL ATTACK SURFACE**" as int {
    rectangle "Redis\n(Cache + Broker)\n---\nAuth: NONE | Net: Internal\n**3 threats | HIGH**" as redis #FF6600
    rectangle "PostgreSQL\n(via PgBouncer)\n---\nAuth: Password (assumed)\n**2 threats | MEDIUM**" as pg #FFCC00
    rectangle "Object Storage\n(Raw files)\n---\nAuth: IAM (assumed)\n**1 threat | MEDIUM**" as obj #FFCC00
}

note bottom of ext
  All external entry points lack authentication.
  File upload is the highest-risk entry point
  (untrusted binary data + no auth).
end note

@enduml
```

---

## Diagram Legend

| Symbol | Meaning |
|---|---|
| Red background (#FF0000) | Critical severity — requires immediate remediation |
| Orange background (#FF6600) | High severity — address before production deployment |
| Yellow background (#FFCC00) | Medium severity — address in short-term roadmap |
| Dashed border | Trust boundary |
| Bold connection label | Sensitive data flow |
| !!! prefix | Critical threat |
| !! prefix | High threat |
| ! prefix | Medium threat |
