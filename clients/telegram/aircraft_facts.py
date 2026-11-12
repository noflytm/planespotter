import urllib.request
import urllib.parse
import json
import re

HEADERS = {
    "User-Agent": "goSpot/0.1 (+https://github.com/noflytm/planespotter)"
}

def clean_aircraft_name_for_wiki(model: str) -> str:
    # E.g. "Airbus A380-861" -> "Airbus A380"
    # "Boeing 737-8AS(BCF)" -> "Boeing 737"
    # "Boeing 757-223(PCF)" -> "Boeing 757"
    model = re.sub(r"\(.*?\)", "", model).strip()
    m = re.match(r"(Airbus\s+A\d+|Boeing\s+\d+|Embraer\s+\d+|Bombardier\s+CRJ\d+|ATR\s+\d+|Cessna\s+\d+|Piper\s+PA-\d+)", model, re.I)
    if m:
        return m.group(1)
    return model.split("-")[0].strip()

def get_aircraft_facts(reg: str, aircraft_model: str = "", airline: str = ""):
    clean_reg = reg.strip().upper()
    facts = []
    
    links = {
        "Flightradar24": f"https://www.flightradar24.com/data/aircraft/{clean_reg}",
        "Planespotters.net": f"https://www.planespotters.net/search?q={clean_reg}",
        "JetPhotos": f"https://www.jetphotos.com/registration/{clean_reg}",
        "Aviation Safety": f"https://aviation-safety.net/wikibase/dblist.php?Registration={clean_reg}"
    }

    # Wikipedia summary for aircraft family
    if aircraft_model:
        wiki_topic = clean_aircraft_name_for_wiki(aircraft_model)
        wiki_url = f"https://ru.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(wiki_topic)}"
        try:
            req = urllib.request.Request(wiki_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                extract = data.get("extract", "")
                if extract:
                    sentences = extract.split(". ")
                    short_summary = ". ".join(sentences[:2]) + "."
                    facts.append(f"✈️ **О семействе {wiki_topic}:**\n{short_summary}")
        except Exception:
            # Try English Wikipedia if Russian not found
            try:
                en_wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(wiki_topic)}"
                req = urllib.request.Request(en_wiki_url, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=4) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    extract = data.get("extract", "")
                    if extract:
                        sentences = extract.split(". ")
                        short_summary = ". ".join(sentences[:2]) + "."
                        facts.append(f"✈️ **About {wiki_topic}:**\n{short_summary}")
            except Exception:
                pass

    return {
        "reg": clean_reg,
        "facts": facts,
        "links": links
    }

if __name__ == "__main__":
    res = get_aircraft_facts("A6-EOY", "Airbus A380-861", "Emirates")
    print(res)
