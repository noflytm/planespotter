import re
import json
import urllib.request
import urllib.parse
import boto3
import os

COUNTRY_PREFIXES = [
    ("SP-", {"ru": "Польша 🇵🇱", "en": "Poland 🇵🇱", "pl": "Polska 🇵🇱"}),
    ("OE-", {"ru": "Австрия 🇦🇹", "en": "Austria 🇦🇹", "pl": "Austria 🇦🇹"}),
    ("9H-", {"ru": "Мальта 🇲🇹", "en": "Malta 🇲🇹", "pl": "Malta 🇲🇹"}),
    ("D-", {"ru": "Германия 🇩🇪", "en": "Germany 🇩🇪", "pl": "Niemcy 🇩🇪"}),
    ("F-", {"ru": "Франция 🇫🇷", "en": "France 🇫🇷", "pl": "Francja 🇫🇷"}),
    ("G-", {"ru": "Великобритания 🇬🇧", "en": "United Kingdom 🇬🇧", "pl": "Wielka Brytania 🇬🇧"}),
    ("EI-", {"ru": "Ирландия 🇮🇪", "en": "Ireland 🇮🇪", "pl": "Irlandia 🇮🇪"}),
    ("EJ-", {"ru": "Ирландия 🇮🇪", "en": "Ireland 🇮🇪", "pl": "Irlandia 🇮🇪"}),
    ("TC-", {"ru": "Турция 🇹🇷", "en": "Turkey 🇹🇷", "pl": "Turcja 🇹🇷"}),
    ("A6-", {"ru": "ОАЭ 🇦🇪", "en": "UAE 🇦🇪", "pl": "ZEA 🇦🇪"}),
    ("A7-", {"ru": "Катар 🇶🇦", "en": "Qatar 🇶🇦", "pl": "Katar 🇶🇦"}),
    ("HZ-", {"ru": "Саудовская Аравия 🇸🇦", "en": "Saudi Arabia 🇸🇦", "pl": "Arabia Saudyjska 🇸🇦"}),
    ("4X-", {"ru": "Израиль 🇮🇱", "en": "Israel 🇮🇱", "pl": "Izrael 🇮🇱"}),
    ("UR-", {"ru": "Украина 🇺🇦", "en": "Ukraine 🇺🇦", "pl": "Ukraina 🇺🇦"}),
    ("RA-", {"ru": "Россия 🇷🇺", "en": "Russia 🇷🇺", "pl": "Rosja 🇷🇺"}),
    ("RF-", {"ru": "Россия 🇷🇺", "en": "Russia 🇷🇺", "pl": "Rosja 🇷🇺"}),
    ("EW-", {"ru": "Беларусь 🇧🇾", "en": "Belarus 🇧🇾", "pl": "Białoruś 🇧🇾"}),
    ("YL-", {"ru": "Латвия 🇱🇻", "en": "Latvia 🇱🇻", "pl": "Łotwa 🇱🇻"}),
    ("LY-", {"ru": "Литва 🇱🇹", "en": "Lithuania 🇱🇹", "pl": "Litwa 🇱🇹"}),
    ("ES-", {"ru": "Эстония 🇪🇪", "en": "Estonia 🇪🇪", "pl": "Estonia 🇪🇪"}),
    ("HB-", {"ru": "Швейцария 🇨🇭", "en": "Switzerland 🇨🇭", "pl": "Szwajcaria 🇨🇭"}),
    ("OH-", {"ru": "Финляндия 🇫🇮", "en": "Finland 🇫🇮", "pl": "Finlandia 🇫🇮"}),
    ("SE-", {"ru": "Швеция 🇸🇪", "en": "Sweden 🇸🇪", "pl": "Szwecja 🇸🇪"}),
    ("LN-", {"ru": "Норвегия 🇳🇴", "en": "Norway 🇳🇴", "pl": "Norwegia 🇳🇴"}),
    ("OY-", {"ru": "Дания 🇩🇰", "en": "Denmark 🇩🇰", "pl": "Dania 🇩🇰"}),
    ("PH-", {"ru": "Нидерланды 🇳🇱", "en": "Netherlands 🇳🇱", "pl": "Holandia 🇳🇱"}),
    ("OO-", {"ru": "Бельгия 🇧🇪", "en": "Belgium 🇧🇪", "pl": "Belgia 🇧🇪"}),
    ("LX-", {"ru": "Люксембург 🇱🇺", "en": "Luxembourg 🇱🇺", "pl": "Luksemburg 🇱🇺"}),
    ("EC-", {"ru": "Испания 🇪🇸", "en": "Spain 🇪🇸", "pl": "Hiszpania 🇪🇸"}),
    ("CS-", {"ru": "Португалия 🇵🇹", "en": "Portugal 🇵🇹", "pl": "Portugalia 🇵🇹"}),
    ("I-", {"ru": "Италия 🇮🇹", "en": "Italy 🇮🇹", "pl": "Włochy 🇮🇹"}),
    ("SX-", {"ru": "Греция 🇬🇷", "en": "Greece 🇬🇷", "pl": "Grecja 🇬🇷"}),
    ("HA-", {"ru": "Венгрия 🇭🇺", "en": "Hungary 🇭🇺", "pl": "Węgry 🇭🇺"}),
    ("OK-", {"ru": "Чехия 🇨🇿", "en": "Czech Republic 🇨🇿", "pl": "Czechy 🇨🇿"}),
    ("OM-", {"ru": "Словакия 🇸🇰", "en": "Slovakia 🇸🇰", "pl": "Słowacja 🇸🇰"}),
    ("9A-", {"ru": "Хорватия 🇭🇷", "en": "Croatia 🇭🇷", "pl": "Chorwacja 🇭🇷"}),
    ("S5-", {"ru": "Словения 🇸🇮", "en": "Slovenia 🇸🇮", "pl": "Słowenia 🇸🇮"}),
    ("YU-", {"ru": "Сербия 🇷🇸", "en": "Serbia 🇷🇸", "pl": "Serbia 🇷🇸"}),
    ("LZ-", {"ru": "Болгария 🇧🇬", "en": "Bulgaria 🇧🇬", "pl": "Bułgaria 🇧🇬"}),
    ("YR-", {"ru": "Румыния 🇷🇴", "en": "Romania 🇷🇴", "pl": "Rumunia 🇷🇴"}),
    ("B-", {"ru": "Китай / Тайвань 🇨🇳", "en": "China / Taiwan 🇨🇳", "pl": "Chiny / Tajwan 🇨🇳"}),
    ("JA", {"ru": "Япония 🇯🇵", "en": "Japan 🇯🇵", "pl": "Japonia 🇯🇵"}),
    ("HL", {"ru": "Южная Корея 🇰🇷", "en": "South Korea 🇰🇷", "pl": "Korea Południowa 🇰🇷"}),
    ("VT-", {"ru": "Индия 🇮🇳", "en": "India 🇮🇳", "pl": "Indie 🇮🇳"}),
    ("VH-", {"ru": "Австралия 🇦🇺", "en": "Australia 🇦🇺", "pl": "Australia 🇦🇺"}),
    ("ZK-", {"ru": "Новая Зеландия 🇳🇿", "en": "New Zealand 🇳🇿", "pl": "Nowa Zelandia 🇳🇿"}),
    ("C-", {"ru": "Канада 🇨🇦", "en": "Canada 🇨🇦", "pl": "Kanada 🇨🇦"}),
    ("N", {"ru": "США 🇺🇸", "en": "USA 🇺🇸", "pl": "USA 🇺🇸"}),
]

