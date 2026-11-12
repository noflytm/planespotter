import json
import os
import re
import time
from datetime import datetime, timedelta
import boto3
from common import (
    normalize_reg, detect_country, get_dynamo_tables, send_telegram, send_invoice,
    create_invoice_link, answer_pre_checkout, send_telegram_document,
    set_chat_menu_button, edit_telegram_message, get_bot_token
)
from i18n import (
    t, detect_user_lang, build_main_reply_keyboard, HUB_BASE_URL,
    COMMON_TIMEZONES, get_timezone_for_airport,
    SUPPORTED_LANGUAGES, LANG_FLAGS, LANG_NAMES
)
from airports import find_nearest_airport, AIRPORTS, get_airport_by_code, generate_atc_m3u, get_airport_country, world_countries, world_cities, world_country_name, country_flag, search_world_airports
from schedule_provider import get_airport_schedule
from jetphotos_api import search_jetphotos, get_aircraft_live_photo
from airlines import format_airline_display, get_airline_info
from spotterguide import get_spotterguide_url, get_spots_for_airport
from collections import Counter

class _LazyToken:
    def __str__(self):
        return get_bot_token()
    def __repr__(self):
        return get_bot_token()
    def __bool__(self):
        return bool(get_bot_token())

BOT_TOKEN = _LazyToken()
SYNC_LAMBDA_NAME = os.environ.get("SYNC_LAMBDA_NAME", "planespotter-sync")
lambda_client = boto3.client("lambda", region_name=os.environ.get("AWS_REGION", "us-east-1"))

SUPERUSER_USERNAMES = ["user_not_found_now"]

def is_superuser(message_or_from: dict) -> bool:
    if not message_or_from:
        return False
    user_info = message_or_from.get("from") if "from" in message_or_from else message_or_from
    username = (user_info.get("username") or "").lower().strip()
    return username in SUPERUSER_USERNAMES

