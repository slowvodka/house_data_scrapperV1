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
        url: Direct URL to the listing page.
        scraped_at: Timestamp when the data was extracted.

        # Core property details
        price: Listing price in ILS (None if not available).
        rooms: Number of rooms (can be fractional, e.g., 3.5).
        floor: Floor number (None if not specified).
        sqm: Property size in square meters.
        address: Street address (e.g., "רחוב דיזנגוף 50").
        neighborhood: Neighborhood name within the city.
        asset_type: Type of property (דירה, דירת גן, פנטהאוז, etc.).
        description: Free-text description of the listing.

        # Building information
        total_floors: Total number of floors in the building.
        year_built: Year the building was constructed.
        elevator: Whether the building has an elevator.

        # Property features
        parking: Number of parking spots (0 if none).
        balconies: Number of balconies (0 if none).
        mamad: Whether the property has a safe room (ממ"ד).
        storage_unit: Whether there's a storage unit (מחסן).
        condition: Property condition (חדש, משופץ, שמור, דרוש שיפוץ).

        # Availability
        entrance_date: When the property is available for move-in.
    """

    # Required fields
    city: str
    url: str
    scraped_at: datetime

    # Core property details (optional)
    price: Optional[int] = None
    rooms: Optional[float] = None
    floor: Optional[int] = None
    sqm: Optional[int] = None
    address: Optional[str] = None
    neighborhood: Optional[str] = None
    asset_type: Optional[str] = None
    description: Optional[str] = None

    # Building information (optional)
    total_floors: Optional[int] = None
    year_built: Optional[int] = None
    elevator: Optional[bool] = None

    # Property features (optional)
    parking: Optional[int] = None
    balconies: Optional[int] = None
    mamad: Optional[bool] = None
    storage_unit: Optional[bool] = None
    condition: Optional[str] = None

    # Availability (optional)
    entrance_date: Optional[str] = None
