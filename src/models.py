"""
Data models for the Yad2 Real Estate Scraper.

Contains dataclasses representing the structured data extracted from listings.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Listing:
    """
    Represents a single real estate listing from yad2.

    Attributes:
        city: The city where the property is located.
        price: Listing price in ILS (None if not available).
        rooms: Number of rooms (can be fractional, e.g., 3.5).
        floor: Floor number (None if not specified).
        sqm: Property size in square meters.
        neighborhood: Neighborhood name within the city.
        asset_type: Type of property (apartment, house, penthouse, etc.).
        description: Free-text description of the listing.
        url: Direct URL to the listing page.
        scraped_at: Timestamp when the data was extracted.
    """

    city: str
    url: str
    scraped_at: datetime
    price: Optional[int] = None
    rooms: Optional[float] = None
    floor: Optional[int] = None
    sqm: Optional[int] = None
    neighborhood: Optional[str] = None
    asset_type: Optional[str] = None
    description: Optional[str] = None