UNKNOWN_COUNTRY = {
    "ru": "Неизвестная страна",
    "en": "Unknown country",
    "pl": "Nieznany kraj"
}

_CACHED_TOKEN = None

def get_bot_token() -> str:
    global _CACHED_TOKEN
    if _CACHED_TOKEN:
        return _CACHED_TOKEN
    token = os.environ.get("BOT_TOKEN", "").strip()
    if token:
        _CACHED_TOKEN = token
        return _CACHED_TOKEN
    for param_name in ["plainspotter_api_key", "/plainspotter_api_key", "/plainspotter/bot_token"]:
        try:
            ssm = boto3.client("ssm", region_name=os.environ.get("AWS_REGION", "us-east-1"))
            res = ssm.get_parameter(Name=param_name, WithDecryption=True)
            val = res.get("Parameter", {}).get("Value", "").strip()
            if val:
                _CACHED_TOKEN = val
                print(f"Bot token successfully loaded from SSM Parameter Store ({param_name}).")
                return _CACHED_TOKEN
        except Exception:
            continue
    return ""

def normalize_reg(reg: str) -> str:
    if not reg:
        return ""
    return re.sub(r"[^A-Z0-9]", "", reg.upper())

def detect_country(reg: str, lang: str = "ru") -> str:
    upper_reg = reg.upper().strip()
    for prefix, country_data in COUNTRY_PREFIXES:
        if upper_reg.startswith(prefix.upper()):
            if isinstance(country_data, dict):
                return country_data.get(lang) or country_data.get("en") or list(country_data.values())[0]
            return str(country_data)
    norm = normalize_reg(reg)
    for prefix, country_data in COUNTRY_PREFIXES:
        norm_p = normalize_reg(prefix)
        if norm.startswith(norm_p):
            if isinstance(country_data, dict):
                return country_data.get(lang) or country_data.get("en") or list(country_data.values())[0]
            return str(country_data)
    return UNKNOWN_COUNTRY.get(lang, UNKNOWN_COUNTRY.get("en", "Unknown country"))

