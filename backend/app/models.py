"""Canonical spatial data models for GeoFabric.

Three tables:
- datasets: metadata about an uploaded geospatial file
- spatial_features: individual geometry features belonging to a dataset
- processing_jobs: audit trail for operations run against a dataset
"""

import uuid
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

INGESTION_STATUSES = ("pending", "processing", "complete", "failed")
VALIDATION_STATUSES = ("valid", "repaired", "invalid", "pending")
JOB_STATUSES = ("pending", "running", "complete", "failed")
GEOMETRY_TYPES = ("Polygon", "MultiPolygon")


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_format: Mapped[str] = mapped_column(String(50), nullable=False)
    source_file_uri: Mapped[str] = mapped_column(Text, nullable=False)
    declared_crs: Mapped[str | None] = mapped_column(String(50))
    normalized_crs: Mapped[str] = mapped_column(
        String(50), nullable=False, default="EPSG:4326"
    )
    feature_count: Mapped[int] = mapped_column(Integer, default=0)
    extent: Mapped[dict | None] = mapped_column(JSONB)
    ingestion_status: Mapped[str] = mapped_column(
        Enum(*INGESTION_STATUSES, name="ingestion_status_enum"),
        nullable=False,
        default="pending",
    )
    validation_summary: Mapped[dict | None] = mapped_column(JSONB)
    processing_history: Mapped[list | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    features: Mapped[list["SpatialFeature"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan"
    )
    processing_jobs: Mapped[list["ProcessingJob"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "feature_count >= 0", name="ck_datasets_feature_count_non_negative"
        ),
    )


# ---------------------------------------------------------------------------
# SpatialFeature
# ---------------------------------------------------------------------------


class SpatialFeature(Base):
    __tablename__ = "spatial_features"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    geometry_type: Mapped[str] = mapped_column(
        Enum(*GEOMETRY_TYPES, name="geometry_type_enum"), nullable=False
    )
    raw_geometry: Mapped[str | None] = mapped_column(
        Geometry(geometry_type="GEOMETRY", srid=0, spatial_index=False)
    )
    normalized_geometry: Mapped[str] = mapped_column(
        Geometry(geometry_type="GEOMETRY", srid=4326), nullable=False
    )
    bbox: Mapped[dict | None] = mapped_column(JSONB)
    centroid: Mapped[dict | None] = mapped_column(JSONB)
    area: Mapped[float | None] = mapped_column(Float)
    perimeter: Mapped[float | None] = mapped_column(Float)
    source_crs: Mapped[str | None] = mapped_column(String(50))
    normalized_crs: Mapped[str] = mapped_column(
        String(50), nullable=False, default="EPSG:4326"
    )
    properties: Mapped[dict | None] = mapped_column(JSONB)
    validation_status: Mapped[str] = mapped_column(
        Enum(*VALIDATION_STATUSES, name="validation_status_enum"),
        nullable=False,
        default="pending",
    )
    validation_errors: Mapped[list | None] = mapped_column(JSONB)
    provenance: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    dataset: Mapped["Dataset"] = relationship(back_populates="features")

    __table_args__ = (
        Index("ix_spatial_features_dataset_id", "dataset_id"),
    )


# ---------------------------------------------------------------------------
# ProcessingJob
# ---------------------------------------------------------------------------


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    operation_type: Mapped[str] = mapped_column(String(100), nullable=False)
    parameters: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(
        Enum(*JOB_STATUSES, name="job_status_enum"),
        nullable=False,
        default="pending",
    )
    result_artifact_uri: Mapped[str | None] = mapped_column(Text)
    error_log: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    dataset: Mapped["Dataset"] = relationship(back_populates="processing_jobs")

    __table_args__ = (
        Index("ix_processing_jobs_dataset_id", "dataset_id"),
    )
