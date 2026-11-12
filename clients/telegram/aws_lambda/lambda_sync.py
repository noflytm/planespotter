import json
import time
import os
import boto3
import urllib.request
import re
from datetime import datetime
import urllib.parse
import polite_http
from common import normalize_reg, get_dynamo_tables, send_telegram, get_bot_token
from i18n import t

DEMO_ID = "demo"

def _token():
    return get_bot_token()

def handler(event, context):
    print("Received sync event:", json.dumps(event))
    
    # Check if this is an EventBridge daily cron or batch sync
    if event.get("source") == "aws.events" or event.get("daily_sync") or "telegram_id" not in event:
        return handle_daily_sync()

    telegram_id = str(event.get("telegram_id", "")).strip()
    jetphotos_id = str(event.get("jetphotos_id", "")).strip()

    if not telegram_id or not jetphotos_id:
        print("Missing telegram_id or jetphotos_id, executing daily batch sync")
        return handle_daily_sync()

    return sync_user(telegram_id, jetphotos_id, notify=True)


def handle_daily_sync():
    """Daily automatic synchronization of all active spotter collections."""
    print("Starting daily automatic synchronization for all users...")
    users_table, aircraft_table = get_dynamo_tables()
    
    try:
        resp = users_table.scan()
        users = resp.get("Items", [])
    except Exception as e:
        print(f"Error scanning users table: {e}")
        return {"status": "error", "message": str(e)}

    synced_count = 0
    now_str = datetime.utcnow().isoformat()

    for u in users:
        tg_id = u.get("telegram_id")
        jp_id = u.get("jetphotos_id")
        if not tg_id:
            continue
        # Only sync users who already completed initial setup
        if u.get("sync_status") in ["COMPLETED", "SYNCING"]:
            print(f"Daily sync: syncing user {tg_id} (JP: {jp_id})...")
            sync_user(tg_id, jp_id, notify=False)
            synced_count += 1

    print(f"Daily sync completed! Total users synced: {synced_count}")
    return {"status": "success", "daily_sync": True, "users_synced": synced_count, "completed_at": now_str}


def get_photographer_stats(photographer_id: str) -> dict:
    base_url = os.environ.get("JETPHOTOS_API_URL", "").rstrip("/")
    clean_id = str(photographer_id).strip()
    url = f"{base_url}/api/jetphotos?id={clean_id}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with polite_http.urlopen(req, timeout=25) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                return data
    except Exception as e:
        print(f"Notice: Failed to fetch photographer stats for {clean_id}: {e}")
    return {}

def sync_user(telegram_id: str, jetphotos_id: str, notify: bool = True):
    users_table, aircraft_table = get_dynamo_tables()

    # Update status to SYNCING
    users_table.update_item(
        Key={"telegram_id": telegram_id},
        UpdateExpression="SET sync_status = :s, updated_at = :u",
        ExpressionAttributeValues={
            ":s": "SYNCING",
            ":u": datetime.utcnow().isoformat()
        }
    )

    is_demo = str(jetphotos_id) == DEMO_ID
    photographer_name = "Demo spotter" if is_demo else f"Photographer #{jetphotos_id}"
    total_photos_count = 0
    aircraft_map = {}
    live_aircraft = []

    if is_demo:
        # Synthetic sample data only: nothing is fetched from any website.
        demo_file = os.path.join(os.path.dirname(__file__), "demo_aircraft.json")
        with open(demo_file, "r", encoding="utf-8") as f:
            for a in json.load(f):
                reg_k = normalize_reg(a.get("reg_code", ""))
                if reg_k:
                    aircraft_map[reg_k] = a
    else:
        # Optional scraping, off unless SCRAPING_ENABLED=1 (see polite_http.py). Without it this finds nothing.
        print(f"Fetching live profile stats for photographer {jetphotos_id}...")
        stats = get_photographer_stats(jetphotos_id)
        if stats and stats.get("photos"):
            try:
                total_photos_count = int(str(stats["photos"]).replace(",", "").strip())
            except Exception:
                total_photos_count = 0
            if stats.get("name"):
                photographer_name = stats["name"].strip()
        print(f"Fetching live JetPhotos aircraft for photographer {jetphotos_id}...")
        live_aircraft, _, live_name = scrape_jetphotos(jetphotos_id, max_pages=1)
        if live_name:
            photographer_name = live_name

    if live_aircraft:
        print(f"Merging {len(live_aircraft)} live aircraft with baseline ({len(aircraft_map)} aircraft)...")
        for a in live_aircraft:
            reg_k = normalize_reg(a.get("reg_code", ""))
            if reg_k:
                aircraft_map[reg_k] = a

    all_aircraft = list(aircraft_map.values())
    if not all_aircraft:
        print("No aircraft found.")
        users_table.update_item(
            Key={"telegram_id": telegram_id},
            UpdateExpression="SET sync_status = :s, updated_at = :u",
            ExpressionAttributeValues={
                ":s": "FAILED",
                ":u": datetime.utcnow().isoformat()
            }
        )
        return {"status": "failed"}

    # Write items to DynamoDB in batches
    print(f"Writing {len(all_aircraft)} unique aircraft to DynamoDB for user {telegram_id}...")
    with aircraft_table.batch_writer() as batch:
        for item in all_aircraft:
            reg = item.get("reg_code", "").strip()
            norm = normalize_reg(reg)
            if not norm:
                continue

            db_item = {
                "user_id": telegram_id,
                "reg_norm": norm,
                "reg_code": reg,
                "aircraft_name": item.get("aircraft_name", ""),
                "airline_name": item.get("airline_name", ""),
                "serial_val": item.get("serial_val", ""),
                "msn": item.get("msn", item.get("serial_val", "")),
                "thumbnail_url": item.get("thumbnail_url", ""),
                "info_url": item.get("info_url", ""),
                "photos_url": item.get("photos_url", f"https://www.jetphotos.com/registration/{reg}"),
                "aircraft_url": item.get("aircraft_url", ""),
                "airline_url": item.get("airline_url", ""),
                "serial_url": item.get("serial_url", ""),
                "photo_count": item.get("photo_count", len(item.get("photos", []))),
                "latest_photo_date": item.get("latest_photo_date", ""),
                "updated_at": datetime.utcnow().isoformat()
            }
            batch.put_item(Item=db_item)

    total_photos_count = max(total_photos_count, len(all_aircraft))

    # Update user record
    users_table.update_item(
        Key={"telegram_id": telegram_id},
        UpdateExpression="SET sync_status = :s, photographer_name = :p, total_photos = :tp, total_aircraft = :ta, last_sync_at = :ls, updated_at = :u",
        ExpressionAttributeValues={
            ":s": "COMPLETED",
            ":p": photographer_name,
            ":tp": total_photos_count,
            ":ta": len(all_aircraft),
            ":ls": datetime.utcnow().isoformat(),
            ":u": datetime.utcnow().isoformat()
        }
    )

    print(f"Sync successfully completed for user {telegram_id}! (Total photos: {total_photos_count}, Total aircraft: {len(all_aircraft)})")

    # Send completion alert to user if requested
    if notify:
        user_lang = "en"
        try:
            resp = users_table.get_item(Key={"telegram_id": telegram_id})
            u_item = resp.get("Item", {})
            user_lang = u_item.get("lang") or u_item.get("language", "en")
        except Exception:
            pass

        msg = (
            f"{t('sync_completed_title', user_lang)}\n\n"
            f"{t('sync_photographer', user_lang)} {photographer_name} (ID: {jetphotos_id})\n"
            f"{t('sync_total_photos', user_lang)} {total_photos_count} {t('sync_photos_unit', user_lang)}\n"
            f"{t('sync_unique_aircraft', user_lang)} {len(all_aircraft)} {t('sync_aircraft_unit', user_lang)}\n\n"
            f"{t('sync_ready_hint', user_lang)}"
        )
        send_telegram(_token(), int(telegram_id) if str(telegram_id).isdigit() else telegram_id, msg)
    return {"status": "success", "aircraft_count": len(all_aircraft), "total_photos": total_photos_count}

