import httpx
import asyncio
from typing import Optional, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class GeocodingService:
    """Service for geocoding addresses to get latitude and longitude coordinates"""

    def __init__(self):
        self.nominatim_base_url = "https://nominatim.openstreetmap.org"
        self.headers = {
            "User-Agent": "BiteWise-Merchant-Service/1.0"  # Required by Nominatim
        }

    async def geocode_address(self, address: str, city: str = None, state: str = None,
                            country: str = None, postal_code: str = None) -> Optional[Tuple[float, float]]:
        """
        Geocode an address to get latitude and longitude coordinates

        Args:
            address: Street address
            city: City name
            state: State/Province name
            country: Country name
            postal_code: Postal/ZIP code

        Returns:
            Tuple of (latitude, longitude) if found, None otherwise
        """
        try:
            # Build the full address string
            full_address = self._build_address_string(address, city, state, country, postal_code)

            if not full_address.strip():
                logger.warning("Empty address provided for geocoding")
                return None

            # Prepare the query parameters
            params = {
                "q": full_address,
                "format": "json",
                "limit": 1,
                "addressdetails": 1
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.nominatim_base_url}/search",
                    params=params,
                    headers=self.headers,
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()

                    if data and len(data) > 0:
                        result = data[0]
                        lat = float(result.get("lat", 0))
                        lon = float(result.get("lon", 0))

                        if lat != 0 and lon != 0:
                            logger.info(f"Successfully geocoded address: {full_address} -> ({lat}, {lon})")
                            return (lat, lon)
                        else:
                            logger.warning(f"Invalid coordinates returned for address: {full_address}")
                            return None
                    else:
                        logger.warning(f"No results found for address: {full_address}")
                        return None
                else:
                    logger.error(f"Geocoding API error: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Error geocoding address '{full_address}': {str(e)}")
            return None

    def _build_address_string(self, address: str, city: str = None, state: str = None,
                            country: str = None, postal_code: str = None) -> str:
        """Build a complete address string from components"""
        address_parts = []

        if address:
            address_parts.append(address.strip())
        if city:
            address_parts.append(city.strip())
        if state:
            address_parts.append(state.strip())
        if postal_code:
            address_parts.append(postal_code.strip())
        if country:
            address_parts.append(country.strip())

        return ", ".join(address_parts)

    async def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Reverse geocode coordinates to get address information

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Dictionary with address information if found, None otherwise
        """
        try:
            params = {
                "lat": latitude,
                "lon": longitude,
                "format": "json",
                "addressdetails": 1
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.nominatim_base_url}/reverse",
                    params=params,
                    headers=self.headers,
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    if data and "address" in data:
                        logger.info(f"Successfully reverse geocoded coordinates: ({latitude}, {longitude})")
                        return data
                    else:
                        logger.warning(f"No address found for coordinates: ({latitude}, {longitude})")
                        return None
                else:
                    logger.error(f"Reverse geocoding API error: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Error reverse geocoding coordinates ({latitude}, {longitude}): {str(e)}")
            return None

# Create a singleton instance
geocoding_service = GeocodingService()

