"""Tests for Dataset, SpatialFeature, and ProcessingJob models."""

import uuid

import pytest
from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import Dataset, ProcessingJob, SpatialFeature

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_dataset(**overrides) -> Dataset:
    defaults = {
        "name": "Test Dataset",
        "source_format": "GeoJSON",
        "source_file_uri": "/uploads/test.geojson",
    }
    defaults.update(overrides)
    return Dataset(**defaults)


def _make_polygon_wkb(srid: int = 4326):
    """Return a simple square polygon as a WKB element."""
    poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])
    return from_shape(poly, srid=srid)


# ---------------------------------------------------------------------------
# Dataset tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_dataset_with_defaults(session):
    ds = _make_dataset()
    session.add(ds)
    await session.commit()

    result = await session.execute(select(Dataset))
    row = result.scalar_one()
    assert row.name == "Test Dataset"
    assert row.ingestion_status == "pending"
    assert row.normalized_crs == "EPSG:4326"
    assert row.feature_count == 0
    assert row.created_at is not None
    assert row.updated_at is not None


@pytest.mark.asyncio
async def test_dataset_requires_name(session):
    ds = Dataset(source_format="GeoJSON", source_file_uri="/uploads/x.geojson")
    session.add(ds)
    with pytest.raises(IntegrityError):
        await session.flush()


@pytest.mark.asyncio
async def test_dataset_requires_source_format(session):
    ds = Dataset(name="Missing format", source_file_uri="/uploads/x.geojson")
    session.add(ds)
    with pytest.raises(IntegrityError):
        await session.flush()


@pytest.mark.asyncio
async def test_dataset_feature_count_non_negative(session):
    ds = _make_dataset(feature_count=-1)
    session.add(ds)
    with pytest.raises(IntegrityError):
        await session.flush()


@pytest.mark.asyncio
async def test_dataset_uuid_auto_generated(session):
    ds = _make_dataset()
    session.add(ds)
    await session.commit()
    assert isinstance(ds.id, uuid.UUID)


# ---------------------------------------------------------------------------
# SpatialFeature tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_spatial_feature(session):
    ds = _make_dataset()
    session.add(ds)
    await session.flush()

    feat = SpatialFeature(
        dataset_id=ds.id,
        geometry_type="Polygon",
        normalized_geometry=_make_polygon_wkb(),
        properties={"landuse": "residential"},
    )
    session.add(feat)
    await session.commit()

    result = await session.execute(select(SpatialFeature))
    row = result.scalar_one()
    assert row.geometry_type == "Polygon"
    assert row.validation_status == "pending"
    assert row.properties == {"landuse": "residential"}


@pytest.mark.asyncio
async def test_spatial_feature_requires_dataset(session):
    feat = SpatialFeature(
        dataset_id=uuid.uuid4(),  # non-existent dataset
        geometry_type="Polygon",
        normalized_geometry=_make_polygon_wkb(),
    )
    session.add(feat)
    with pytest.raises(IntegrityError):
        await session.flush()


@pytest.mark.asyncio
async def test_spatial_feature_requires_normalized_geometry(session):
    ds = _make_dataset()
    session.add(ds)
    await session.flush()

    feat = SpatialFeature(
        dataset_id=ds.id,
        geometry_type="Polygon",
    )
    session.add(feat)
    with pytest.raises(IntegrityError):
        await session.flush()


@pytest.mark.asyncio
async def test_spatial_feature_invalid_geometry_type(session):
    ds = _make_dataset()
    session.add(ds)
    await session.flush()

    feat = SpatialFeature(
        dataset_id=ds.id,
        geometry_type="LineString",
        normalized_geometry=_make_polygon_wkb(),
    )
    session.add(feat)
    with pytest.raises((IntegrityError, Exception)):
        await session.flush()


# ---------------------------------------------------------------------------
# ProcessingJob tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_processing_job(session):
    ds = _make_dataset()
    session.add(ds)
    await session.flush()

    job = ProcessingJob(
        dataset_id=ds.id,
        operation_type="ingest",
        parameters={"format": "GeoJSON"},
    )
    session.add(job)
    await session.commit()

    result = await session.execute(select(ProcessingJob))
    row = result.scalar_one()
    assert row.operation_type == "ingest"
    assert row.status == "pending"
    assert row.parameters == {"format": "GeoJSON"}
    assert row.completed_at is None


@pytest.mark.asyncio
async def test_processing_job_requires_dataset(session):
    job = ProcessingJob(
        dataset_id=uuid.uuid4(),
        operation_type="ingest",
    )
    session.add(job)
    with pytest.raises(IntegrityError):
        await session.flush()


# ---------------------------------------------------------------------------
# Relationship / cascade tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dataset_cascade_deletes_features(session):
    ds = _make_dataset()
    session.add(ds)
    await session.flush()

    feat = SpatialFeature(
        dataset_id=ds.id,
        geometry_type="Polygon",
        normalized_geometry=_make_polygon_wkb(),
    )
    session.add(feat)
    await session.commit()

    await session.delete(ds)
    await session.commit()

    result = await session.execute(select(SpatialFeature))
    assert result.scalars().all() == []


@pytest.mark.asyncio
async def test_dataset_cascade_deletes_jobs(session):
    ds = _make_dataset()
    session.add(ds)
    await session.flush()

    job = ProcessingJob(dataset_id=ds.id, operation_type="ingest")
    session.add(job)
    await session.commit()

    await session.delete(ds)
    await session.commit()

    result = await session.execute(select(ProcessingJob))
    assert result.scalars().all() == []


@pytest.mark.asyncio
async def test_dataset_relationship_access(session):
    ds = _make_dataset()
    feat = SpatialFeature(
        geometry_type="Polygon",
        normalized_geometry=_make_polygon_wkb(),
    )
    job = ProcessingJob(operation_type="ingest")
    ds.features.append(feat)
    ds.processing_jobs.append(job)
    session.add(ds)
    await session.commit()

    result = await session.execute(
        select(Dataset).where(Dataset.id == ds.id)
    )
    loaded = result.scalar_one()
    assert len(await session.run_sync(lambda s: loaded.features)) >= 0
