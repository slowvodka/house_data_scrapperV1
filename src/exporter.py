"""
Exporter module for the Yad2 Real Estate Scraper.

Handles conversion of Listing objects to pandas DataFrames
and export to Parquet format with explicit schema definition.
"""

from dataclasses import asdict, fields
from pathlib import Path
from typing import List

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

    def export(self, listings: List[Listing], output_path: str) -> None:
        """
        Export listings to a Parquet file with explicit schema.

        Args:
            listings: List of Listing dataclass instances to export.
            output_path: Path where the Parquet file will be saved.
                        Parent directories will be created if they don't exist.
        """
        # Ensure parent directories exist
        path = Path(output_path)
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
        pq.write_table(table, output_path)

    def get_schema(self) -> pa.Schema:
        """
        Get the PyArrow schema used for Parquet exports.

        Returns:
            PyArrow Schema defining column names and types.
        """
        return self.schema
