from __future__ import annotations

from domain.exceptions import InvalidLocationError
from domain.interfaces import StationRepository
from domain.models import Location, Station


class MidpointService:
    def __init__(self, repository: StationRepository) -> None:
        self._repository = repository

    def calculate_midpoint(self, locations: list[Location]) -> Location:
        if not locations:
            raise InvalidLocationError("locations must not be empty")
        lat = sum(loc.lat for loc in locations) / len(locations)
        lng = sum(loc.lng for loc in locations) / len(locations)
        return Location(lat=lat, lng=lng)

    def find_meeting_station(self, locations: list[Location]) -> Station:
        midpoint = self.calculate_midpoint(locations)
        return self._repository.find_nearest(midpoint)