def get_dynamo_tables():
    region = os.environ.get("AWS_REGION", "us-east-1")
    dynamo = boto3.resource("dynamodb", region_name=region)
    users_table = dynamo.Table(os.environ.get("USERS_TABLE", "planespotter_users"))
    aircraft_table = dynamo.Table(os.environ.get("AIRCRAFT_TABLE", "planespotter_aircraft"))
    return users_table, aircraft_table

def send_telegram(token: str, chat_id: int, text: str, parse_mode: str = "HTML", reply_markup: dict = None, photo_url: str = None, disable_preview: bool = False):
    if not token:
        token = get_bot_token()
    if not token:
        print("Telegram token not available, skipping send.")
        return False

    if photo_url:
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        payload = {
            "chat_id": chat_id,
            "photo": photo_url,
            "caption": text,
            "parse_mode": parse_mode
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"sendPhoto failed ({e}), falling back to sendMessage...")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    full_text = text
    if photo_url and photo_url not in text:
        full_text = f'<a href="{photo_url}">&#8205;</a>' + text

    payload = {
        "chat_id": chat_id,
        "text": full_text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_preview
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")
        return False

def send_invoice(token: str, chat_id: int, title: str, description: str, payload_str: str, currency: str = "XTR", prices: list = None):
    if not token:
        token = get_bot_token()
    if not token:
        return False
    url = f"https://api.telegram.org/bot{token}/sendInvoice"
    payload = {
        "chat_id": chat_id,
        "title": title,
        "description": description,
        "payload": payload_str,
        "currency": currency,
        "prices": prices or [{"label": "⭐ 50 Telegram Stars", "amount": 50}]
    }
    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Failed to send Invoice: {e}")
        return False

def create_invoice_link(token: str, title: str, description: str, payload_str: str, currency: str = "XTR", prices: list = None) -> str:
    if not token:
        token = get_bot_token()
    if not token:
        return ""
    url = f"https://api.telegram.org/bot{token}/createInvoiceLink"
    payload = {
        "title": title,
        "description": description,
        "payload": payload_str,
        "currency": currency,
        "prices": prices or [{"label": "⭐ 50 Telegram Stars", "amount": 50}]
    }
    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            if res.get("ok"):
                return res.get("result", "")
    except Exception as e:
        print(f"Failed to create Invoice link: {e}")
    return ""

def answer_pre_checkout(token: str, pre_checkout_query_id: str, ok: bool = True, error_msg: str = None):
    if not token:
        token = get_bot_token()
    url = f"https://api.telegram.org/bot{token}/answerPreCheckoutQuery"
    payload = {"pre_checkout_query_id": pre_checkout_query_id, "ok": ok}
    if error_msg:
        payload["error_message"] = error_msg
    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Failed to answer PreCheckout: {e}")
        return False

def send_telegram_document(token: str, chat_id: int, file_content: bytes, filename: str, caption: str = None, reply_markup: dict = None):
    if not token:
        token = get_bot_token()
    if not token:
        return False
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"

    parts = []
    # chat_id
    parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"chat_id\"\r\n\r\n{chat_id}\r\n".encode("utf-8"))
    # caption
    if caption:
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"caption\"\r\n\r\n{caption}\r\n".encode("utf-8"))
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"parse_mode\"\r\n\r\nHTML\r\n".encode("utf-8"))
    # reply_markup
    if reply_markup:
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"reply_markup\"\r\n\r\n{json.dumps(reply_markup)}\r\n".encode("utf-8"))
    # document
    parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"document\"; filename=\"{filename}\"\r\nContent-Type: audio/x-mpegurl\r\n\r\n".encode("utf-8"))
    parts.append(file_content)
    parts.append(f"\r\n--{boundary}--\r\n".encode("utf-8"))

    body = b"".join(parts)
    req = urllib.request.Request(url, data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Failed to send Telegram document: {e}")
        return False


def set_chat_menu_button(token: str, chat_id: int, title: str, webapp_url: str):
    if not token:
        token = get_bot_token()
    if not token:
        return False
    url = f"https://api.telegram.org/bot{token}/setChatMenuButton"
    payload = {
        "chat_id": chat_id,
        "menu_button": {
            "type": "web_app",
            "text": title,
            "web_app": {"url": webapp_url}
        }
    }
    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Failed to setChatMenuButton for {chat_id}: {e}")
        return False


def edit_telegram_message(token: str, chat_id: int, message_id: int, text: str, parse_mode: str = "HTML", reply_markup: dict = None):
    if not token:
        token = get_bot_token()
    if not token:
        return False
    url = f"https://api.telegram.org/bot{token}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Failed to edit Telegram message: {e}")
        return False


