"""
Global Airlines Directory for PlaneSpotter Bot.
Maps ICAO, IATA and Callsigns to official readable airline names with country flags.
"""

AIRLINES_DATA = {
    # Poland & Central Europe
    "LOT": {"iata": "LO", "name": "LOT Polish Airlines", "country": "Польша 🇵🇱", "callsign": "POLLOT"},
    "RYS": {"iata": "RR", "name": "Buzz (Ryanair Sun)", "country": "Польша 🇵🇱", "callsign": "MAGIC SUN"},
    "ENT": {"iata": "E4", "name": "Enter Air", "country": "Польша 🇵🇱", "callsign": "ENTER AIR"},
    "SPR": {"iata": "SR", "name": "SprintAir", "country": "Польша 🇵🇱", "callsign": "AIR REPUBLIK"},
    "WZZ": {"iata": "W6", "name": "Wizz Air", "country": "Венгрия 🇭🇺", "callsign": "WIZZ AIR"},
    "WUK": {"iata": "W9", "name": "Wizz Air UK", "country": "Великобритания 🇬🇧", "callsign": "WIZZ GO"},
    "WAW": {"iata": "W4", "name": "Wizz Air Malta", "country": "Мальта 🇲🇹", "callsign": "WIZZ AIR"},
    "RYR": {"iata": "FR", "name": "Ryanair", "country": "Ирландия 🇮🇪", "callsign": "RYANAIR"},
    "MAY": {"iata": "BF", "name": "Malta Air (Ryanair)", "country": "Мальта 🇲🇹", "callsign": "MALTA AIR"},
    "LID": {"iata": "LD", "name": "Lauda Europe (Ryanair)", "country": "Мальта 🇲🇹", "callsign": "BEAUFORT"},
    "CSA": {"iata": "OK", "name": "Czech Airlines", "country": "Чехия 🇨🇿", "callsign": "CSA-LINES"},
    "TVS": {"iata": "QS", "name": "Smartwings", "country": "Чехия 🇨🇿", "callsign": "SMARTWINGS"},

    # Western Europe & Nordics
    "DLH": {"iata": "LH", "name": "Lufthansa", "country": "Германия 🇩🇪", "callsign": "LUFTHANSA"},
    "DLX": {"iata": "LH", "name": "Lufthansa CityLine", "country": "Германия 🇩🇪", "callsign": "HANSALINE"},
    "EWG": {"iata": "EW", "name": "Eurowings", "country": "Германия 🇩🇪", "callsign": "EUROWINGS"},
    "CFG": {"iata": "DE", "name": "Condor", "country": "Германия 🇩🇪", "callsign": "CONDOR"},
    "AFR": {"iata": "AF", "name": "Air France", "country": "Франция 🇫🇷", "callsign": "AIRFRANS"},
    "KLM": {"iata": "KL", "name": "KLM Royal Dutch Airlines", "country": "Нидерланды 🇳🇱", "callsign": "KLM"},
    "KLC": {"iata": "WA", "name": "KLM Cityhopper", "country": "Нидерланды 🇳🇱", "callsign": "CITY"},
    "TRA": {"iata": "HV", "name": "Transavia", "country": "Нидерланды 🇳🇱", "callsign": "TRANSAVIA"},
    "BAW": {"iata": "BA", "name": "British Airways", "country": "Великобритания 🇬🇧", "callsign": "SPEEDBIRD"},
    "EZY": {"iata": "U2", "name": "easyJet UK", "country": "Великобритания 🇬🇧", "callsign": "EASY"},
    "EZS": {"iata": "DS", "name": "easyJet Switzerland", "country": "Швейцария 🇨🇭", "callsign": "TOPSWISS"},
    "EJU": {"iata": "EC", "name": "easyJet Europe", "country": "Австрия 🇦🇹", "callsign": "ALPINE"},
    "SAS": {"iata": "SK", "name": "Scandinavian Airlines (SAS)", "country": "Швеция 🇸🇪", "callsign": "SCANDINAVIAN"},
    "NOZ": {"iata": "DY", "name": "Norwegian Air Shuttle", "country": "Норвегия 🇳🇴", "callsign": "NOR SHUTTLE"},
    "NSZ": {"iata": "D8", "name": "Norwegian Air Sweden", "country": "Швеция 🇸🇪", "callsign": "REDNOSE"},
    "FIN": {"iata": "AY", "name": "Finnair", "country": "Финляндия 🇫🇮", "callsign": "FINNAIR"},
    "AUA": {"iata": "OS", "name": "Austrian Airlines", "country": "Австрия 🇦🇹", "callsign": "AUSTRIAN"},
    "SWR": {"iata": "LX", "name": "Swiss International Air Lines", "country": "Швейцария 🇨🇭", "callsign": "SWISS"},
    "BEL": {"iata": "SN", "name": "Brussels Airlines", "country": "Бельгия 🇧🇪", "callsign": "BEE-LINE"},
    "IBE": {"iata": "IB", "name": "Iberia", "country": "Испания 🇪🇸", "callsign": "IBERIA"},
    "IBS": {"iata": "I2", "name": "Iberia Express", "country": "Испания 🇪🇸", "callsign": "IBERIAEXPRES"},
    "VLG": {"iata": "VY", "name": "Vueling Airlines", "country": "Испания 🇪🇸", "callsign": "VUELING"},
    "AEA": {"iata": "UX", "name": "Air Europa", "country": "Испания 🇪🇸", "callsign": "EUROPA"},
    "TAP": {"iata": "TP", "name": "TAP Air Portugal", "country": "Португалия 🇵🇹", "callsign": "AIR PORTUGAL"},
    "ITY": {"iata": "AZ", "name": "ITA Airways", "country": "Италия 🇮🇹", "callsign": "ITARROW"},
    "NOS": {"iata": "NO", "name": "Neos", "country": "Италия 🇮🇹", "callsign": "MOONFLOWER"},
    "EIN": {"iata": "EI", "name": "Aer Lingus", "country": "Ирландия 🇮🇪", "callsign": "SHAMROCK"},
    "ICE": {"iata": "FI", "name": "Icelandair", "country": "Исландия 🇮🇸", "callsign": "ICEAIR"},
    "BTI": {"iata": "BT", "name": "airBaltic", "country": "Латвия 🇱🇻", "callsign": "AIR BALTIC"},

    # Middle East & Turkey
    "THY": {"iata": "TK", "name": "Turkish Airlines", "country": "Турция 🇹🇷", "callsign": "TURKISH"},
    "PGT": {"iata": "PC", "name": "Pegasus Airlines", "country": "Турция 🇹🇷", "callsign": "SUNTURK"},
    "SXS": {"iata": "XQ", "name": "SunExpress", "country": "Турция 🇹🇷", "callsign": "SUNEXPRESS"},
    "UAE": {"iata": "EK", "name": "Emirates", "country": "ОАЭ 🇦🇪", "callsign": "EMIRATES"},
    "ETD": {"iata": "EY", "name": "Etihad Airways", "country": "ОАЭ 🇦🇪", "callsign": "ETIHAD"},
    "FDB": {"iata": "FZ", "name": "flydubai", "country": "ОАЭ 🇦🇪", "callsign": "SKYDUBAI"},
    "ABY": {"iata": "G9", "name": "Air Arabia", "country": "ОАЭ 🇦🇪", "callsign": "ARABIA"},
    "QTR": {"iata": "QR", "name": "Qatar Airways", "country": "Катар 🇶🇦", "callsign": "QATARI"},
    "SVA": {"iata": "SV", "name": "Saudia", "country": "Саудовская Аравия 🇸🇦", "callsign": "SAUDIA"},
    "FAD": {"iata": "XY", "name": "flynas", "country": "Саудовская Аравия 🇸🇦", "callsign": "NAS EXPRESS"},
    "GFA": {"iata": "GF", "name": "Gulf Air", "country": "Бахрейн 🇧🇭", "callsign": "GULF AIR"},
    "OMA": {"iata": "WY", "name": "Oman Air", "country": "Оман 🇴🇲", "callsign": "OMAN AIR"},
    "KAC": {"iata": "KU", "name": "Kuwait Airways", "country": "Кувейт 🇰🇼", "callsign": "KUWAITI"},
    "RJA": {"iata": "RJ", "name": "Royal Jordanian", "country": "Иордания 🇯🇴", "callsign": "JORDANIAN"},
    "MSR": {"iata": "MS", "name": "EgyptAir", "country": "Египет 🇪🇬", "callsign": "EGYPTAIR"},
    "ELY": {"iata": "LY", "name": "EL AL Israel Airlines", "country": "Израиль 🇮🇱", "callsign": "EL AL"},

    # North America
    "AAL": {"iata": "AA", "name": "American Airlines", "country": "США 🇺🇸", "callsign": "AMERICAN"},
    "DAL": {"iata": "DL", "name": "Delta Air Lines", "country": "США 🇺🇸", "callsign": "DELTA"},
    "UAL": {"iata": "UA", "name": "United Airlines", "country": "США 🇺🇸", "callsign": "UNITED"},
    "SWA": {"iata": "WN", "name": "Southwest Airlines", "country": "США 🇺🇸", "callsign": "SOUTHWEST"},
    "JBU": {"iata": "B6", "name": "JetBlue Airways", "country": "США 🇺🇸", "callsign": "JETBLUE"},
    "ASA": {"iata": "AS", "name": "Alaska Airlines", "country": "США 🇺🇸", "callsign": "ALASKA"},
    "FFT": {"iata": "F9", "name": "Frontier Airlines", "country": "США 🇺🇸", "callsign": "FRONTIER FLIGHT"},
    "NKS": {"iata": "NK", "name": "Spirit Airlines", "country": "США 🇺🇸", "callsign": "SPIRIT WINGS"},
    "ACA": {"iata": "AC", "name": "Air Canada", "country": "Канада 🇨🇦", "callsign": "AIR CANADA"},
    "ROU": {"iata": "RV", "name": "Air Canada Rouge", "country": "Канада 🇨🇦", "callsign": "ROUGE"},
    "WJA": {"iata": "WS", "name": "WestJet", "country": "Канада 🇨🇦", "callsign": "WESTJET"},
    "AMX": {"iata": "AM", "name": "Aeroméxico", "country": "Мексика 🇲🇽", "callsign": "AEROMEXICO"},

    # Asia & Pacific
    "ANA": {"iata": "NH", "name": "All Nippon Airways (ANA)", "country": "Япония 🇯🇵", "callsign": "ALL NIPPON"},
    "JAL": {"iata": "JL", "name": "Japan Airlines (JAL)", "country": "Япония 🇯🇵", "callsign": "JAPANAIR"},
    "APJ": {"iata": "MM", "name": "Peach Aviation", "country": "Япония 🇯🇵", "callsign": "AIR PEACH"},
    "KAL": {"iata": "KE", "name": "Korean Air", "country": "Южная Корея 🇰🇷", "callsign": "KOREANAIR"},
    "AAR": {"iata": "OZ", "name": "Asiana Airlines", "country": "Южная Корея 🇰🇷", "callsign": "ASIANA"},
    "SIA": {"iata": "SQ", "name": "Singapore Airlines", "country": "Сингапур 🇸🇬", "callsign": "SINGAPORE"},
    "SCO": {"iata": "TR", "name": "Scoot", "country": "Сингапур 🇸🇬", "callsign": "SCOOTER"},
    "CPA": {"iata": "CX", "name": "Cathay Pacific", "country": "Гонконг 🇭🇰", "callsign": "CATHAY"},
    "CCA": {"iata": "CA", "name": "Air China", "country": "Китай 🇨🇳", "callsign": "AIR CHINA"},
    "CES": {"iata": "MU", "name": "China Eastern Airlines", "country": "Китай 🇨🇳", "callsign": "CHINA EASTERN"},
    "CSN": {"iata": "CZ", "name": "China Southern Airlines", "country": "Китай 🇨🇳", "callsign": "CHINA SOUTHERN"},
    "HDA": {"iata": "HU", "name": "Hainan Airlines", "country": "Китай 🇨🇳", "callsign": "HAINAN"},
    "EVA": {"iata": "BR", "name": "EVA Air", "country": "Тайвань 🇹🇼", "callsign": "EVA"},
    "CAL": {"iata": "CI", "name": "China Airlines", "country": "Тайвань 🇹🇼", "callsign": "DYNASTY"},
    "THA": {"iata": "TG", "name": "Thai Airways", "country": "Таиланд 🇹🇭", "callsign": "THAI"},
    "MAS": {"iata": "MH", "name": "Malaysia Airlines", "country": "Малайзия 🇲🇾", "callsign": "MALAYSIAN"},
    "AXM": {"iata": "AK", "name": "AirAsia", "country": "Малайзия 🇲🇾", "callsign": "ASIAN EXPRESS"},
    "GIA": {"iata": "GA", "name": "Garuda Indonesia", "country": "Индонезия 🇮🇩", "callsign": "INDONESIA"},
    "AIC": {"iata": "AI", "name": "Air India", "country": "Индия 🇮🇳", "callsign": "AIRINDIA"},
    "IGO": {"iata": "6E", "name": "IndiGo", "country": "Индия 🇮🇳", "callsign": "IFLY"},
    "QFA": {"iata": "QF", "name": "Qantas", "country": "Австралия 🇦🇺", "callsign": "QANTAS"},
    "JST": {"iata": "JQ", "name": "Jetstar", "country": "Австралия 🇦🇺", "callsign": "JETSTAR"},
    "VOZ": {"iata": "VA", "name": "Virgin Australia", "country": "Австралия 🇦🇺", "callsign": "VELOCITY"},
    "ANZ": {"iata": "NZ", "name": "Air New Zealand", "country": "Новая Зеландия 🇳🇿", "callsign": "NEW ZEALAND"},

    # Cargo & Heavy Transport
    "FDX": {"iata": "FX", "name": "FedEx Express", "country": "США 🇺🇸", "callsign": "FEDEX"},
    "UPS": {"iata": "5X", "name": "UPS Airlines", "country": "США 🇺🇸", "callsign": "UPS"},
    "GEC": {"iata": "LH", "name": "Lufthansa Cargo", "country": "Германия 🇩🇪", "callsign": "LUFTHANSA CARGO"},
    "BCS": {"iata": "QY", "name": "European Air Transport (DHL)", "country": "Германия 🇩🇪", "callsign": "POSTMAN"},
    "DHK": {"iata": "D0", "name": "DHL Air UK", "country": "Великобритания 🇬🇧", "callsign": "WORLD EXPRESS"},
    "CLX": {"iata": "CV", "name": "Cargolux", "country": "Люксембург 🇱🇺", "callsign": "CARGOLUX"},
    "ADB": {"iata": "ADB", "name": "Antonov Airlines", "country": "Украина 🇺🇦", "callsign": "ANTONOV BUREAU"},
    "AZG": {"iata": "ZP", "name": "Silk Way West Airlines", "country": "Азербайджан 🇦🇿", "callsign": "SILK WEST"}
}

