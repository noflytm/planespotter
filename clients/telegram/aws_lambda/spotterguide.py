"""
Global SpotterGuide.net Integration Engine for PlaneSpotter Bot.
Provides spotting locations, runway views, focal lengths, sun positions,
and Google Maps navigation links for 770+ airports worldwide.
"""

import json
import os
import re
import urllib.request

# Load index if available
INDEX_PATH = os.path.join(os.path.dirname(__file__), "spotterguide_index.json")
_GUIDE_INDEX = {}
if os.path.exists(INDEX_PATH):
    try:
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            _GUIDE_INDEX = json.load(f)
    except Exception as e:
        print(f"Failed to load spotterguide_index.json: {e}")

# Detailed, curated spot coordinates and parameters for top airports
CURATED_SPOTS = {
    "EPGD": [
        {
            "id": "gdn_1",
            "name": "Kosmonautów Hill (Kosmonautów Street)",
            "lat": 54.3725,
            "lon": 18.4735,
            "lens": "70-200mm (Full Frame) / 50-150mm (APS-C)",
            "sun": "Afternoon until sunset (best light after 13:00)",
            "ladder": "Not required (natural hill elevation over fence)",
            "what": "Takeoffs and landings on RWY 29/11, taxiing, full apron view",
            "parking": "Free parking along Kosmonautów street",
            "gmaps": "https://www.google.com/maps/dir/?api=1&destination=54.3725,18.4735"
        },
        {
            "id": "gdn_2",
            "name": "Szybowcowa Spot (Threshold RWY 29)",
            "lat": 54.3670,
            "lon": 18.4890,
            "lens": "24-70mm (wide angle) or 70-200mm",
            "sun": "Morning, sunset, and night spotting",
            "ladder": "Helpful 2-3 steps or shoot through fence mesh",
            "what": "Touchdown zone, low flyover overhead on RWY 29 approach",
            "parking": "Near the forest strip on Szybowcowa street",
            "gmaps": "https://www.google.com/maps/dir/?api=1&destination=54.3670,18.4890"
        },
        {
            "id": "gdn_3",
            "name": "Bysewo Hill (Bysewska Street)",
            "lat": 54.3820,
            "lon": 18.4500,
            "lens": "100-400mm",
            "sun": "Morning and early afternoon (until 14:00)",
            "ladder": "Raised observation terrace with handrails",
            "what": "Landings and departures on RWY 11, line-up on runway",
            "parking": "Parking at the Bysewo bus loop",
            "gmaps": "https://www.google.com/maps/dir/?api=1&destination=54.3820,18.4500"
        }
    ],
    "EPWA": [
        {
            "id": "waw_1",
            "name": "Al. Krakowska Spotters Hill (RWY 15/33)",
            "lat": 52.1795,
            "lon": 20.9450,
            "lens": "70-200mm / 100-400mm",
            "sun": "Afternoon",
            "ladder": "Artificial hill, ladder not needed",
            "what": "Takeoff and landing RWY 15/33, terminal and LOT hangars view",
            "parking": "Hypermarket parking or roadside",
            "gmaps": "https://www.google.com/maps/dir/?api=1&destination=52.1795,20.9450"
        },
        {
            "id": "waw_2",
            "name": "Paluch Hill (RWY 29/11)",
            "lat": 52.1640,
            "lon": 20.9850,
            "lens": "70-300mm",
            "sun": "Morning until noon",
            "ladder": "Artificial mound",
            "what": "Touchdowns on RWY 29, takeoffs from RWY 11",
            "parking": "Near Paluch street",
            "gmaps": "https://www.google.com/maps/dir/?api=1&destination=52.1640,20.9850"
        }
    ],
    "EPKK": [
        {
            "id": "krk_1",
            "name": "Balice Spotting Platform (RWY 25)",
            "lat": 50.0760,
            "lon": 19.8050,
            "lens": "70-200mm",
            "sun": "Afternoon",
            "ladder": "Wooden viewing platform",
            "what": "Final approach RWY 25, view of 8BLTr military ramp",
            "parking": "Roadside near Balice",
            "gmaps": "https://www.google.com/maps/dir/?api=1&destination=50.0760,19.8050"
        }
    ],
    "KJFK": [
        {
            "id": "jfk_1",
            "name": "Costco / Rockaway Blvd (RWY 31L/31R & 4L)",
            "lat": 40.6610,
            "lon": -73.7480,
            "lens": "70-200mm",
            "sun": "Afternoon",
            "ladder": "Not required",
            "what": "Heavy long-haul widebodies (A380, B777, B747) on short final",
            "parking": "Shopping mall parking",
            "gmaps": "https://www.google.com/maps/dir/?api=1&destination=40.6610,-73.7480"
        },
        {
            "id": "jfk_2",
            "name": "TWA Hotel Observation Deck",
            "lat": 40.6450,
            "lon": -73.7780,
            "lens": "24-105mm / 70-200mm",
            "sun": "All day",
            "ladder": "Hotel rooftop pool terrace",
            "what": "Apron panorama T5, taxiing in front of hotel, iconic retro view",
            "parking": "Terminal T5 parking",
            "gmaps": "https://www.google.com/maps/dir/?api=1&destination=40.6450,-73.7780"
        }
    ],
    "KLAX": [
        {
            "id": "lax_1",
            "name": "In-N-Out Burger (Sepulveda Blvd / RWY 24R)",
            "lat": 33.9535,
            "lon": -118.3965,
            "lens": "24-70mm / 70-200mm",
            "sun": "After 13:00 until sunset",
            "ladder": "Park lawn area",
            "what": "Iconic world spot: widebody jets flying 30m directly overhead!",
            "parking": "In-N-Out parking / street",
            "gmaps": "https://www.google.com/maps/dir/?api=1&destination=33.9535,-118.3965"
        },
        {
            "id": "lax_2",
            "name": "Imperial Hill (Clutter's Park / South Runways 25L/25R)",
            "lat": 33.9310,
            "lon": -118.4130,
            "lens": "100-400mm",
            "sun": "Morning and afternoon",
            "ladder": "Park benches and railing",
            "what": "High overview of south runway complex, Pacific Ocean climb-outs",
            "parking": "Park parking lot",
            "gmaps": "https://www.google.com/maps/dir/?api=1&destination=33.9310,-118.4130"
        }
    ]
}

