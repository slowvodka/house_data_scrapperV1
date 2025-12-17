"""
Unit tests for the Exporter Module.

TDD Phase: RED - Writing tests before implementation.
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from src.exporter import ParquetExporter
from src.models import Listing


@pytest.fixture
def sample_listings():
    """Create sample listings for testing."""
    return [
        Listing(
            city="תל אביב",
            url="https://www.yad2.co.il/item/abc123",
            scraped_at=datetime(2025, 12, 12, 10, 30, 0),
            price=2500000,
            rooms=3.5,
            floor=5,
            sqm=85,
            address="דיזנגוף 50",
            neighborhood="הצפון הישן",
            asset_type="דירה",
            description="דירה מרווחת ומוארת",
            total_floors=8,
            year_built=1995,
            elevator=True,
            parking=1,
            balconies=2,
            mamad=True,
            storage_unit=False,
            condition="שמור",
            entrance_date="גמיש",
        ),
        Listing(
            city="תל אביב",
            url="https://www.yad2.co.il/item/def456",
            scraped_at=datetime(2025, 12, 12, 10, 31, 0),
            price=3200000,
            rooms=4.0,
            floor=2,
            sqm=110,
            address="אינשטיין 15",
            neighborhood="רמת אביב",
            asset_type="דירת גן",
            description="דירת גן עם גינה גדולה",
            total_floors=4,
            year_built=2020,
            elevator=True,
            parking=2,
            balconies=1,
            mamad=True,
            storage_unit=True,
            condition="חדש",
            entrance_date="מיידי",
        ),
    ]


@pytest.fixture
def listing_with_missing_fields():
    """Create a listing with some optional fields missing."""
    return Listing(
        city="חיפה",
        url="https://www.yad2.co.il/item/xyz789",
        scraped_at=datetime(2025, 12, 12, 11, 0, 0),
        price=1800000,
        # rooms, floor, sqm, neighborhood, asset_type, description are None
    )


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestParquetExporterConversion:
    """Test DataFrame conversion functionality."""

    def test_listings_convert_to_dataframe(self, sample_listings):
        """Exporter should convert listings to pandas DataFrame."""
        exporter = ParquetExporter()
        df = exporter.to_dataframe(sample_listings)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2

    def test_dataframe_has_correct_columns(self, sample_listings):
        """DataFrame should have all expected columns."""
        exporter = ParquetExporter()
        df = exporter.to_dataframe(sample_listings)

        expected_columns = [
            "city", "url", "scraped_at",
            "price", "rooms", "floor", "sqm", "sqm_build", "address", "area", "neighborhood", 
            "latitude", "longitude", "asset_type", "description", "images",
            "total_floors", "year_built", "elevator",
            "parking", "balconies", "mamad", "storage_unit", "condition",
            "entrance_date"
        ]
        assert list(df.columns) == expected_columns

    def test_dataframe_preserves_hebrew_text(self, sample_listings):
        """DataFrame should correctly preserve Hebrew text."""
        exporter = ParquetExporter()
        df = exporter.to_dataframe(sample_listings)

        assert df.iloc[0]["city"] == "תל אביב"
        assert df.iloc[0]["neighborhood"] == "הצפון הישן"

    def test_dataframe_handles_missing_fields(self, listing_with_missing_fields):
        """DataFrame should handle listings with missing optional fields."""
        exporter = ParquetExporter()
        df = exporter.to_dataframe([listing_with_missing_fields])

        assert len(df) == 1
        assert df.iloc[0]["city"] == "חיפה"
        assert pd.isna(df.iloc[0]["rooms"])
        assert pd.isna(df.iloc[0]["floor"])


class TestParquetExporterSave:
    """Test Parquet file saving functionality."""

    def test_export_creates_parquet_file(self, sample_listings, temp_output_dir):
        """Exporter should create a Parquet file."""
        exporter = ParquetExporter()
        output_path = os.path.join(temp_output_dir, "test_output.parquet")

        exporter.export(sample_listings, output_path)

        assert os.path.exists(output_path)

    def test_exported_parquet_readable(self, sample_listings, temp_output_dir):
        """Exported Parquet file should be readable by pandas."""
        exporter = ParquetExporter()
        output_path = os.path.join(temp_output_dir, "test_output.parquet")

        exporter.export(sample_listings, output_path)
        df_read = pd.read_parquet(output_path)

        assert len(df_read) == 2
        assert df_read.iloc[0]["city"] == "תל אביב"

    def test_export_creates_parent_directories(self, sample_listings, temp_output_dir):
        """Exporter should create parent directories if they don't exist."""
        exporter = ParquetExporter()
        output_path = os.path.join(temp_output_dir, "nested", "dir", "output.parquet")

        exporter.export(sample_listings, output_path)

        assert os.path.exists(output_path)


class TestParquetExporterSchema:
    """Test Parquet schema definition."""

    def test_exported_parquet_has_correct_schema(self, sample_listings, temp_output_dir):
        """Exported Parquet file should have explicitly defined schema."""
        import pyarrow.parquet as pq

        exporter = ParquetExporter()
        output_path = os.path.join(temp_output_dir, "schema_test.parquet")

        exporter.export(sample_listings, output_path)

        # Read schema from file
        parquet_file = pq.read_table(output_path)
        schema = parquet_file.schema

        # Verify key column types
        assert schema.field("price").type == "int64" or str(schema.field("price").type).startswith("int")
        assert schema.field("rooms").type == "double" or str(schema.field("rooms").type).startswith("float")
        assert schema.field("elevator").type == "bool"
        assert str(schema.field("city").type) == "string" or str(schema.field("city").type) == "large_string"

    def test_schema_handles_null_values_correctly(self, temp_output_dir):
        """Schema should properly handle null values in optional fields."""
        import pyarrow.parquet as pq

        exporter = ParquetExporter()
        output_path = os.path.join(temp_output_dir, "nulls_test.parquet")

        # Create listing with many null fields
        listing = Listing(
            city="Test City",
            url="https://test.com",
            scraped_at=datetime.now(),
            # All other fields are None
        )

        exporter.export([listing], output_path)

        # Should be readable without errors
        df = pd.read_parquet(output_path)
        assert len(df) == 1
        assert pd.isna(df.iloc[0]["price"])
        assert pd.isna(df.iloc[0]["elevator"])


class TestParquetExporterEdgeCases:
    """Test edge cases and error handling."""

    def test_export_empty_listings_creates_empty_file(self, temp_output_dir):
        """Exporter should handle empty listings list gracefully."""
        exporter = ParquetExporter()
        output_path = os.path.join(temp_output_dir, "empty_output.parquet")

        exporter.export([], output_path)

        assert os.path.exists(output_path)
        df_read = pd.read_parquet(output_path)
        assert len(df_read) == 0

    def test_export_single_listing(self, temp_output_dir):
        """Exporter should handle a single listing."""
        exporter = ParquetExporter()
        output_path = os.path.join(temp_output_dir, "single_output.parquet")
        single_listing = Listing(
            city="ירושלים",
            url="https://www.yad2.co.il/item/single",
            scraped_at=datetime.now(),
            price=1500000,
        )

        exporter.export([single_listing], output_path)

        df_read = pd.read_parquet(output_path)
        assert len(df_read) == 1
        assert df_read.iloc[0]["city"] == "ירושלים"