def track_user_activity(users_table, telegram_id: str, message: dict = None, action_type: str = "general"):
    """
    Atomically track user activity, request counts, username, and last active timestamp in DynamoDB.
    """
    now_iso = datetime.utcnow().isoformat()
    from_user = message.get("from", {}) if message else {}
    username = from_user.get("username", "")
    first_name = from_user.get("first_name", "")

    update_expr = "ADD request_count :one"
    expr_attr_vals = {":one": 1}

    if action_type == "aircraft_lookup":
        update_expr += ", aircraft_lookups :one"
    elif action_type == "spotting_plan":
        update_expr += ", spotting_plans :one"
    elif action_type == "radar":
        update_expr += ", radar_sessions :one"

    set_clauses = ["last_active_at = :now"]
    expr_attr_vals[":now"] = now_iso

    if username:
        set_clauses.append("username = :un")
        expr_attr_vals[":un"] = username
    if first_name:
        set_clauses.append("first_name = :fn")
        expr_attr_vals[":fn"] = first_name

    update_expr += " SET " + ", ".join(set_clauses)

    try:
        users_table.update_item(
            Key={"telegram_id": telegram_id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_attr_vals
        )
    except Exception as e:
        print(f"Notice: user activity update for {telegram_id}: {e}")

POPULAR_AIRPORTS = [
    {"iata": "GDN", "icao": "EPGD", "flag": "🇵🇱", "names": {"ru": "Гданьск", "en": "Gdansk", "pl": "Gdańsk"}},
    {"iata": "WAW", "icao": "EPWA", "flag": "🇵🇱", "names": {"ru": "Варшава", "en": "Warsaw", "pl": "Warszawa"}},
    {"iata": "KRK", "icao": "EPKK", "flag": "🇵🇱", "names": {"ru": "Краков", "en": "Krakow", "pl": "Kraków"}},
    {"iata": "WMI", "icao": "EPMO", "flag": "🇵🇱", "names": {"ru": "Модлин", "en": "Modlin", "pl": "Modlin"}},
    {"iata": "KTW", "icao": "EPKT", "flag": "🇵🇱", "names": {"ru": "Катовице", "en": "Katowice", "pl": "Katowice"}},
    {"iata": "RIX", "icao": "EVRA", "flag": "🇱🇻", "names": {"ru": "Рига", "en": "Riga", "pl": "Rīga"}},
    {"iata": "BER", "icao": "EDDB", "flag": "🇩🇪", "names": {"ru": "Берлин", "en": "Berlin", "pl": "Berlin"}},
]

def get_popular_airport_label(ap: dict, user_lang: str = "ru") -> str:
    flag = ap.get("flag", "✈️")
    name = ap.get("names", {}).get(user_lang) or ap.get("names", {}).get("en") or ap.get("iata")
    return f"{flag} {ap['iata']} ({name})"



def get_user_settings(user: dict):
    lang = user.get("lang") if user else None
    if not lang or lang not in SUPPORTED_LANGUAGES:
        lang = "ru"
    tz = user.get("timezone", "Europe/Warsaw") if user else "Europe/Warsaw"
    offset = user.get("utc_offset", "+02:00") if user else "+02:00"
    airport = user.get("nearest_airport") or user.get("monitoring_airport") or "WAW" if user else "WAW"
    notify = user.get("notifications_enabled", True) if user else True
    return lang, tz, offset, airport, notify

def build_hub_url(lang: str = "ru", tz: str = "Europe/Warsaw", icao: str = "WAW"):
    return f"{HUB_BASE_URL}/player?lang={lang}&tz={tz}&icao={icao}&v={int(time.time())}"

def send_settings_menu(chat_id: int, user_lang: str, user: dict, message_id: int = None):
    lang, tz, offset, airport, notify = get_user_settings(user)
    lang_display = f"{LANG_FLAGS.get(lang, '🌐')} {LANG_NAMES.get(lang, lang.upper())}"
    notify_status = ("🟢 " + t("status_on", user_lang)) if notify else ("⚪ " + t("status_off", user_lang))
    if user_lang == "en":
        notify_status = "🟢 Enabled" if notify else "⚪ Disabled"
    elif user_lang == "pl":
        notify_status = "🟢 Włączone" if notify else "⚪ Wyłączone"

    body = t("settings_body", user_lang,
             lang_display=lang_display,
             timezone=tz,
             utc_offset=offset,
             airport=airport,
             notifications_status=notify_status)
    msg = t('settings_title', user_lang) + "\n\n" + body

    hub_url = build_hub_url(user_lang, tz, airport)
    kb = {
        "inline_keyboard": [
            [{"text": f"{t('settings_btn_lang', user_lang)} ({LANG_FLAGS.get(lang, '')})", "callback_data": "settings:lang"}],
            [{"text": f"{t('settings_btn_tz', user_lang)} ({offset})", "callback_data": "settings:tz"}],
            [{"text": f"{t('settings_btn_airport', user_lang)} ({airport})", "callback_data": "settings:airport"}],
            [{"text": f"{t('settings_btn_notify', user_lang)}: {notify_status}", "callback_data": "settings:notify_toggle"}],
            [{"text": f"🚀 {t('btn_open_hub_cta', user_lang)}", "web_app": {"url": hub_url}}]
        ]
    }
    if message_id:
        edit_telegram_message(BOT_TOKEN, chat_id, message_id, msg, reply_markup=kb)
    else:
        reply_kb = build_main_reply_keyboard(user_lang, hub_url)
        send_telegram(BOT_TOKEN, chat_id, msg, reply_markup=kb)

def send_lang_menu(chat_id: int, user_lang: str, current_lang: str, message_id: int = None):
    msg = t("lang_select_prompt", user_lang)
    buttons = []
    for l_code in SUPPORTED_LANGUAGES:
        flag = LANG_FLAGS.get(l_code, "")
        name = LANG_NAMES.get(l_code, l_code)
        check = " ✅" if l_code == current_lang else ""
        buttons.append([{"text": f"{flag} {name}{check}", "callback_data": f"lang:{l_code}"}])
    buttons.append([{"text": t("settings_btn_back", user_lang), "callback_data": "settings:main"}])
    kb = {"inline_keyboard": buttons}
    if message_id:
        edit_telegram_message(BOT_TOKEN, chat_id, message_id, msg, reply_markup=kb)
    else:
        send_telegram(BOT_TOKEN, chat_id, msg, reply_markup=kb)

def send_timezone_menu(chat_id: int, user_lang: str, current_tz: str, current_offset: str, hub_url: str, message_id: int = None):
    msg = t("tz_select_prompt", user_lang, tz=current_tz, offset=current_offset)
    buttons = [
        [{"text": t("btn_share_location", user_lang), "callback_data": "tz:loc_prompt"}],
        [{"text": t("btn_tz_device", user_lang), "web_app": {"url": f"{hub_url}&sync_tz=1"}}],
    ]
    tz_rows = []
    for item in COMMON_TIMEZONES:
        label = item["labels"].get(user_lang, item["labels"]["en"])
        check = " ✅" if item["id"] == current_tz else ""
        tz_rows.append([{"text": f"{label}{check}", "callback_data": f"tz:set:{item['id']}:{item['offset']}"}])
    buttons.extend(tz_rows)
    buttons.append([{"text": t("settings_btn_back", user_lang), "callback_data": "settings:main"}])
    kb = {"inline_keyboard": buttons}
    if message_id:
        edit_telegram_message(BOT_TOKEN, chat_id, message_id, msg, reply_markup=kb)
    else:
        send_telegram(BOT_TOKEN, chat_id, msg, reply_markup=kb)

def send_airport_menu(chat_id: int, user_lang: str, current_airport: str, message_id: int = None):
    msg = "📍 <b>Выберите домашний аэропорт по умолчанию:</b>" if user_lang == "ru" else (
        "📍 <b>Select your default home airport:</b>" if user_lang == "en" else "📍 <b>Wybierz domyślne lotnisko:</b>"
    )
    msg += "\n\n" + t("airport_input_hint", user_lang)
    buttons = [
        [{"text": t("btn_browse_geo", user_lang), "callback_data": "geo:c:set"}]
    ]
    row = []
    for ap in POPULAR_AIRPORTS:
        check = " ✅" if ap["iata"] == current_airport or ap["icao"] == current_airport else ""
        ap_label = get_popular_airport_label(ap, user_lang)
        row.append({"text": f"{ap_label}{check}", "callback_data": f"airport:set:{ap['iata']}:{ap['icao']}"})
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([{"text": t("settings_btn_back", user_lang), "callback_data": "settings:main"}])
    kb = {"inline_keyboard": buttons}
    if message_id:
        edit_telegram_message(BOT_TOKEN, chat_id, message_id, msg, reply_markup=kb)
    else:
        send_telegram(BOT_TOKEN, chat_id, msg, reply_markup=kb)

MAIN_REPLY_KEYBOARD = {
    "keyboard": [
        [{"text": "🎯 Режим Споттинга"}, {"text": "🛑 Остановить радар"}],
        [{"text": "📻 Радио ATC"}, {"text": "🔎 Проверить борт"}],
        [{"text": "📍 Моя локация", "request_location": True}, {"text": "📊 Моя статистика"}],
        [{"text": "⭐ Premium (Звёзды)"}, {"text": "❓ Помощь"}]
    ],
    "resize_keyboard": True,
    "is_persistent": True
}

def handler(event, context):
    try:
        body = event.get("body", "{}")
        if event.get("isBase64Encoded", False):
            import base64
            body = base64.b64decode(body).decode("utf-8")
        
        update = json.loads(body) if isinstance(body, str) else body
        print(f"Incoming Telegram Update: {json.dumps(update)}")
    except Exception as e:
        print(f"Error parsing request body: {e}")
        return {"statusCode": 200, "body": "OK"}

    if "pre_checkout_query" in update:
        query_id = update["pre_checkout_query"]["id"]
        answer_pre_checkout(BOT_TOKEN, query_id, ok=True)
        return {"statusCode": 200, "body": "OK"}

    if "message" in update:
        handle_message(update["message"])
    elif "callback_query" in update:
        handle_callback(update["callback_query"])

    return {"statusCode": 200, "body": "OK"}


def handle_message(message: dict):
    chat_id = message["chat"]["id"]
    telegram_id = str(chat_id)
    text = message.get("text", "").strip()
    users_table, aircraft_table = get_dynamo_tables()

    # Track user interaction & metadata
    track_user_activity(users_table, telegram_id, message, action_type="general")

    res = users_table.get_item(Key={"telegram_id": telegram_id})
    user = res.get("Item")

    user_lang, user_tz, user_tz_offset, user_airport, _ = get_user_settings(user)
    # Detect language if not stored yet
    if not user or "lang" not in user:
        detected = detect_user_lang(message.get("from", {}), None)
        user_lang = detected
        try:
            users_table.update_item(
                Key={"telegram_id": telegram_id},
                UpdateExpression="SET lang = :l, updated_at = :u",
                ExpressionAttributeValues={":l": detected, ":u": datetime.utcnow().isoformat()}
            )
        except Exception:
            pass

    hub_url = build_hub_url(user_lang, user_tz, user_airport)
    user_reply_kb = build_main_reply_keyboard(user_lang, hub_url)

    # 1. Successful Telegram Stars Payment
    if "successful_payment" in message:
        pay = message["successful_payment"]
        currency = pay.get("currency")
        amount = pay.get("total_amount")
        
        exp_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
        users_table.update_item(
            Key={"telegram_id": telegram_id},
            UpdateExpression="SET is_premium = :p, premium_until = :pu, updated_at = :u",
            ExpressionAttributeValues={
                ":p": True,
                ":pu": exp_date,
                ":u": datetime.utcnow().isoformat()
            }
        )
        msg = t("stars_payment_success_msg", user_lang, amount=amount, currency=currency)
        send_telegram(BOT_TOKEN, chat_id, msg, reply_markup=user_reply_kb)
        return

    # 2. Location shared
    if "location" in message:
        loc = message["location"]
        lat, lon = loc["latitude"], loc["longitude"]
        airport, dist = find_nearest_airport(lat, lon)
        
        if airport:
            tz_info = get_timezone_for_airport(airport["icao"])
            offset_str = f"UTC{'+' if tz_info['offset'] >= 0 else ''}{tz_info['offset']}"
            users_table.update_item(
                Key={"telegram_id": telegram_id},
                UpdateExpression="SET last_latitude = :lat, last_longitude = :lon, nearest_airport = :ap, #tz = :tz, utc_offset = :off, updated_at = :u",
                ExpressionAttributeNames={"#tz": "timezone"},
                ExpressionAttributeValues={
                    ":lat": str(lat),
                    ":lon": str(lon),
                    ":ap": airport["icao"],
                    ":tz": tz_info["tz"],
                    ":off": offset_str,
                    ":u": datetime.utcnow().isoformat()
                }
            )
            msg = t("location_detected", user_lang,
                    name=airport["name"],
                    icao=airport["icao"],
                    iata=airport["iata"],
                    country=get_airport_country(airport["country"], user_lang),
                    dist=dist,
                    tz=tz_info["tz"],
                    offset=offset_str)
            hub_url = build_hub_url(user_lang, tz_info["tz"], airport["icao"])
            kb = {
                "inline_keyboard": [
                    [{"text": f"📋 {t('btn_spotting_mode', user_lang)} ({airport['iata']})", "callback_data": f"plan:{airport['iata']}:{airport['icao']}"}],
                    [{"text": f"🚀 {t('btn_open_hub_cta', user_lang)}", "web_app": {"url": hub_url}}],
                    [{"text": t("btn_radar_30", user_lang), "callback_data": f"radar:30:{airport['icao']}"}],
                    [{"text": t("btn_stop_radar", user_lang), "callback_data": "stop_radar"}]
                ]
            }
            reply_kb = build_main_reply_keyboard(user_lang, hub_url)
            send_telegram(BOT_TOKEN, chat_id, msg, reply_markup=kb)
            set_chat_menu_button(BOT_TOKEN, chat_id, t("menu_button_title", user_lang), hub_url)
        else:
            send_telegram(BOT_TOKEN, chat_id, t("location_not_found", user_lang), reply_markup=user_reply_kb)
        return

    if not text:
        return

    # 3. Handle Button Commands (both Text and Slash commands)
    if text.startswith("/admin") or text in ["👑 Админка", "админка", "admin"]:
        if not is_superuser(message):
            send_telegram(BOT_TOKEN, chat_id, t("admin_only_msg", user_lang), reply_markup=user_reply_kb)
            return
        send_admin_panel(chat_id)
        return

    if text.startswith("/sync_now"):
        if not is_superuser(message):
            send_telegram(BOT_TOKEN, chat_id, t("admin_only_msg", user_lang), reply_markup=user_reply_kb)
            return
        trigger_admin_sync(chat_id)
        return

    if text.startswith("/broadcast"):
        if not is_superuser(message):
            send_telegram(BOT_TOKEN, chat_id, t("admin_only_msg", user_lang), reply_markup=user_reply_kb)
            return
        parts = text.split(" ", 1)
        if len(parts) < 2 or not parts[1].strip():
            send_telegram(BOT_TOKEN, chat_id, "ℹ️ Использование: <code>/broadcast Ваше объявление здесь</code>")
            return
        execute_broadcast(chat_id, parts[1].strip(), users_table)
        return

    if text.startswith("/grant_premium"):
        if not is_superuser(message):
            send_telegram(BOT_TOKEN, chat_id, t("admin_only_msg", user_lang), reply_markup=user_reply_kb)
            return
        parts = text.split()
        if len(parts) < 3 or not parts[2].isdigit():
            send_telegram(BOT_TOKEN, chat_id, "ℹ️ Использование: <code>/grant_premium &lt;user_id&gt; &lt;дней&gt;</code>\nПример: <code>/grant_premium 12345678 30</code>", reply_markup=user_reply_kb)
            return
        target_uid = parts[1].strip()
        days = int(parts[2])
        exp_date = (datetime.utcnow() + timedelta(days=days)).isoformat()
        try:
            users_table.update_item(
                Key={"telegram_id": target_uid},
                UpdateExpression="SET is_premium = :p, premium_until = :pu, updated_at = :u",
                ExpressionAttributeValues={
                    ":p": True,
                    ":pu": exp_date,
                    ":u": datetime.utcnow().isoformat()
                }
            )
            send_telegram(BOT_TOKEN, chat_id, f"✅ <b>Premium успешно выдан!</b>\n\n👤 Пользователь: <code>{target_uid}</code>\n⏰ Срок: <b>{days} дней</b> (до {exp_date[:10]})\n⭐️ Статус: <b>Active Premium</b>", reply_markup=user_reply_kb)
            try:
                send_telegram(BOT_TOKEN, int(target_uid) if target_uid.isdigit() else target_uid, f"🎉 <b>Администратор активировал вам PlaneSpotter Premium на {days} дней!</b>\n\nВам доступны:\n• Радар до 4 часов\n• Алерты Squawk 7700 и диверты\n• Споттинг-план на 1 час с разметкой новых бортов")
            except Exception as e:
                print(f"Notice: unable to notify recipient {target_uid}: {e}")
        except Exception as e:
            send_telegram(BOT_TOKEN, chat_id, f"❌ Ошибка выдачи Premium: {e}")
        return

    # Settings Menu Command
    if text in ["⚙️ Настройки", "⚙️ Settings", "⚙️ Ustawienia", "/settings", "settings", "настройки", "ustawienia"]:
        send_settings_menu(chat_id, user_lang, user)
        return

    if text in ["🎯 Режим Споттинга", "🎯 Spotting Mode", "🎯 Tryb Spottingu", "/spotting"]:
        send_spotting_menu(chat_id, user_lang)
        return

    if text in ["🔎 Проверить борт", "🔎 Check tail", "🔎 Sprawdź rejestrację", "/check"]:
        send_telegram(BOT_TOKEN, chat_id, t("check_reg_prompt", user_lang))
        return

    if text in ["📻 Радио ATC", "📻 ATC Radio", "📻 Radio ATC", "/atc", "/radio", "радио", "atc"]:
        send_atc_menu(chat_id, user, user_lang)
        return

    if text in ["🛑 Остановить радар", "🛑 Stop Radar", "🛑 Zatrzymaj radar", "/stop"]:
        stop_radar(chat_id, telegram_id, users_table, user_lang)
        return

    if text in ["📊 Моя статистика", "📊 My Stats", "📊 Moje statystyki", "/stats"]:
        if user and user.get("sync_status") == "COMPLETED":
            monitoring_until = int(user.get("monitoring_until", 0))
            is_monitoring = monitoring_until > int(time.time())
            radar_status = t("radar_status_active", user_lang, airport=user.get('monitoring_airport', 'EPGD')) if is_monitoring else t("radar_status_off", user_lang)
            tier_str = "Premium ⭐" if user.get("is_premium") else ("Standard (Free)" if user_lang != "ru" else "Базовый (Бесплатный)")
            
            msg = t(
                "stats_summary_msg",
                user_lang,
                name=user.get('photographer_name', 'Spotter'),
                jp_id=user.get('jetphotos_id', 'N/A'),
                photos=user.get('total_photos', 0),
                aircraft=user.get('total_aircraft', 0),
                radar=radar_status,
                tier=tier_str,
                last_sync=user.get('last_sync_at', 'Recently')[:16]
            )
            send_telegram(BOT_TOKEN, chat_id, msg, reply_markup=user_reply_kb)
        else:
            send_telegram(BOT_TOKEN, chat_id, t("stats_no_base_msg", user_lang), reply_markup=user_reply_kb)
        return

    if text in ["⭐ Premium (Звёзды)", "⭐ Premium (Stars)", "⭐ Premium (Gwiazdki)", "/premium"]:
        send_premium_info(chat_id, user_lang=user_lang)
        return

    if text in ["❓ Помощь", "❓ Help", "❓ Pomoc", "/help"]:
        send_telegram(BOT_TOKEN, chat_id, t("help_text", user_lang), reply_markup=user_reply_kb)
        return

    if text.startswith("/start"):
        # Auto-grant owner & premium role to superuser
        if is_superuser(message):
            try:
                users_table.update_item(
                    Key={"telegram_id": telegram_id},
                    UpdateExpression="SET is_premium = :p, is_owner = :o, updated_at = :u",
                    ExpressionAttributeValues={":p": True, ":o": True, ":u": datetime.utcnow().isoformat()}
                )
            except Exception:
                pass

        # Set Native Telegram WebApp Menu button (CardBox style)
        set_chat_menu_button(BOT_TOKEN, chat_id, t("menu_button_title", user_lang), hub_url)

        # Check if user needs language selection first (e.g. not explicitly selected yet or reset)
        has_lang = user and user.get("lang_chosen")
        if not has_lang or text == "/start reset":
            msg = t("start_lang_prompt", "multi")
            kb = {
                "inline_keyboard": [
                    [
                        {"text": "🇷🇺 Русский", "callback_data": "start_lang:ru"},
                        {"text": "🇬🇧 English", "callback_data": "start_lang:en"},
                        {"text": "🇵🇱 Polski", "callback_data": "start_lang:pl"}
                    ]
                ]
            }
            send_telegram(BOT_TOKEN, chat_id, msg, reply_markup=kb)
            return

        welcome_text = t("welcome_title", user_lang) + "\n\n" + t("welcome_body", user_lang)

        inline_cta = {
            "inline_keyboard": [
                [{"text": f"🚀 {t('btn_open_hub_cta', user_lang)}", "web_app": {"url": hub_url}}],
                [{"text": t("settings_btn_tz", user_lang), "callback_data": "settings:tz"}, {"text": t("settings_btn_lang", user_lang), "callback_data": "settings:lang"}],
                [{"text": t("btn_demo_base", user_lang), "callback_data": "demo_link"}]
            ]
        }

        # If user has not set location or nearest airport yet, prompt onboarding
        if not user or not user.get("nearest_airport"):
            onboarding_prompt = t("onboarding_tz_prompt", user_lang)
            onboarding_reply_kb = {
                "keyboard": [
                    [{"text": t("btn_share_location", user_lang), "request_location": True}],
                    [{"text": t("btn_spotting_mode", user_lang)}, {"text": t("btn_settings", user_lang)}],
                    [{"text": t("btn_check_reg", user_lang)}, {"text": t("btn_help", user_lang)}]
                ],
                "resize_keyboard": True,
                "one_time_keyboard": True
            }
            send_telegram(BOT_TOKEN, chat_id, welcome_text, reply_markup=onboarding_reply_kb)
            send_telegram(BOT_TOKEN, chat_id, onboarding_prompt, reply_markup=inline_cta)
        else:
            send_telegram(BOT_TOKEN, chat_id, welcome_text, reply_markup=user_reply_kb)
            send_telegram(BOT_TOKEN, chat_id, f"📍 <b>{user.get('nearest_airport', 'WAW')}</b> • <code>{user_tz}</code> ({user_tz_offset})", reply_markup=inline_cta)
        return

    # Smart routing: airport code -> city/airport name search -> (below) JetPhotos ID / aircraft registration
    clean_code = text.upper().strip()
    looks_like_reg = bool(re.fullmatch(r"[A-Z0-9]{1,2}-[A-Z0-9]{1,5}", clean_code)) or \
        bool(re.fullmatch(r"N\d{1,5}[A-Z]{0,2}", clean_code))
    if not looks_like_reg and re.fullmatch(r"[A-Z]{3}|[A-Z0-9]{4}", clean_code):
        match_ap = get_airport_by_code(clean_code)
        if match_ap:
            track_user_activity(users_table, telegram_id, message, action_type="spotting_plan")
            send_spotting_plan(chat_id, telegram_id, match_ap["iata"], match_ap["icao"], users_table, aircraft_table, user, user_lang=user_lang)
            return

    if not looks_like_reg and re.fullmatch(r"[^\W\d_]+(?:[ '\-][^\W\d_]+)*", text.strip()) and len(text.strip()) >= 3:
        found = search_world_airports(text)
        if len(found) == 1:
            track_user_activity(users_table, telegram_id, message, action_type="spotting_plan")
            send_spotting_plan(chat_id, telegram_id, found[0]["iata"], found[0]["icao"], users_table, aircraft_table, user, user_lang=user_lang)
            return
        if found:
            rows = []
            for ap in found:
                label = f"{country_flag(ap['cc'])} {ap['iata']} — {ap['city']}: {ap['name']}"
                rows.append([{"text": label[:45], "callback_data": f"plan:{ap['iata']}:{ap['icao']}"}])
            send_telegram(BOT_TOKEN, chat_id, t("search_results_title", user_lang, n=len(found)), reply_markup={"inline_keyboard": rows})
            return

    # 4. Check JetPhotos ID linking
    m_jp = re.search(r"jetphotos\.com/photographer/(\d{4,8})", text) or re.fullmatch(r"\s*(\d{4,8})\s*", text)
    if m_jp and (not user or user.get("sync_status") != "COMPLETED"):
        jp_id = m_jp.group(1)
        
        if user and user.get("jetphotos_id") and user.get("jetphotos_id") != jp_id and user.get("sync_status") == "COMPLETED":
            send_telegram(
                BOT_TOKEN,
                chat_id,
                t("jp_already_linked_warning", user_lang, jp_id=user.get('jetphotos_id'), name=user.get('photographer_name')),
                reply_markup=user_reply_kb
            )
            return

        users_table.put_item(Item={
            "telegram_id": telegram_id,
            "jetphotos_id": jp_id,
            "sync_status": "PENDING",
            "is_premium": False,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        })

        send_telegram(
            BOT_TOKEN,
            chat_id,
            t("jp_import_starting", user_lang, jp_id=jp_id),
            reply_markup=user_reply_kb
        )

        try:
            lambda_client.invoke(
                FunctionName=SYNC_LAMBDA_NAME,
                InvocationType="Event",
                Payload=json.dumps({"telegram_id": telegram_id, "jetphotos_id": jp_id})
            )
        except Exception as e:
            print(f"Error invoking sync lambda: {e}")
        return

    norm_reg = normalize_reg(text)
    if not norm_reg:
        send_telegram(BOT_TOKEN, chat_id, t("not_recognized", user_lang), reply_markup=user_reply_kb)
        return

    clean_reg = text.upper().strip()
    country = detect_country(clean_reg, user_lang)
    track_user_activity(users_table, telegram_id, message, action_type="aircraft_lookup")
    is_user_synced = bool(user and user.get("sync_status") == "COMPLETED")

    # Check local collection if user is synced
    plane = None
    if is_user_synced:
        ac_res = aircraft_table.get_item(
            Key={"user_id": telegram_id, "reg_norm": norm_reg}
        )
        plane = ac_res.get("Item")

    if plane:
        reg_code = plane.get("reg_code", clean_reg)
        country = detect_country(reg_code, user_lang)
        
        reg_links = []
        if plane.get("info_url"):
            reg_links.append(f'<a href="{plane["info_url"]}">{reg_code} full info |</a>')
        photos_url = plane.get("photos_url", f"https://www.jetphotos.com/registration/{reg_code}")
        reg_links.append(f'<a href="{photos_url}">{reg_code} photos</a>')
        reg_str = " ".join(reg_links)

        ac_name = plane.get("aircraft_name", "N/A")
        ac_str = f'<a href="{plane.get("aircraft_url", "")}">{ac_name}</a>' if plane.get("aircraft_url") else ac_name

        al_name = plane.get("airline_name", "N/A")
        al_formatted = format_airline_display(al_name)
        al_str = f'<a href="{plane.get("airline_url", "")}">{al_formatted}</a>' if plane.get("airline_url") else al_formatted

        sn_val = plane.get("serial_val", plane.get("msn", "N/A"))
        sn_str = f'<a href="{plane.get("serial_url", "")}">{sn_val}</a>' if plane.get("serial_url") and sn_val != "N/A" else sn_val

        cnt = plane.get("photo_count", 1)
        latest_date = plane.get("latest_photo_date") or t("card_not_specified", user_lang)
        thumbnail = plane.get("thumbnail_url", "")

        card = (
            f"{t('card_collection_found_title', user_lang)}\n\n"
            f"{t('card_label_model', user_lang)} {ac_str}\n"
            f"{t('card_label_msn', user_lang)} {sn_str}\n"
            f"{t('card_label_reg', user_lang)} {reg_str} ({country})\n"
            f"{t('card_label_airline', user_lang)} {al_str}\n\n"
            f"{t('card_label_latest_photo', user_lang)} {latest_date}\n"
            f"{t('card_label_in_collection', user_lang, cnt=cnt)}\n"
            f"{t('card_label_all_photos', user_lang, reg=reg_code)}\n\n"
            f"{t('card_hint_livery', user_lang)}"
        )
        kb = {
            "inline_keyboard": [
                [{"text": t("btn_aircraft_facts", user_lang), "callback_data": f"facts:{reg_code}"}],
                [
                    {"text": t("card_btn_all_photos_jp", user_lang), "url": f"https://www.jetphotos.com/registration/{reg_code}"},
                    {"text": t("btn_fr24", user_lang), "url": f"https://www.flightradar24.com/data/aircraft/{reg_code}"}
                ],
                [{"text": f"🚀 {t('btn_open_hub_cta', user_lang)}", "web_app": {"url": f"{HUB_BASE_URL}/player?lang={user_lang}&reg={reg_code}&v={int(time.time())}"}}]
            ]
        }
        send_telegram(BOT_TOKEN, chat_id, card, reply_markup=kb, photo_url=thumbnail)
    else:
        # Aircraft is NOT in user's collection or user has not synced yet.
        # Query Global JetPhotos API for live photos and info!
        live = get_aircraft_live_photo(clean_reg)

        if live:
            model = live.get("aircraftType") or t("card_aircraft_fallback", user_lang)
            airline = format_airline_display(live.get("airline", "N/A"))
            msn = live.get("msn", "N/A")
            photographer = live.get("photographer", "JetPhotos")
            photo_date = live.get("photoDate") or t("card_recently", user_lang)
            thumb = live.get("thumbnailUrl", "")
            full_img = live.get("imageUrl", "")
            photo_page = live.get("photoPageUrl", f"https://www.jetphotos.com/registration/{clean_reg}")

            source_name = "Planespotters" if live.get("source") == "planespotters" else "JetPhotos"
            if is_user_synced:
                title = t("card_new_for_collection_title", user_lang)
                hint = t("card_new_for_collection_hint", user_lang)
            else:
                title = t("card_global_info_title", user_lang, source=source_name.upper())
                hint = t("card_global_info_hint", user_lang)

            card = (
                f"{title}\n\n"
                f"{t('card_label_model', user_lang)} {model}\n"
                f"{t('card_label_msn', user_lang)} {msn}\n"
                f"{t('card_label_reg', user_lang)} <code>{clean_reg}</code> ({country})\n"
                f"{t('card_label_airline', user_lang)} {airline}\n\n"
                f"{t('card_label_photo_date', user_lang)} {photo_date}\n"
                f"{t('card_label_author', user_lang)} {photographer}\n\n"
                f"{hint}"
            )
            buttons = [
                [
                    {"text": t("card_btn_photo_source", user_lang, source=source_name), "url": photo_page},
                    {"text": t("btn_fr24", user_lang), "url": f"https://www.flightradar24.com/data/aircraft/{clean_reg}"}
                ],
                [
                    {"text": t("btn_aircraft_facts", user_lang), "callback_data": f"facts:{clean_reg}"},
                    {"text": f"🛰 {t('btn_spotter_hub', user_lang)}", "web_app": {"url": f"{HUB_BASE_URL}/player?lang={user_lang}&reg={clean_reg}&v={int(time.time())}"}}
                ]
            ]
            if not is_user_synced:
                buttons.append([{"text": t("btn_demo_base", user_lang), "callback_data": "demo_link"}])

            send_telegram(BOT_TOKEN, chat_id, card, reply_markup={"inline_keyboard": buttons}, photo_url=thumb)
        else:
            # Not found on JetPhotos
            msg = (
                f"{t('card_rare_title', user_lang)}\n\n"
                f"{t('card_rare_body', user_lang, reg=clean_reg, country=country)}"
            )
            kb = {
                "inline_keyboard": [
                    [
                        {"text": t("btn_fr24", user_lang), "url": f"https://www.flightradar24.com/data/aircraft/{clean_reg}"},
                        {"text": "📷 JetPhotos", "url": f"https://www.jetphotos.com/registration/{clean_reg}"}
                    ],
                    [{"text": t("btn_aircraft_facts", user_lang), "callback_data": f"facts:{clean_reg}"}]
                ]
            }
            send_telegram(BOT_TOKEN, chat_id, msg, reply_markup=kb)


def stop_radar(chat_id: int, telegram_id: str, users_table, user_lang: str = "ru"):
    res = users_table.get_item(Key={"telegram_id": telegram_id})
    user = res.get("Item")
    current_time = int(time.time())
    
    monitoring_until = int(user.get("monitoring_until", 0)) if user else 0
    if monitoring_until > current_time:
        users_table.update_item(
            Key={"telegram_id": telegram_id},
            UpdateExpression="SET monitoring_until = :zero, updated_at = :u",
            ExpressionAttributeValues={
                ":zero": 0,
                ":u": datetime.utcnow().isoformat()
            }
        )
        msg = t("radar_stopped_msg", user_lang)
    else:
        msg = t("radar_not_active_msg", user_lang)
    reply_kb = build_main_reply_keyboard(user_lang)
    send_telegram(BOT_TOKEN, chat_id, msg, reply_markup=reply_kb)


def send_spotting_menu(chat_id: int, user_lang: str = "ru", message_id: int = None):
    msg = t("spotting_menu_msg", user_lang)
    buttons = [
        [{"text": t("btn_browse_geo", user_lang), "callback_data": "geo:c:plan"}]
    ]
    row = []
    for ap in POPULAR_AIRPORTS:
        row.append({"text": get_popular_airport_label(ap, user_lang), "callback_data": f"plan:{ap['iata']}:{ap['icao']}"})
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    buttons.append([{"text": t("btn_stop_active_radar", user_lang), "callback_data": "stop_radar"}])
    buttons.append([{"text": t("btn_buy_premium_inline", user_lang), "callback_data": "buy_premium"}])
    kb = {"inline_keyboard": buttons}
    if message_id:
        edit_telegram_message(BOT_TOKEN, chat_id, message_id, msg, reply_markup=kb)
    else:
        send_telegram(BOT_TOKEN, chat_id, msg, reply_markup=kb)


GEO_PAGE_SIZE = 20


def _geo_cb(mode: str, iata: str, icao: str) -> str:
    if mode == "plan":
        return f"plan:{iata}:{icao}"
    if mode == "set":
        return f"airport:set:{iata}:{icao}"
    return f"atc:{iata}:{icao}"


def _geo_send(chat_id, message_id, msg, buttons):
    kb = {"inline_keyboard": buttons}
    if message_id:
        edit_telegram_message(BOT_TOKEN, chat_id, message_id, msg, reply_markup=kb)
    else:
        send_telegram(BOT_TOKEN, chat_id, msg, reply_markup=kb)


def _geo_pager(buttons, page, total, cb_fn):
    pages = max(1, (total + GEO_PAGE_SIZE - 1) // GEO_PAGE_SIZE)
    if pages > 1:
        nav = []
        if page > 0:
            nav.append({"text": "◀️", "callback_data": cb_fn(page - 1)})
        nav.append({"text": f"{page + 1}/{pages}", "callback_data": cb_fn(page)})
        if page < pages - 1:
            nav.append({"text": "▶️", "callback_data": cb_fn(page + 1)})
        buttons.append(nav)


def send_geo_countries_menu(chat_id: int, user_lang: str, mode: str, message_id: int = None, page: int = 0):
    items = world_countries()
    page = max(0, min(page, (len(items) - 1) // GEO_PAGE_SIZE))
    chunk = items[page * GEO_PAGE_SIZE:(page + 1) * GEO_PAGE_SIZE]
    buttons, row = [], []
    for cc, name in chunk:
        row.append({"text": f"{country_flag(cc)} {name}"[:30], "callback_data": f"geo:ci:{cc}:{mode}:0"})
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    _geo_pager(buttons, page, len(items), lambda p: f"geo:c:{mode}:{p}")
    back_cb = "settings:airport" if mode == "set" else f"geo:back:{mode}"
    back_txt = t("settings_btn_back", user_lang) if mode == "set" else t("btn_back_to_spotting", user_lang)
    buttons.append([{"text": back_txt, "callback_data": back_cb}])
    _geo_send(chat_id, message_id, t("geo_countries_title", user_lang), buttons)


def send_geo_cities_menu(chat_id: int, user_lang: str, country_code: str, mode: str, message_id: int = None, page: int = 0):
    cities = world_cities(country_code)
    if not cities:
        send_geo_countries_menu(chat_id, user_lang, mode, message_id=message_id)
        return
    page = max(0, min(page, (len(cities) - 1) // GEO_PAGE_SIZE))
    msg = t("geo_cities_title", user_lang, country=f"{country_flag(country_code)} {world_country_name(country_code)}")
    buttons, row = [], []
    for idx in range(page * GEO_PAGE_SIZE, min(len(cities), (page + 1) * GEO_PAGE_SIZE)):
        city, aps = cities[idx]
        if len(aps) == 1:
            label = f"{city} ({aps[0][0]})"[:30]
            cb = _geo_cb(mode, aps[0][0], aps[0][1])
        else:
            label = f"🏙 {city} ({len(aps)}) ❯"[:30]
            cb = f"geo:ap:{country_code}:{idx}:{mode}"
        row.append({"text": label, "callback_data": cb})
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    _geo_pager(buttons, page, len(cities), lambda p: f"geo:ci:{country_code}:{mode}:{p}")
    buttons.append([{"text": t("btn_back_to_countries", user_lang), "callback_data": f"geo:c:{mode}:0"}])
    _geo_send(chat_id, message_id, msg, buttons)


def send_geo_airports_menu(chat_id: int, user_lang: str, country_code: str, city_idx, mode: str, message_id: int = None):
    cities = world_cities(country_code)
    try:
        city, aps = cities[int(city_idx)]
    except (ValueError, IndexError):
        send_geo_cities_menu(chat_id, user_lang, country_code, mode, message_id=message_id)
        return
    flag = country_flag(country_code)
    buttons = []
    for iata, icao, name, _lat, _lon in aps:
        label = f"{flag} {iata} — {name}"
        if len(label) > 40:
            label = label[:39] + "…"
        buttons.append([{"text": label, "callback_data": _geo_cb(mode, iata, icao)}])
    buttons.append([{"text": t("btn_back_to_cities", user_lang), "callback_data": f"geo:ci:{country_code}:{mode}:0"}])
    _geo_send(chat_id, message_id, t("geo_airports_title", user_lang, city=city), buttons)


def send_atc_menu(chat_id: int, user: dict = None, user_lang: str = "ru", message_id: int = None):
    # Determine active airport for user (monitored airport, spotting airport, or default EPGD / GDN)
    active_code = "EPGD"
    if user:
        candidate = user.get("monitoring_airport") or user.get("airport") or user.get("last_airport")
        if candidate:
            active_code = candidate

    active_ap = get_airport_by_code(active_code) or get_airport_by_code("EPGD")
    active_icao = active_ap.get("icao", "EPGD")
    active_iata = active_ap.get("iata", "GDN")

    msg = t("atc_menu_title", user_lang) + chr(10) + chr(10) + t("atc_menu_body", user_lang, iata=active_iata, icao=active_icao)
    webapp_url = f"{HUB_BASE_URL}/player?lang={user_lang}&icao={active_icao}&iata={active_iata}&v={int(time.time())}"
    buttons = [
        [{"text": t("atc_btn_scanner", user_lang, iata=active_iata), "web_app": {"url": webapp_url}}],
        [{"text": t("btn_browse_geo", user_lang), "callback_data": "geo:c:atc"}]
    ]
    row = []
    for ap in POPULAR_AIRPORTS:
        row.append({"text": get_popular_airport_label(ap, user_lang), "callback_data": f"atc:{ap['iata']}:{ap['icao']}"})
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    kb = {"inline_keyboard": buttons}
    if message_id:
        edit_telegram_message(BOT_TOKEN, chat_id, message_id, msg, reply_markup=kb)
    else:
        send_telegram(BOT_TOKEN, chat_id, msg, reply_markup=kb)



def send_atc_card(chat_id: int, iata: str, icao: str, user_lang: str = "ru"):
    ap = get_airport_by_code(iata) or get_airport_by_code(icao)
    if not ap:
        reply_kb = build_main_reply_keyboard(user_lang)
        send_telegram(BOT_TOKEN, chat_id, t("atc_not_found", user_lang, iata=iata, icao=icao), reply_markup=reply_kb)
        return

    name = ap.get("name", "Airport")
    country = get_airport_country(ap.get("country", ""), user_lang)
    freqs = ap.get("frequencies", {})
    twr = freqs.get("twr", "—")
    app = freqs.get("app", "—")
    gnd = freqs.get("gnd", "—")
    atis = freqs.get("atis", "—")

    liveatc = ap.get("liveatc", {})
    is_available = liveatc.get("available", False)
    streams = liveatc.get("streams", [])
    web_url = liveatc.get("web_url", f"https://www.liveatc.net/search/?icao={ap['icao']}")
    webapp_url = f"{HUB_BASE_URL}/player?lang={user_lang}&icao={ap['icao']}&iata={ap['iata']}&v={int(time.time())}"

    lines = [
        t("atc_card_title", user_lang, icao=ap["icao"], iata=ap["iata"]),
        f"<i>{name} ({country})</i>\n",
        t("atc_official_freqs", user_lang),
        t("atc_freq_twr", user_lang, freq=twr),
        t("atc_freq_app", user_lang, freq=app),
        t("atc_freq_gnd", user_lang, freq=gnd),
        t("atc_freq_atis", user_lang, freq=atis) + "\n",
    ]

    buttons = []
    if is_available and streams:
        titles = ", ".join([s.get("title", "") for s in streams])
        lines.append(t("atc_stream_active", user_lang))
        lines.append(t("atc_stream_channels", user_lang, titles=titles))
        lines.append(t("atc_stream_hint", user_lang))
        buttons.append([
            {"text": t("atc_btn_listen_tg", user_lang), "web_app": {"url": webapp_url}}
        ])
        buttons.append([
            {"text": t("atc_btn_download_m3u", user_lang), "callback_data": f"m3u:{ap['iata']}:{ap['icao']}"},
            {"text": t("atc_btn_liveatc_web", user_lang), "url": web_url}
        ])
    else:
        lines.append(t("atc_stream_unavailable", user_lang))
        lines.append(f"ℹ️ <i>{t('atc_stream_unavail_note', user_lang)}</i>\n")
        lines.append(t("atc_airband_hint", user_lang))
        buttons.append([
            {"text": t("atc_btn_open_scanner_tg", user_lang), "web_app": {"url": webapp_url}}
        ])
        buttons.append([
            {"text": t("atc_btn_check_liveatc", user_lang), "url": web_url}
        ])

    buttons.append([{"text": t("atc_btn_back_plan", user_lang), "callback_data": f"plan:{ap['iata']}:{ap['icao']}:all"}])

    send_telegram(BOT_TOKEN, chat_id, "\n".join(lines), reply_markup={"inline_keyboard": buttons})


def send_atc_playlist(chat_id: int, iata: str, icao: str, user_lang: str = "ru"):
    ap = get_airport_by_code(iata) or get_airport_by_code(icao)
    if not ap:
        send_telegram(BOT_TOKEN, chat_id, t("atc_not_found", user_lang, iata=iata, icao=icao))
        return

    m3u_text = generate_atc_m3u(ap)
    if not m3u_text:
        send_telegram(BOT_TOKEN, chat_id, t("atc_playlist_not_found", user_lang, icao=ap.get("icao", icao)))
        return

    file_bytes = m3u_text.encode("utf-8")
    filename = f"ATC_{ap['icao']}_{ap['iata']}_Live.m3u"
    caption = t("atc_playlist_caption", user_lang, icao=ap["icao"], iata=ap["iata"], filename=filename)
    kb = {
        "inline_keyboard": [
            [{"text": t("atc_btn_liveatc_web", user_lang), "url": ap.get("liveatc", {}).get("web_url", "https://www.liveatc.net")}],
            [{"text": t("atc_btn_back_freqs", user_lang), "callback_data": f"atc:{ap['iata']}:{ap['icao']}"}]
        ]
    }
    send_telegram_document(BOT_TOKEN, chat_id, file_bytes, filename, caption=caption, reply_markup=kb)


def send_spotting_plan(chat_id: int, telegram_id: str, iata: str, icao: str, users_table, aircraft_table, user: dict, filter_mode: str = "all", page: int = 1, selected_airline: str = "all", user_lang: str = "ru"):
    flights = get_airport_schedule(iata)
    if not flights:
        reply_kb = build_main_reply_keyboard(user_lang)
        send_telegram(BOT_TOKEN, chat_id, t("plan_fetch_error", user_lang, iata=iata), reply_markup=reply_kb)
        return

    # Tag flights with user collection items
    for f in flights:
        reg = f["reg"]
        norm = normalize_reg(reg)
        item = aircraft_table.get_item(Key={"user_id": telegram_id, "reg_norm": norm}).get("Item")
        f["item"] = item

    # Base filtering by mode
    if filter_mode == "arrivals":
        base_flights = [f for f in flights if f["mode"] == "arrivals"]
    elif filter_mode == "departures":
        base_flights = [f for f in flights if f["mode"] == "departures"]
    else:
        base_flights = flights

    # Calculate airline breakdown across all flights in current mode
    airline_counts = Counter()
    for f in base_flights:
        al = f.get("airline") or (f.get("flight_num", "")[:3] if f.get("flight_num") else "Other")
        airline_counts[al] += 1

    top_airlines = [al for al, cnt in airline_counts.most_common(5) if al and al not in ["Другие", "Other"]]

    # Filter by specific airline if chosen
    clean_sel = (selected_airline or "all").strip()
    if clean_sel.lower() != "all":
        active_flights = [
            f for f in base_flights
            if clean_sel.lower() in (f.get("airline") or "").lower() or clean_sel.lower() in (f.get("flight_num") or "").lower()
        ]
    else:
        active_flights = base_flights
        clean_sel = "all"

    # Pagination: 6 flights per page for ultra-crisp mobile readability
    PAGE_SIZE = 6
    total_items = len(active_flights)
    total_pages = max(1, (total_items + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(1, min(page, total_pages))
    start_idx = (page - 1) * PAGE_SIZE
    page_flights = active_flights[start_idx : start_idx + PAGE_SIZE]

    mode_label = ""
    if filter_mode == "departures":
        mode_label = t("plan_mode_dep_label", user_lang)
    elif filter_mode == "arrivals":
        mode_label = t("plan_mode_arr_label", user_lang)

    airline_filter_label = t("plan_filter_prefix", user_lang, filter=clean_sel.upper()) if clean_sel != "all" else ""

    header_line = t("plan_header", user_lang, icao=icao, iata=iata.upper(), mode_label=mode_label)
    sub_line = t("plan_sub_schedule", user_lang, count=len(active_flights), airline_filter=airline_filter_label, page=page, total_pages=total_pages)

    lines = [
        header_line,
        sub_line
    ]

    # Airline breakdown summary header
    if top_airlines:
        top_al_strs = [f"{format_airline_display(al, fallback=al)} ({airline_counts[al]})" for al in top_airlines[:3]]
        lines.append(t("plan_this_hour", user_lang) + " • ".join(top_al_strs))
        lines.append("")

    if not page_flights:
        lines.append(t("plan_no_flights_msg", user_lang))
    else:
        for f in page_flights:
            icon = "🛬" if f["mode"] == "arrivals" else "🛫"
            t_badge = f.get("time_badge", f.get("time_str", "--:-- UTC"))
            divert_badge = t("plan_badge_divert", user_lang) if f.get("is_diverted") else ""
            
            # Clickable Flightradar24 links
            flight_num_raw = str(f.get("flight_num") or "N/A").strip()
            reg_raw = str(f.get("reg") or "").strip()
            fr_reg_link = f"https://www.flightradar24.com/data/aircraft/{reg_raw.lower()}" if reg_raw else "https://www.flightradar24.com"
            fr_flight_link = f"https://www.flightradar24.com/data/flights/{flight_num_raw.lower()}" if flight_num_raw != "N/A" else fr_reg_link
            
            # Formatted airline
            airline_raw = f.get("airline") or (flight_num_raw[:3] if flight_num_raw != "N/A" else "")
            airline_display = format_airline_display(airline_raw, fallback=airline_raw)

            if not f.get("item"):
                badge = t("plan_badge_new", user_lang)
            else:
                cnt = f["item"].get("photo_count", 1)
                badge = t("plan_badge_in_db", user_lang, cnt=cnt)

            # Compact 2-line HUD card
            lines.append(
                f"{icon} <b>{t_badge}</b> <a href=\"{fr_reg_link}\"><code>{reg_raw}</code></a> ({f.get('model', 'Aircraft')}){divert_badge} — {badge}\n"
                f"   ✈️ {airline_display} | <a href=\"{fr_flight_link}\"><b>{flight_num_raw}</b></a> ({f.get('orig', 'N/A')} ➔ {f.get('dest', 'N/A')})"
            )
        lines.append("")

    lines.append(t("plan_fr24_hint", user_lang))

    # Build Interactive Keyboard
    inline_rows = []

    # 1. Mode selector buttons
    mode_row = []
    if filter_mode != "all":
        mode_row.append({"text": t("btn_plan_all_flights", user_lang), "callback_data": f"pl:{iata}:{icao}:all:1:{clean_sel[:8]}"})
    if filter_mode != "departures":
        mode_row.append({"text": t("btn_plan_departures", user_lang), "callback_data": f"pl:{iata}:{icao}:departures:1:{clean_sel[:8]}"})
    if filter_mode != "arrivals":
        mode_row.append({"text": t("btn_plan_arrivals", user_lang), "callback_data": f"pl:{iata}:{icao}:arrivals:1:{clean_sel[:8]}"})
    if mode_row:
        inline_rows.append(mode_row)

    # 2. Airline filter chips (top 3 airlines)
    al_row = []
    if clean_sel != "all":
        al_row.append({"text": t("btn_plan_reset_filter", user_lang), "callback_data": f"pl:{iata}:{icao}:{filter_mode}:1:all"})
    else:
        for al in top_airlines[:3]:
            al_short = al[:10].strip()
            al_row.append({"text": f"{al_short} ({airline_counts[al]})", "callback_data": f"pl:{iata}:{icao}:{filter_mode}:1:{al_short}"})
    if al_row:
        inline_rows.append(al_row)

    # 3. Pagination row
    if total_pages > 1:
        nav_row = []
        if page > 1:
            nav_row.append({"text": t("btn_plan_prev", user_lang), "callback_data": f"pl:{iata}:{icao}:{filter_mode}:{page-1}:{clean_sel[:8]}"})
        nav_row.append({"text": t("btn_plan_page", user_lang, page=page, total_pages=total_pages), "callback_data": f"pl:{iata}:{icao}:{filter_mode}:{page}:{clean_sel[:8]}"})
        if page < total_pages:
            nav_row.append({"text": t("btn_plan_next", user_lang), "callback_data": f"pl:{iata}:{icao}:{filter_mode}:{page+1}:{clean_sel[:8]}"})
        inline_rows.append(nav_row)

    # 4. Spotter tools & Hub
    sg_url = get_spotterguide_url(iata) or get_spotterguide_url(icao)
    hub_url = f"{HUB_BASE_URL}/player?lang={user_lang}&icao={icao}&iata={iata}&v={int(time.time())}"
    inline_rows.append([
        {"text": t("btn_spotterguide_spots", user_lang, iata=iata), "url": sg_url},
        {"text": t("btn_open_hub_cta", user_lang), "web_app": {"url": hub_url}}
    ])
    inline_rows.append([{"text": t("btn_atc_radio_inline", user_lang), "callback_data": f"atc:{iata}:{icao}"}])
    inline_rows.append([
        {"text": t("btn_radar_30", user_lang), "callback_data": f"radar:30:{icao}"},
        {"text": t("btn_radar_240", user_lang), "callback_data": f"radar:240:{icao}"}
    ])
    inline_rows.append([{"text": t("btn_stop_radar", user_lang), "callback_data": "stop_radar"}])

    kb = {"inline_keyboard": inline_rows}
    send_telegram(BOT_TOKEN, chat_id, "\n".join(lines), reply_markup=kb)


def send_premium_info(chat_id: int, user_lang: str = "en"):
    msg = t("prem_info_msg", user_lang)
    kb = {
        "inline_keyboard": [
            [{"text": t("prem_btn_pay", user_lang), "callback_data": "send_invoice_stars"}]
        ]
    }
    send_telegram(BOT_TOKEN, chat_id, msg, reply_markup=kb)


def handle_callback(cb: dict):
    cb_id = cb["id"]
    chat_id = cb["message"]["chat"]["id"]
    telegram_id = str(chat_id)
    from_user = cb.get("from", {})
    data = cb.get("data", "")
    users_table, aircraft_table = get_dynamo_tables()

    res = users_table.get_item(Key={"telegram_id": telegram_id})
    user = res.get("Item")
    user_lang = detect_user_lang(from_user, user.get("lang") or user.get("language") if user else None)
    _, user_tz, user_tz_offset, user_airport, _ = get_user_settings(user)
    hub_url = build_hub_url(user_lang, user_tz, user_airport)
    user_reply_kb = build_main_reply_keyboard(user_lang, hub_url)

    # 1. Settings Callbacks
    if data == "settings:main":
        send_settings_menu(chat_id, user_lang, user, message_id=cb["message"]["message_id"])
        return

    elif data == "settings:lang":
        send_lang_menu(chat_id, user_lang, user.get("lang", user_lang) if user else user_lang, message_id=cb["message"]["message_id"])
        return

    elif data.startswith("start_lang:"):
        new_lang = data.split(":")[1]
        if new_lang in SUPPORTED_LANGUAGES:
            users_table.update_item(
                Key={"telegram_id": telegram_id},
                UpdateExpression="SET lang = :l, lang_chosen = :c, updated_at = :u",
                ExpressionAttributeValues={":l": new_lang, ":c": True, ":u": datetime.utcnow().isoformat()}
            )
            res = users_table.get_item(Key={"telegram_id": telegram_id})
            user = res.get("Item")
            user_lang = new_lang
            user_tz = user.get("timezone", "Europe/Warsaw") if user else "Europe/Warsaw"
            user_offset = user.get("utc_offset", "+02:00") if user else "+02:00"
            user_airport = user.get("nearest_airport", "WAW") if user else "WAW"
            new_hub_url = build_hub_url(user_lang, user_tz, user_airport)
            set_chat_menu_button(BOT_TOKEN, chat_id, t("menu_button_title", user_lang), new_hub_url)
            new_reply_kb = build_main_reply_keyboard(user_lang, new_hub_url)

            welcome_text = t("welcome_title", user_lang) + "\n\n" + t("welcome_body", user_lang)
            onboarding_prompt = t("onboarding_tz_prompt", user_lang)

            inline_cta = {
                "inline_keyboard": [
                    [{"text": f"🚀 {t('btn_open_hub_cta', user_lang)}", "web_app": {"url": new_hub_url}}],
                    [{"text": t("settings_btn_tz", user_lang), "callback_data": "settings:tz"}, {"text": t("settings_btn_lang", user_lang), "callback_data": "settings:lang"}]
                ]
            }
            onboarding_reply_kb = {
                "keyboard": [
                    [{"text": t("btn_share_location", user_lang), "request_location": True}],
                    [{"text": t("btn_spotting_mode", user_lang)}, {"text": t("btn_settings", user_lang)}],
                    [{"text": t("btn_check_reg", user_lang)}, {"text": t("btn_help", user_lang)}]
                ],
                "resize_keyboard": True,
                "one_time_keyboard": True
            }
            edit_telegram_message(BOT_TOKEN, chat_id, cb["message"]["message_id"], welcome_text)
            send_telegram(BOT_TOKEN, chat_id, onboarding_prompt, reply_markup=onboarding_reply_kb)
            send_telegram(BOT_TOKEN, chat_id, f"📍 <b>{user_airport}</b> • <code>{user_tz}</code> ({user_offset})", reply_markup=inline_cta)
        return

    elif data.startswith("lang:"):
        new_lang = data.split(":")[1]
        if new_lang in SUPPORTED_LANGUAGES:
            users_table.update_item(
                Key={"telegram_id": telegram_id},
                UpdateExpression="SET lang = :l, updated_at = :u",
                ExpressionAttributeValues={":l": new_lang, ":u": datetime.utcnow().isoformat()}
            )
            res = users_table.get_item(Key={"telegram_id": telegram_id})
            user = res.get("Item")
            tz = user.get("timezone", "Europe/Warsaw") if user else "Europe/Warsaw"
            ap = user.get("nearest_airport", "WAW") if user else "WAW"
            new_hub_url = build_hub_url(new_lang, tz, ap)
            set_chat_menu_button(BOT_TOKEN, chat_id, t("menu_button_title", new_lang), new_hub_url)
            new_reply_kb = build_main_reply_keyboard(new_lang, new_hub_url)
            send_telegram(BOT_TOKEN, chat_id, t("lang_changed", new_lang), reply_markup=new_reply_kb)
            send_settings_menu(chat_id, new_lang, user, message_id=cb["message"]["message_id"])
        return

    elif data == "settings:tz":
        send_timezone_menu(chat_id, user_lang, user_tz, user_tz_offset, hub_url, message_id=cb["message"]["message_id"])
        return

    elif data.startswith("tz:set:"):
        parts = data.split(":")
        tz_id = parts[2]
        offset_val = int(parts[3])
        offset_str = f"UTC{'+' if offset_val >= 0 else ''}{offset_val}"
        users_table.update_item(
            Key={"telegram_id": telegram_id},
            UpdateExpression="SET #tz = :tz, utc_offset = :off, updated_at = :u",
            ExpressionAttributeNames={"#tz": "timezone"},
            ExpressionAttributeValues={":tz": tz_id, ":off": offset_str, ":u": datetime.utcnow().isoformat()}
        )
        res = users_table.get_item(Key={"telegram_id": telegram_id})
        user = res.get("Item")
        send_settings_menu(chat_id, user_lang, user, message_id=cb["message"]["message_id"])
        return

    elif data == "tz:loc_prompt":
        loc_kb = {
            "keyboard": [[{"text": t("btn_share_location", user_lang), "request_location": True}]],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
        send_telegram(BOT_TOKEN, chat_id, t("onboarding_tz_prompt", user_lang), reply_markup=loc_kb)
        return

    elif data == "settings:airport":
        current_ap = user.get("nearest_airport", "WAW") if user else "WAW"
        send_airport_menu(chat_id, user_lang, current_ap, message_id=cb["message"]["message_id"])
        return

    elif data.startswith("geo:"):
        parts = data.split(":")
        action = parts[1]
        msg_id = cb.get("message", {}).get("message_id")

        if action == "back":
            mode = parts[2] if len(parts) > 2 else "plan"
            if mode == "plan":
                send_spotting_menu(chat_id, user_lang, message_id=msg_id)
            elif mode == "atc":
                send_atc_menu(chat_id, user, user_lang, message_id=msg_id)
            elif mode == "set":
                current_ap = user.get("nearest_airport", "WAW") if user else "WAW"
                send_airport_menu(chat_id, user_lang, current_ap, message_id=msg_id)
            return

        elif action == "c":
            mode = parts[2] if len(parts) > 2 else "plan"
            pg = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
            send_geo_countries_menu(chat_id, user_lang, mode, message_id=msg_id, page=pg)
            return

        elif action == "ci":
            country_code = parts[2]
            mode = parts[3] if len(parts) > 3 else "plan"
            pg = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0
            send_geo_cities_menu(chat_id, user_lang, country_code, mode, message_id=msg_id, page=pg)
            return

        elif action == "ap":
            country_code = parts[2]
            city_idx = parts[3]
            mode = parts[4] if len(parts) > 4 else "plan"
            send_geo_airports_menu(chat_id, user_lang, country_code, city_idx, mode, message_id=msg_id)
            return

    elif data.startswith("airport:set:"):
        parts = data.split(":")
        iata = parts[2]
        icao = parts[3]
        tz_info = get_timezone_for_airport(icao)
        offset_str = f"UTC{'+' if tz_info['offset'] >= 0 else ''}{tz_info['offset']}"
        users_table.update_item(
            Key={"telegram_id": telegram_id},
            UpdateExpression="SET nearest_airport = :ap, #tz = :tz, utc_offset = :off, updated_at = :u",
            ExpressionAttributeNames={"#tz": "timezone"},
            ExpressionAttributeValues={
                ":ap": icao,
                ":tz": tz_info["tz"],
                ":off": offset_str,
                ":u": datetime.utcnow().isoformat()
            }
        )
        res = users_table.get_item(Key={"telegram_id": telegram_id})
        user = res.get("Item")
        send_settings_menu(chat_id, user_lang, user, message_id=cb["message"]["message_id"])
        return

    elif data == "settings:notify_toggle":
        current_val = user.get("notifications_enabled", True) if user else True
        new_val = not current_val
        users_table.update_item(
            Key={"telegram_id": telegram_id},
            UpdateExpression="SET notifications_enabled = :ne, updated_at = :u",
            ExpressionAttributeValues={":ne": new_val, ":u": datetime.utcnow().isoformat()}
        )
        res = users_table.get_item(Key={"telegram_id": telegram_id})
        user = res.get("Item")
        send_settings_menu(chat_id, user_lang, user, message_id=cb["message"]["message_id"])
        return

    if data.startswith("pl:") or data.startswith("plan:"):
        track_user_activity(users_table, telegram_id, None, action_type="spotting_plan")
        parts = data.split(":")
        if data.startswith("pl:"):
            # pl:{iata}:{icao}:{mode}:{page}:{airline}
            iata = parts[1]
            icao = parts[2]
            filter_mode = parts[3] if len(parts) > 3 else "all"
            page = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 1
            selected_al = parts[5] if len(parts) > 5 else "all"
        else:
            iata = parts[1]
            icao = parts[2]
            filter_mode = parts[3] if len(parts) > 3 else "all"
            page = 1
            selected_al = "all"
        res = users_table.get_item(Key={"telegram_id": telegram_id})
        user = res.get("Item")
        user_lang = detect_user_lang(from_user, user.get("language") if user else None)
        send_spotting_plan(chat_id, telegram_id, iata, icao, users_table, aircraft_table, user, filter_mode=filter_mode, page=page, selected_airline=selected_al, user_lang=user_lang)

    elif data.startswith("atc:"):
        parts = data.split(":")
        iata = parts[1]
        icao = parts[2] if len(parts) > 2 else iata
        res = users_table.get_item(Key={"telegram_id": telegram_id})
        user = res.get("Item")
        user_lang = detect_user_lang(from_user, user.get("language") if user else None)
        send_atc_card(chat_id, iata, icao, user_lang=user_lang)

    elif data.startswith("m3u:"):
        parts = data.split(":")
        iata = parts[1]
        icao = parts[2] if len(parts) > 2 else iata
        res = users_table.get_item(Key={"telegram_id": telegram_id})
        user = res.get("Item")
        user_lang = detect_user_lang(from_user, user.get("language") if user else None)
        send_atc_playlist(chat_id, iata, icao, user_lang=user_lang)

    elif data == "demo_link":
        jp_id = "demo"  # synthetic sample data, see aws_lambda/demo_aircraft.json
        users_table.put_item(Item={
            "telegram_id": telegram_id,
            "jetphotos_id": jp_id,
            "sync_status": "PENDING",
            "is_premium": False,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        })
        send_telegram(
            BOT_TOKEN,
            chat_id,
            t("demo_connecting_msg", user_lang),
            reply_markup=user_reply_kb
        )
        try:
            lambda_client.invoke(
                FunctionName=SYNC_LAMBDA_NAME,
                InvocationType="Event",
                Payload=json.dumps({"telegram_id": telegram_id, "jetphotos_id": jp_id})
            )
        except Exception as e:
            print(f"Error invoking sync lambda for demo: {e}")

    elif data == "stop_radar":
        res = users_table.get_item(Key={"telegram_id": telegram_id})
        user = res.get("Item")
        user_lang = detect_user_lang(from_user, user.get("language") if user else None)
        stop_radar(chat_id, telegram_id, users_table, user_lang=user_lang)

    elif data == "buy_premium":
        send_premium_info(chat_id, user_lang=user_lang)

    elif data == "send_invoice_stars":
        title = t("invoice_title", user_lang)
        description = t("invoice_desc", user_lang)
        price_label = t("invoice_price_label", user_lang)
        send_invoice(
            BOT_TOKEN,
            chat_id,
            title=title,
            description=description,
            payload_str="premium_spotter_30d",
            currency="XTR",
            prices=[{"label": price_label, "amount": 50}]
        )

    elif data.startswith("radar:"):
        track_user_activity(users_table, telegram_id, None, action_type="radar")
        parts = data.split(":")
        minutes = int(parts[1])
        icao = parts[2]

        res = users_table.get_item(Key={"telegram_id": telegram_id})
        user = res.get("Item", {})
        is_premium = user.get("is_premium", False)
        user_lang = detect_user_lang(from_user, user.get("language") or user.get("lang"))

        if minutes > 30 and not is_premium:
            send_telegram(
                BOT_TOKEN,
                chat_id,
                t("radar_prem_limit_warning", user_lang)
            )
            minutes = 30

        expires_at = int(time.time()) + minutes * 60

        users_table.update_item(
            Key={"telegram_id": telegram_id},
            UpdateExpression="SET monitoring_airport = :ap, monitoring_until = :exp, alerted_flights = :af, updated_at = :u",
            ExpressionAttributeValues={
                ":ap": icao,
                ":exp": expires_at,
                ":af": [],
                ":u": datetime.utcnow().isoformat()
            }
        )
        kb = {
            "inline_keyboard": [
                [{"text": t("btn_stop_radar", user_lang), "callback_data": "stop_radar"}]
            ]
        }
        send_telegram(
            BOT_TOKEN,
            chat_id,
            t("radar_activated_msg", user_lang, icao=icao, minutes=minutes),
            reply_markup=kb
        )

    elif data.startswith("facts:"):
        reg = data.split(":", 1)[1].strip()
        country_raw = detect_country(reg, user_lang)
        country = get_airport_country(country_raw, user_lang)
        msg = t("facts_msg", user_lang, reg=reg, reg_lower=reg.lower(), country=country)
        send_telegram(BOT_TOKEN, chat_id, msg)

    elif data == "admin_sync":
        if is_superuser(cb.get("from", {})):
            trigger_admin_sync(chat_id)
        else:
            send_telegram(BOT_TOKEN, chat_id, t("admin_only_msg", user_lang))

    elif data == "back_to_main":
        send_telegram(BOT_TOKEN, chat_id, t("main_menu_title", user_lang), reply_markup=user_reply_kb)


def send_admin_panel(chat_id: int):
    users_table, _ = get_dynamo_tables()
    try:
        resp = users_table.scan()
        users = resp.get("Items", [])
    except Exception as e:
        users = []
        print(f"Error scanning users for admin: {e}")

    total_users = len(users)
    synced_users = sum(1 for u in users if u.get("sync_status") == "COMPLETED")
    premium_users = sum(1 for u in users if u.get("is_premium"))
    total_planes = sum(int(u.get("total_aircraft", 0)) for u in users)
    
    current_time = int(time.time())
    active_radars = sum(1 for u in users if int(u.get("monitoring_until", 0)) > current_time)

    # User interactions and activities
    total_requests = sum(int(u.get("request_count", 0)) for u in users)
    total_lookups = sum(int(u.get("aircraft_lookups", 0)) for u in users)
    total_plans = sum(int(u.get("spotting_plans", 0)) for u in users)
    total_radars = sum(int(u.get("radar_sessions", 0)) for u in users)
    stars_revenue = premium_users * 50

    # Top 5 most active spotters
    sorted_users = sorted(users, key=lambda x: int(x.get("request_count", 0)), reverse=True)[:5]
    top_lines = []
    for idx, u in enumerate(sorted_users, 1):
        un = f"@{u['username']}" if u.get("username") else (u.get("first_name") or str(u.get("telegram_id", "ID")))
        rc = int(u.get("request_count", 0))
        al = int(u.get("aircraft_lookups", 0))
        sp = int(u.get("spotting_plans", 0))
        p_star = " ⭐" if u.get("is_premium") else ""
        top_lines.append(f"{idx}. <b>{un}</b>{p_star} — <b>{rc}</b> действий (🔎 {al} борт., 📋 {sp} план.)")
    top_section = "\n".join(top_lines) if top_lines else "<i>Пока нет активных действий</i>"

    dashboard = (
        f"👑 <b>СУПЕРАДМИН ДАШБОРД / OWNER</b> (@user_not_found_now)\n\n"
        f"👥 <b>Пользователи:</b>\n"
        f"• Всего зарегистрировано: <b>{total_users}</b>\n"
        f"• Активных баз JetPhotos: <b>{synced_users}</b>\n"
        f"• Самолётов в коллекциях: <b>{total_planes}</b>\n\n"
        f"💳 <b>Подписки и Оплаты:</b>\n"
        f"• Активных Premium споттеров: <b>{premium_users}</b>\n"
        f"• Выручка Telegram Stars: <b>⭐️ {stars_revenue} XTR</b>\n\n"
        f"📊 <b>Взаимодействие и Активность:</b>\n"
        f"• Всего запросов (actions): <b>{total_requests}</b>\n"
        f"• Поисков бортов (Global + База): <b>{total_lookups}</b>\n"
        f"• Споттинг-планов сформировано: <b>{total_plans}</b>\n"
        f"• Сессий радара запущено: <b>{total_radars}</b>\n"
        f"• Радаров прямо сейчас: <b>{active_radars}</b> 🟢\n\n"
        f"🏆 <b>Топ активных споттеров:</b>\n"
        f"{top_section}\n\n"
        f"🛠 <b>Команды управления:</b>\n"
        f"• <code>/grant_premium &lt;user_id&gt; &lt;days&gt;</code> — выдать Premium\n"
        f"• <code>/broadcast &lt;текст&gt;</code> — рассылка всем пользователям\n"
        f"• <code>/sync_now</code> — принудительный синк всех баз"
    )

    kb = {
        "inline_keyboard": [
            [{"text": "🔄 Запустить авто-синк базы сейчас", "callback_data": "admin_sync"}],
            [{"text": f"🚀 {t('btn_open_hub_cta', user_lang)}", "web_app": {"url": build_hub_url(user_lang, user_tz, user_airport)}}],
            [{"text": "🔙 Назад в меню", "callback_data": "back_to_main"}]
        ]
    }
    send_telegram(BOT_TOKEN, chat_id, dashboard, reply_markup=kb)


def trigger_admin_sync(chat_id: int):
    try:
        lambda_client.invoke(
            FunctionName=SYNC_LAMBDA_NAME,
            InvocationType="Event",
            Payload=json.dumps({"daily_sync": True})
        )
        send_telegram(BOT_TOKEN, chat_id, "🔄 <b>Синхронизация базы запущена!</b>\n\nLambda <code>planespotter-sync</code> запущена в фоне для всех зарегистрированных споттеров.")
    except Exception as e:
        send_telegram(BOT_TOKEN, chat_id, f"❌ Ошибка запуска синхронизации: {e}")


def execute_broadcast(chat_id: int, broadcast_text: str, users_table):
    try:
        resp = users_table.scan()
        users = resp.get("Items", [])
    except Exception as e:
        send_telegram(BOT_TOKEN, chat_id, f"❌ Ошибка получения пользователей: {e}")
        return

    send_telegram(BOT_TOKEN, chat_id, f"⏳ Начинаю рассылку для {len(users)} пользователей...")
    success = 0
    failed = 0

    announcement = (
        f"📢 <b>ОБЪЯВЛЕНИЕ ОТ PLANESPOTTER TEAM:</b>\n\n"
        f"{broadcast_text}"
    )

    for u in users:
        uid = u.get("telegram_id")
        if not uid:
            continue
        try:
            send_telegram(BOT_TOKEN, int(uid) if str(uid).isdigit() else uid, announcement)
            success += 1
        except Exception as e:
            failed += 1

    send_telegram(BOT_TOKEN, chat_id, f"✅ <b>Рассылка завершена!</b>\n\nУспешно доставлено: {success}\nОшибок: {failed}")