def get_spotterguide_slug(airport_code: str) -> str:
    """Returns SpotterGuide.net post slug for any ICAO/IATA code."""
    if not airport_code:
        return ""
    code = airport_code.upper().strip()
    return _GUIDE_INDEX.get(code, "")


def get_spotterguide_url(airport_code: str) -> str:
    """Returns official SpotterGuide.net guide URL for any airport in the world."""
    slug = get_spotterguide_slug(airport_code)
    if slug:
        return f"https://www.spotterguide.net/planespotting/{slug}/"
    return f"https://www.spotterguide.net/?s={airport_code.upper().strip()}"


def get_spots_for_airport(airport_code: str, lang: str = "en") -> list:
    """
    Returns spotting spots for airport (curated list if available,
    or dynamically fetched from SpotterGuide WordPress API).
    """
    if not airport_code:
        return []
    code = airport_code.upper().strip()
    if code in CURATED_SPOTS:
        return CURATED_SPOTS[code]

    # Check ICAO match in curated
    for icao_key, spots in CURATED_SPOTS.items():
        if code == icao_key:
            return spots

    # Otherwise return general guide link and metadata
    slug = get_spotterguide_slug(code)
    if not slug:
        return []

    lens_desc = "70-300mm (recommended versatile zoom)" if lang == "en" else ("70-300mm (zalecany uniwersalny zoom)" if lang == "pl" else "70-300mm (рекомендуемый универсальный зум)")
    sun_desc = "Depends on time of day and active runway" if lang == "en" else ("Zależnie od pory dnia i kierunku pasa" if lang == "pl" else "Зависит от времени суток и направления ВПП")
    ladder_desc = "See details in official guide" if lang == "en" else ("Zobacz szczegóły w oficjalnym przewodniku" if lang == "pl" else "Смотрите подробности в официальном гайде")
    what_desc = "Takeoffs, landings and apron operations" if lang == "en" else ("Starty, lądowania i operacje na płycie" if lang == "pl" else "Взлёты, посадки и перрон")

    return [
        {
            "id": f"sg_{code.lower()}_guide",
            "name": f"SpotterGuide.net: {code} Official Guide",
            "lat": None,
            "lon": None,
            "lens": lens_desc,
            "sun": sun_desc,
            "ladder": ladder_desc,
            "what": what_desc,
            "web_url": f"https://www.spotterguide.net/planespotting/{slug}/",
            "gmaps": ""
        }
    ]
