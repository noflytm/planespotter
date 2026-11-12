import time
import os
import boto3
from datetime import datetime
from common import get_dynamo_tables, normalize_reg, detect_country, send_telegram, get_bot_token
from airports import AIRPORTS
from schedule_provider import get_live_flights_near_airport
from jetphotos_api import get_aircraft_live_photo
from i18n import t

def _token():
    return get_bot_token()

def handler(event, context):
    users_table, aircraft_table = get_dynamo_tables()
    current_time = int(time.time())

    # Scan for users with active monitoring sessions
    response = users_table.scan(
        FilterExpression="attribute_exists(monitoring_until) AND monitoring_until > :now",
        ExpressionAttributeValues={":now": current_time}
    )
    active_users = response.get("Items", [])
    print(f"Found {len(active_users)} active monitoring sessions.")

    if not active_users:
        return {"status": "no_active_sessions"}

    # Map airport ICAO to coordinates
    airport_map = {ap["icao"]: ap for ap in AIRPORTS}

    for user in active_users:
        telegram_id = user["telegram_id"]
        icao = user.get("monitoring_airport", "EPGD")
        airport_info = airport_map.get(icao, AIRPORTS[0])

        lat, lon = airport_info["lat"], airport_info["lon"]
        iata = airport_info.get("iata", "GDN")

        flights = get_live_flights_near_airport(lat, lon, airport_iata=iata, airport_icao=icao)
        print(f"User {telegram_id} monitoring {icao}: found {len(flights)} relevant low-altitude/airport flights.")

        already_alerted = set(user.get("alerted_flights", []))
        new_alerts = []

        user_lang = user.get("lang") or user.get("language", "en")

        for f in flights:
            reg = f["reg"]
            norm = normalize_reg(reg)
            if not norm or norm in already_alerted:
                continue

            country = detect_country(reg, user_lang)
            model_str = f["model"] if f.get("model") else "Aircraft"
            flight_str = f"Flight: <b>{f['flight']}</b>\n" if user_lang == "en" else (f"Lot: <b>{f['flight']}</b>\n" if user_lang == "pl" else f"Рейс: <b>{f['flight']}</b>\n") if f.get("flight") and f["flight"] != "N/A" else ""
            route_str = f"Route: {f['origin']} ➔ {f['dest']}\n" if user_lang == "en" else (f"Trasa: {f['origin']} ➔ {f['dest']}\n" if user_lang == "pl" else f"Маршрут: {f['origin']} ➔ {f['dest']}\n") if f.get("origin") or f.get("dest") else ""
            alt_str = f"Alt: <b>{f['altitude']} ft</b>\n" if f.get("altitude") else ""

            # Check for Emergency Squawk (7700, 7600, 7500)
            if f.get("is_emergency"):
                emergency_title = t("radar_alert_emergency", user_lang, squawk=f['squawk'])
                tail_lbl = "Tail" if user_lang == "en" else ("Rejestracja" if user_lang == "pl" else "Борт")
                model_lbl = "Model" if user_lang != "ru" else "Модель"
                msg = (
                    f"{emergency_title}\n\n"
                    f"✈️ {flight_str}"
                    f"🔹 <b>{tail_lbl}:</b> <code>{reg}</code> ({country})\n"
                    f"🔹 <b>{model_lbl}:</b> {model_str}\n"
                    f"{route_str}"
                    f"{alt_str}\n"
                    f"⚠️ SQUAWK {f['squawk']} @ {icao}!"
                )
                kb = {
                    "inline_keyboard": [
                        [{"text": t("radar_btn_fr24", user_lang), "url": f"https://www.flightradar24.com/data/aircraft/{reg}"}],
                        [{"text": t("radar_btn_jp", user_lang), "url": f"https://www.jetphotos.com/registration/{reg}"}]
                    ]
                }
                send_telegram(_token(), int(telegram_id), msg, reply_markup=kb)
                new_alerts.append(norm)
                continue

            # Check for Diverted flight
            if f.get("is_diverted"):
                divert_title = t("radar_alert_divert", user_lang, icao=icao)
                tail_lbl = "Tail" if user_lang == "en" else ("Rejestracja" if user_lang == "pl" else "Борт")
                model_lbl = "Model" if user_lang != "ru" else "Модель"
                msg = (
                    f"{divert_title}\n\n"
                    f"✈️ {flight_str}"
                    f"🔹 <b>{tail_lbl}:</b> <code>{reg}</code> ({country})\n"
                    f"🔹 <b>{model_lbl}:</b> {model_str}\n"
                    f"{route_str}"
                    f"{alt_str}\n"
                    f"🎯 Divert ➔ {icao}!"
                )
                kb = {
                    "inline_keyboard": [
                        [{"text": t("radar_btn_fr24", user_lang), "url": f"https://www.flightradar24.com/data/aircraft/{reg}"}],
                        [{"text": t("radar_btn_jp", user_lang), "url": f"https://www.jetphotos.com/registration/{reg}"}]
                    ]
                }
                send_telegram(_token(), int(telegram_id), msg, reply_markup=kb)
                new_alerts.append(norm)
                continue

            # Regular flight: check if unspotted in user collection
            item = aircraft_table.get_item(Key={"user_id": telegram_id, "reg_norm": norm}).get("Item")
            if not item:
                # UNSPOTTED AIRCRAFT
                mode = f.get("flight_mode", "local")
                is_gnd = f.get("is_on_ground", False)

                if is_gnd:
                    badge = t("radar_alert_unspotted_gnd", user_lang, icao=icao)
                elif mode == "departure":
                    badge = t("radar_alert_unspotted_dep", user_lang, icao=icao)
                elif mode == "arrival":
                    badge = t("radar_alert_unspotted_arr", user_lang, icao=icao)
                else:
                    badge = t("radar_alert_unspotted_air", user_lang, icao=icao)

                # Query live photo from JetPhotos API for unspotted aircraft
                live_photo = get_aircraft_live_photo(reg)
                thumb_url = live_photo.get("thumbnailUrl") if live_photo else None
                if live_photo and live_photo.get("aircraftType") and model_str in ["Самолёт", "Aircraft", "Samolot"]:
                    model_str = live_photo["aircraftType"]

                tail_lbl = "Tail" if user_lang == "en" else ("Rejestracja" if user_lang == "pl" else "Бортовой номер")
                model_lbl = "Model" if user_lang != "ru" else "Модель"
                not_in_coll = t("radar_not_in_collection", user_lang)

                msg = (
                    f"{badge}\n\n"
                    f"✈️ {flight_str}"
                    f"🔹 <b>{tail_lbl}:</b> <code>{reg}</code> ({country})\n"
                    f"🔹 <b>{model_lbl}:</b> {model_str}\n"
                    f"{route_str}"
                    f"{alt_str}\n"
                    f"{not_in_coll}"
                )
                kb = {
                    "inline_keyboard": [
                        [{"text": t("radar_btn_fr24", user_lang), "url": f"https://www.flightradar24.com/data/aircraft/{reg}"}],
                        [{"text": t("radar_btn_jp", user_lang), "url": f"https://www.jetphotos.com/registration/{reg}"}]
                    ]
                }
                send_telegram(_token(), int(telegram_id), msg, reply_markup=kb, photo_url=thumb_url)
                new_alerts.append(norm)

        # Update alerted list to avoid spam
        if new_alerts:
            updated_alerted = list(already_alerted.union(new_alerts))[-50:]
            users_table.update_item(
                Key={"telegram_id": telegram_id},
                UpdateExpression="SET alerted_flights = :af, updated_at = :u",
                ExpressionAttributeValues={
                    ":af": updated_alerted,
                    ":u": datetime.utcnow().isoformat()
                }
            )

    return {"status": "ok", "checked_users": len(active_users)}
