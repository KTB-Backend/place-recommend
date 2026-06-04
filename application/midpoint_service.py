from __future__ import annotations

from domain.exceptions import InvalidLocationError, NoNearbyStationError
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

    def find_meeting_station_candidates(
        self,
        locations: list[Location],
        limit: int,
    ) -> list[Station]:
        midpoint = self.calculate_midpoint(locations)
        return self._repository.find_nearest_candidates(midpoint, limit)

    def locations_from_station_names(self, station_names: list[str]) -> list[Location]:
        if not station_names:
            raise InvalidLocationError("station_names must not be empty")

        locations: list[Location] = []
        missing: list[str] = []
        for name in station_names:
            station = self._repository.find_by_name(name)
            if station is None:
                missing.append(name)
                continue
            locations.append(Location(lat=station.lat, lng=station.lng))

        if missing:
            raise NoNearbyStationError(f"unknown station names: {', '.join(missing)}")
        return locations
