"""Source of flight data for the spotting plan and the radar.

The prototype read an unofficial FlightRadar24 endpoint while sending a browser User-Agent. That client is
not part of this repository (terms-of-service risk). The bot depends on this small interface instead.

With no provider configured both functions return an empty list, and the bot shows its normal
"could not fetch the schedule" reply. To plug in a real source (for example open ADS-B data), write a module that
defines the same two functions and set SCHEDULE_PROVIDER=<module name>.

get_airport_schedule(iata) -> list of dicts for the next hour, one per flight:
    mode ("arrivals"/"departures"), reg, model, airline, flight_num, orig, dest,
    time_str, sch_str, delay_min, time_badge, status, is_diverted

get_live_flights_near_airport(lat, lon, airport_iata="", airport_icao="") -> list of dicts:
    reg, model, flight, origin, dest, altitude, vspeed, is_on_ground, flight_mode,
    squawk, is_emergency, is_diverted, is_target_airport
"""

import importlib
import os


def _provider():
    name = os.environ.get("SCHEDULE_PROVIDER", "").strip()
    return importlib.import_module(name) if name else None


def get_airport_schedule(iata_code: str) -> list:
    provider = _provider()
    return provider.get_airport_schedule(iata_code) if provider else []


def get_live_flights_near_airport(lat: float, lon: float, airport_iata: str = "", airport_icao: str = "", **kwargs) -> list:
    provider = _provider()
    if provider:
        return provider.get_live_flights_near_airport(lat, lon, airport_iata=airport_iata, airport_icao=airport_icao, **kwargs)
    return []