# Reverse lookup by IATA
_IATA_INDEX = {v["iata"]: v for v in AIRLINES_DATA.values() if v.get("iata")}


def get_airline_info(query: str) -> dict:
    """
    Look up airline by ICAO, IATA, or part of callsign/flight number.
    Returns dict with name, country, iata, icao, callsign or None.
    """
    if not query:
        return None
    q = query.upper().strip()

    # Exact ICAO
    if q in AIRLINES_DATA:
        res = dict(AIRLINES_DATA[q])
        res["icao"] = q
        return res

    # Exact IATA
    if q in _IATA_INDEX:
        res = dict(_IATA_INDEX[q])
        for icao, info in AIRLINES_DATA.items():
            if info.get("iata") == q:
                res["icao"] = icao
                break
        return res

    # Prefix match
    for icao in sorted(AIRLINES_DATA.keys(), key=len, reverse=True):
        if q.startswith(icao):
            res = dict(AIRLINES_DATA[icao])
            res["icao"] = icao
            return res

    for iata in sorted(_IATA_INDEX.keys(), key=len, reverse=True):
        if len(iata) >= 2 and q.startswith(iata):
            res = dict(_IATA_INDEX[iata])
            for icao, info in AIRLINES_DATA.items():
                if info.get("iata") == iata:
                    res["icao"] = icao
                    break
            return res

    return None


def format_airline_display(query: str, fallback: str = "") -> str:
    """
    Returns a user-facing airline string:
    e.g. 'LOT Polish Airlines 🇵🇱' or 'Wizz Air 🇭🇺'
    """
    info = get_airline_info(query)
    if info:
        flag = info['country'].split(' ')[-1]
        return f"{info['name']} {flag}"
    return fallback or query
