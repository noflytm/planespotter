import json
import os
import re

COUNTRY_PREFIXES = [
    ("SP-", "Польша 🇵🇱"),
    ("OE-", "Австрия 🇦🇹"),
    ("9H-", "Мальта 🇲🇹"),
    ("D-", "Германия 🇩🇪"),
    ("F-", "Франция 🇫🇷"),
    ("G-", "Великобритания 🇬🇧"),
    ("EI-", "Ирландия 🇮🇪"),
    ("EJ-", "Ирландия 🇮🇪"),
    ("TC-", "Турция 🇹🇷"),
    ("A6-", "ОАЭ 🇦🇪"),
    ("A7-", "Катар 🇶🇦"),
    ("HZ-", "Саудовская Аравия 🇸🇦"),
    ("4X-", "Израиль 🇮🇱"),
    ("UR-", "Украина 🇺🇦"),
    ("RA-", "Россия 🇷🇺"),
    ("RF-", "Россия 🇷🇺"),
    ("EW-", "Беларусь 🇧🇾"),
    ("YL-", "Латвия 🇱🇻"),
    ("LY-", "Литва 🇱🇹"),
    ("ES-", "Эстония 🇪🇪"),
    ("HB-", "Швейцария 🇨🇭"),
    ("OH-", "Финляндия 🇫🇮"),
    ("SE-", "Швеция 🇸🇪"),
    ("LN-", "Норвегия 🇳🇴"),
    ("OY-", "Дания 🇩🇰"),
    ("PH-", "Нидерланды 🇳🇱"),
    ("OO-", "Бельгия 🇧🇪"),
    ("LX-", "Люксембург 🇱🇺"),
    ("EC-", "Испания 🇪🇸"),
    ("CS-", "Португалия 🇵🇹"),
    ("I-", "Италия 🇮🇹"),
    ("SX-", "Греция 🇬🇷"),
    ("HA-", "Венгрия 🇭🇺"),
    ("OK-", "Чехия 🇨🇿"),
    ("OM-", "Словакия 🇸🇰"),
    ("9A-", "Хорватия 🇭🇷"),
    ("S5-", "Словения 🇸🇮"),
    ("YU-", "Сербия 🇷🇸"),
    ("LZ-", "Болгария 🇧🇬"),
    ("YR-", "Румыния 🇷🇴"),
    ("B-", "Китай / Тайвань 🇨🇳"),
    ("JA", "Япония 🇯🇵"),
    ("HL", "Южная Корея 🇰🇷"),
    ("VT-", "Индия 🇮🇳"),
    ("VH-", "Австралия 🇦🇺"),
    ("ZK-", "Новая Зеландия 🇳🇿"),
    ("C-", "Канада 🇨🇦"),
    ("N", "США 🇺🇸"),
]

def normalize_reg(reg: str) -> str:
    if not reg:
        return ""
    return re.sub(r"[^A-Z0-9]", "", reg.upper())

def detect_country(reg: str) -> str:
    upper_reg = reg.upper().strip()
    for prefix, country in COUNTRY_PREFIXES:
        if upper_reg.startswith(prefix.upper()):
            return country
    norm = normalize_reg(reg)
    for prefix, country in COUNTRY_PREFIXES:
        norm_p = normalize_reg(prefix)
        if norm.startswith(norm_p):
            return country
    return "Неизвестная страна"

class SpotterDB:
    def __init__(self, data_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "aws_lambda", "demo_aircraft.json")):
        self.data_path = data_path
        self.unique_aircraft = {}
        self.total_photos = 0
        self.load_data()

    def load_data(self):
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Database file not found: {self.data_path}")

        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in data:
            reg = item.get("reg_code", "").strip()
            if not reg:
                continue
            norm = normalize_reg(reg)
            self.unique_aircraft[norm] = item
            self.total_photos += item.get("photo_count", 1)

    def get_stats(self):
        return {
            "total_photos": self.total_photos,
            "total_aircraft": len(self.unique_aircraft)
        }

    def search(self, query: str):
        query = query.strip()
        norm_query = normalize_reg(query)
        if not norm_query:
            return None

        if norm_query in self.unique_aircraft:
            return self.unique_aircraft[norm_query]

        if len(norm_query) >= 3:
            matches = [v for k, v in self.unique_aircraft.items() if norm_query in k]
            if len(matches) == 1:
                return matches[0]
            elif len(matches) > 1:
                return {"partial_matches": matches[:5]}

        return None
