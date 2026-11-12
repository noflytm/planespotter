import os
import re
import json
import urllib.request
import urllib.parse
import polite_http

JETPHOTOS_SEARCH_URL = "https://www.jetphotos.com/showphotos.php"
JETPHOTOS_API_ENDPOINT = os.environ.get("JETPHOTOS_API_URL", "").rstrip("/")

BROWSER_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.jetphotos.com/",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}

def search_jetphotos(
    keywords: str,
    keywords_type: str = "reg",
    sort_order: int = 0,
    page: int = 1,
    limit: int = 20
) -> dict:
    """
    Search JetPhotos via roowus/JetPhotos-API endpoint (with local/edge proxy fallback).
    """
    clean_kw = keywords.strip()
    if not clean_kw:
        return {"count": 0, "photos": []}

    # 1. First attempt: Use the fast JetPhotos API (Cloudflare Worker / Tunnel)
    if JETPHOTOS_API_ENDPOINT:
        try:
            api_params = {
                "page": str(page),
                "sort-order": str(sort_order),
                "keywords": clean_kw,
                "keywords-type": keywords_type,
                "keywords-contain": "0" if keywords_type == "reg" else "3"
            }
            api_url = f"{JETPHOTOS_API_ENDPOINT}/?{urllib.parse.urlencode(api_params)}"
            req = urllib.request.Request(api_url, headers={"Accept": "application/json"})
            with polite_http.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    if data.get("photos"):
                        return {
                            "count": len(data["photos"]),
                            "photos": data["photos"][:limit],
                            "source": "api"
                        }
        except Exception as e:
            print(f"Notice: JetPhotos API endpoint ({JETPHOTOS_API_ENDPOINT}) error: {e}. Falling back to direct query.")

    # 2. Fallback attempt: Direct HTML query with browser headers
    params = {
        "page": str(page),
        "sort-order": str(sort_order),
        "keywords-contain": "0" if keywords_type == "reg" else "3",
        "keywords-type": keywords_type,
        "keywords": clean_kw,
        "aircraft": "all",
        "airline": "all",
        "country-location": "all",
        "photo-year": "all",
        "photographer-group": "all",
        "category": "all",
        "genre": "all",
        "search-type": "Advanced"
    }

    url = f"{JETPHOTOS_SEARCH_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers=BROWSER_HEADERS)

    try:
        with polite_http.urlopen(req, timeout=3) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Error querying JetPhotos direct search for {clean_kw}: {e}")
        return {"count": 0, "photos": [], "error": str(e)}

    # Parse HTML cards
    parts = html.split('<div class="result"')
    photos = []

    for part in parts[1:]:
        if len(photos) >= limit:
            break

        m_id = re.search(r'data-photo=[\"\x27](\d+)[\"\x27]', part)
        photo_id = m_id.group(1) if m_id else ""

        m_img = re.search(r'src=[\"\x27](//cdn\.jetphotos\.com/[^\"\x27]+)[\"\x27]', part)
        if not m_img:
            m_img = re.search(r'data-src=[\"\x27](//cdn\.jetphotos\.com/[^\"\x27]+)[\"\x27]', part)
        
        raw_thumb = ("https:" + m_img.group(1)) if m_img else ""
        thumbnail_url = raw_thumb
        image_url = thumbnail_url.replace("/400/", "/full/") if "/400/" in thumbnail_url else thumbnail_url
        photo_page_url = f"https://www.jetphotos.com/photo/{photo_id}" if photo_id else ""

        m_reg = re.search(r'<a\s+href=[\"\x27]/registration/([^\"\x27]+)[\"\x27][^>]*>(.*?)</a>', part)
        registration = m_reg.group(2).strip() if m_reg else ""
        if not registration:
            m_reg2 = re.search(r'/registration/([A-Z0-9\-_]+)', part)
            registration = m_reg2.group(1).strip() if m_reg2 else clean_kw

        m_model = re.search(r'<a\s+href=[\"\x27]/aircraft/([^\"\x27]+)[\"\x27][^>]*>(.*?)</a>', part)
        aircraft_type = m_model.group(2).strip() if m_model else ""

        m_al = re.search(r'<a\s+href=[\"\x27]/airline/([^\"\x27]+)[\"\x27][^>]*>(.*?)</a>', part)
        airline = m_al.group(2).strip() if m_al else ""

        m_sn = re.search(r'Serial\s*#:\s*<a\s+href=[\"\x27][^\"\x27]+[\"\x27][^>]*>(.*?)</a>', part)
        msn = m_sn.group(1).strip() if m_sn else ""

        m_ph = re.search(r'<a\s+href=[\"\x27]/photographer/([^\"\x27]+)[\"\x27][^>]*>(.*?)</a>', part)
        photographer = m_ph.group(2).strip() if m_ph else ""

        m_loc = re.search(r'<a\s+href=[\"\x27]/airport/([^\"\x27]+)[\"\x27][^>]*>(.*?)</a>', part)
        location = m_loc.group(2).strip() if m_loc else ""

        m_date = re.search(r'Photo date:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})', part)
        photo_date = m_date.group(1) if m_date else ""

        if photo_id or registration:
            photos.append({
                "photoId": photo_id,
                "thumbnailUrl": thumbnail_url,
                "imageUrl": image_url,
                "photoPageUrl": photo_page_url,
                "registration": registration,
                "aircraftType": aircraft_type,
                "airline": airline,
                "msn": msn,
                "photographer": photographer,
                "location": location,
                "photoDate": photo_date
            })

    return {
        "count": len(photos),
        "photos": photos,
        "source": "html"
    }


def fetch_planespotters_photo(registration: str) -> dict:
    clean_reg = registration.upper().strip()
    url = f"https://api.planespotters.net/pub/photos/reg/{clean_reg}"
    req = urllib.request.Request(url, headers={"User-Agent": "PlaneSpotterBot/1.0 (+https://t.me/plainspotter_bot)"})
    try:
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            photos = data.get("photos", [])
            if photos:
                p = photos[0]
                thumb = p.get("thumbnail_large", {}).get("src") or p.get("thumbnail", {}).get("src", "")
                return {
                    "photoId": str(p.get("id", "")),
                    "thumbnailUrl": thumb,
                    "imageUrl": thumb,
                    "photoPageUrl": p.get("link", ""),
                    "registration": clean_reg,
                    "photographer": p.get("photographer", ""),
                    "source": "planespotters"
                }
    except Exception as e:
        print(f"Notice: Planespotters API lookup error for {clean_reg}: {e}")
    return {}


def get_aircraft_live_photo(registration: str) -> dict:
    clean_reg = registration.upper().strip()

    # 1. Fast path: Planespotters public API (responds in ~80ms, 24/7 reliability in AWS Lambda)
    try:
        ps_photo = fetch_planespotters_photo(clean_reg)
        if ps_photo and ps_photo.get("thumbnailUrl"):
            return ps_photo
    except Exception as e:
        print(f"Notice: Planespotters lookup error for {clean_reg}: {e}")

    # 2. Fallback to JetPhotos search
    try:
        res = search_jetphotos(clean_reg, keywords_type="reg", sort_order=0, limit=1)
        if res.get("photos"):
            return res["photos"][0]
    except Exception as e:
        print(f"JetPhotos lookup error for {clean_reg}: {e}")

    return {}
