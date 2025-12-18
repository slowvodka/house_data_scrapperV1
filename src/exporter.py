"""
Exporter module for the Yad2 Real Estate Scraper.

Handles conversion of Listing objects to pandas DataFrames
and export to Parquet format with explicit schema definition.
"""

from dataclasses import asdict, fields
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from src.models import Listing


# Explicit PyArrow schema for Parquet files
# This ensures consistent types across all exports and enables proper null handling
LISTING_SCHEMA = pa.schema([
    # Required fields
    ("city", pa.string()),
    ("url", pa.string()),
    ("scraped_at", pa.timestamp("us")),  # microsecond precision

    # Core property details (nullable)
    ("price", pa.int64()),
    ("rooms", pa.float64()),
    ("floor", pa.int32()),
    ("sqm", pa.int32()),
    ("sqm_build", pa.int32()),
    ("address", pa.string()),
    ("area", pa.string()),
    ("neighborhood", pa.string()),
    ("latitude", pa.float64()),
    ("longitude", pa.float64()),
    ("asset_type", pa.string()),
    ("description", pa.string()),
    ("images", pa.list_(pa.string())),

    # Building information (nullable)
    ("total_floors", pa.int32()),
    ("year_built", pa.int32()),
    ("elevator", pa.bool_()),

    # Property features (nullable)
    ("parking", pa.int32()),
    ("balconies", pa.int32()),
    ("mamad", pa.bool_()),
    ("storage_unit", pa.bool_()),
    ("condition", pa.string()),

    # Availability (nullable)
    ("entrance_date", pa.string()),
])


class ParquetExporter:
    """
    Exports listing data to Parquet format with explicit schema.

    Provides methods to convert Listing dataclass instances to pandas
    DataFrames and save them as Parquet files for efficient analytics.
    Uses a predefined schema to ensure type consistency across files.
    """

    def __init__(self):
        """Initialize exporter with the listing schema."""
        self.schema = LISTING_SCHEMA

    def to_dataframe(self, listings: List[Listing]) -> pd.DataFrame:
        """
        Convert a list of Listing objects to a pandas DataFrame.

        Args:
            listings: List of Listing dataclass instances.

        Returns:
            pandas DataFrame with columns matching Listing fields,
            preserving field order from the dataclass definition.
        """
        if not listings:
            # Return empty DataFrame with correct columns
            column_names = [f.name for f in fields(Listing)]
            return pd.DataFrame(columns=column_names)

        # Convert each listing to dict and create DataFrame
        data = [asdict(listing) for listing in listings]
        df = pd.DataFrame(data)

        # Ensure column order matches dataclass field order
        column_order = [f.name for f in fields(Listing)]
        df = df[column_order]

        return df

    def generate_output_path(
        self, base_output_path: str, city_name: str, date: Optional[datetime] = None
    ) -> Path:
        """
        Generate output path in the format: {base_output_path}/{city_name}/{YYYYMMDD}_{city_name}.parquet

        Args:
            base_output_path: Base directory for output files (e.g., "data/output").
            city_name: City name (will be sanitized for filesystem).
            date: Optional datetime object. If None, uses current date.

        Returns:
            Path object pointing to the output file.
        """
        if date is None:
            date = datetime.now()

        # Sanitize city name for filesystem (replace spaces and special chars)
        city_safe = city_name.replace(" ", "_").replace("/", "_")
        date_str = date.strftime("%Y%m%d")

        # Structure: {base_output_path}/{city_name}/{YYYYMMDD}_{city_name}.parquet
        output_path = Path(base_output_path) / city_safe / f"{date_str}_{city_safe}.parquet"

        return output_path

    def export(
        self,
        listings: List[Listing],
        output_path: str,
        city_name: Optional[str] = None,
        base_output_path: Optional[str] = None,
        date: Optional[datetime] = None,
    ) -> Path:
        """
        Export listings to a Parquet file with explicit schema.

        Supports two modes:
        1. Direct path mode: Provide `output_path` directly (backward compatible)
        2. Structured mode: Provide `city_name` and `base_output_path` to generate
           path in format: {base_output_path}/{city_name}/{YYYYMMDD}_{city_name}.parquet

        Args:
            listings: List of Listing dataclass instances to export.
            output_path: Direct path where the Parquet file will be saved.
                        If `city_name` and `base_output_path` are provided, this is ignored.
            city_name: City name for structured output path (optional).
            base_output_path: Base directory for structured output (optional).
            date: Optional datetime object for structured output. If None, uses current date.

        Returns:
            Path object pointing to the created file.
        """
        # Determine output path
        if city_name and base_output_path:
            # Structured mode: generate path
            path = self.generate_output_path(base_output_path, city_name, date)
        else:
            # Direct path mode (backward compatible)
            path = Path(output_path)

        # Ensure parent directories exist
        path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to DataFrame
        df = self.to_dataframe(listings)

        if df.empty:
            # Create empty table with schema for empty DataFrame
            table = pa.Table.from_pandas(df, schema=self.schema, preserve_index=False)
        else:
            # Convert DataFrame to PyArrow Table with explicit schema
            table = pa.Table.from_pandas(df, schema=self.schema, preserve_index=False)

        # Write to Parquet with schema
        pq.write_table(table, str(path))

        return path

    def get_schema(self) -> pa.Schema:
        """
        Get the PyArrow schema used for Parquet exports.

        Returns:
            PyArrow Schema defining column names and types.
        """
        return self.schema