def scrape_jetphotos(photographer_id: str, max_pages: int = 20):
    """
    Fetches live aircraft collection from JetPhotos via Cloudflare Worker API.
    Supports pagination and aggregates into unique aircraft list for DynamoDB.
    """
    base_url = os.environ.get("JETPHOTOS_API_URL", "").rstrip("/")
    clean_id = str(photographer_id).strip()
    photographer_name = f"Photographer #{clean_id}"
    all_photos = []

    for page in range(1, max_pages + 1):
        try:
            params = {
                "photographer": f"photographer;{clean_id}",
                "page": str(page)
            }
            url = f"{base_url}/?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with polite_http.urlopen(req, timeout=30) as resp:
                if resp.status != 200:
                    break
                data = json.loads(resp.read().decode("utf-8"))
                photos = data.get("photos", [])
                if not photos:
                    break
                if photos[0].get("photographer"):
                    photographer_name = photos[0]["photographer"]
                all_photos.extend(photos)
                time.sleep(1)
                if len(photos) < 45:
                    break
        except Exception as e:
            print(f"Notice: Page {page} fetch for photographer {clean_id} error: {e}")
            break

    if not all_photos:
        return [], 0, photographer_name

    unique_map = {}
    for p in all_photos:
        reg = p.get("registration", "").strip()
        if not reg or reg == "N/A":
            continue
        norm = normalize_reg(reg)
        if not norm:
            continue

        photo_id = str(p.get("photoId", "")).strip()
        photo_date = str(p.get("photoDate", "")).strip()
        thumb = p.get("thumbnailUrl", "")

        if norm not in unique_map:
            unique_map[norm] = {
                "reg_code": reg,
                "aircraft_name": p.get("aircraftType", ""),
                "airline_name": p.get("airline", ""),
                "serial_val": p.get("msn", ""),
                "msn": p.get("msn", ""),
                "thumbnail_url": thumb,
                "info_url": "",
                "photos_url": f"https://www.jetphotos.com/registration/{reg}",
                "aircraft_url": "",
                "airline_url": p.get("airlineUrl", ""),
                "serial_url": "",
                "photo_count": 1,
                "photo_ids": [photo_id] if photo_id else [],
                "latest_photo_date": photo_date,
            }
        else:
            item = unique_map[norm]
            item["photo_count"] += 1
            if photo_id and photo_id not in item["photo_ids"]:
                item["photo_ids"].append(photo_id)
            if photo_date and photo_date > item.get("latest_photo_date", ""):
                item["latest_photo_date"] = photo_date
                if thumb:
                    item["thumbnail_url"] = thumb

    unique_aircraft = list(unique_map.values())
    print(f"Scraped {len(all_photos)} total photos ({len(unique_aircraft)} unique aircraft) for {photographer_name}")
    return unique_aircraft, len(all_photos), photographer_name
