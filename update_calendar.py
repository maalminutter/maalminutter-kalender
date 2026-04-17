import requests
import json
from datetime import datetime, timedelta

# DINE 8 DBU LINKS
CALS = [
    {"liga": "Superliga", "type": "Kvalifikationsspil", "url": "https://ical.dbu.dk/PoolProgram.ashx?key=3edd88ba-1e4d-43ee-9456-5e0583903066&siteid=2"},
    {"liga": "Superliga", "type": "Mesterskabsspil", "url": "https://ical.dbu.dk/PoolProgram.ashx?key=2e80303e-718b-4acb-a960-bf62e9d7ae25&siteid=2"},
    {"liga": "Betinia Liga", "type": "Kvalifikationsspil", "url": "https://ical.dbu.dk/PoolProgram.ashx?key=0a6e523e-cf39-4d93-b063-be2e5d924d43&siteid=2"},
    {"liga": "Betinia Liga", "type": "Oprykningsspil", "url": "https://ical.dbu.dk/PoolProgram.ashx?key=1ec9d82c-7c75-40cb-9b24-904dda818294&siteid=2"},
    {"liga": "2. division", "type": "Kvalifikationsspil", "url": "https://ical.dbu.dk/PoolProgram.ashx?key=b04544be-f22a-4eb4-8ecb-eea8350058e1&siteid=2"},
    {"liga": "2. division", "type": "Oprykningsspil", "url": "https://ical.dbu.dk/PoolProgram.ashx?key=1a5eea18-b2f3-4ba6-94cb-380f979d0e99&siteid=2"},
    {"liga": "3. division", "type": "Kvalifikationsspil", "url": "https://ical.dbu.dk/PoolProgram.ashx?key=ab453392-e233-4e5d-b322-92ee82cf5a32&siteid=2"},
    {"liga": "3. division", "type": "Oprykningsspil", "url": "https://ical.dbu.dk/PoolProgram.ashx?key=0aaabfda-7059-4fba-bc7f-b59025d7921b&siteid=2"}
]

def parse_ics(text, liga, event_type ):
    events = []
    # Split ved VEVENT og fjern headeren
    blocks = text.split("BEGIN:VEVENT")[1:]
    now = datetime.now()
    # Vi kigger 14 dage frem for at være sikre på at fange alt relevant
    end_date = now + timedelta(days=14)

    for block in blocks:
        summary = ""
        dtstart = ""
        # Find SUMMARY og DTSTART manuelt for at undgå regex-fejl
        for line in block.splitlines():
            line = line.strip()
            if line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()
            elif line.startswith("DTSTART"):
                dtstart = line.split(":")[-1].strip()
        
        if not summary or not dtstart:
            continue
        
        try:
            # Parse dato-formater: YYYYMMDD eller YYYYMMDDTHHMMSSZ
            y, m, d = int(dtstart[:4]), int(dtstart[4:6]), int(dtstart[6:8])
            if "T" in dtstart:
                h, mi = int(dtstart[9:11]), int(dtstart[11:13])
                dt = datetime(y, m, d, h, mi)
            else:
                dt = datetime(y, m, d, 12, 0)
            
            # Filtrer på dato (vi viser kun fremtidige kampe)
            if dt >= now - timedelta(hours=24) and dt <= end_date:
                events.append({
                    "summary": summary,
                    "start": dt.isoformat(),
                    "liga": liga,
                    "type": event_type
                })
        except Exception as e:
            print(f"Fejl ved parsing af event: {e}")
            continue
    return events

all_events = []
print(f"Starter hentning af {len(CALS)} kalendere...")

for cal in CALS:
    try:
        print(f"Henter {cal['liga']} - {cal['type']}...")
        r = requests.get(cal["url"], timeout=15)
        if r.ok:
            found = parse_ics(r.text, cal["liga"], cal["type"])
            all_events.extend(found)
            print(f"Fandt {len(found)} kampe.")
        else:
            print(f"Kunne ikke hente {cal['liga']}: HTTP {r.status_code}")
    except Exception as e:
        print(f"Netværksfejl ved {cal['liga']}: {e}")
        continue

# Sortér alle kampe efter tid
all_events.sort(key=lambda x: x["start"])

print(f"Gemmer i alt {len(all_events)} kampe i kampe.json")
with open("kampe.json", "w", encoding="utf-8") as f:
    json.dump(all_events, f, ensure_ascii=False, indent=2)
