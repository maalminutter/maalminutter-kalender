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
    blocks = text.split("BEGIN:VEVENT")[1:]
    now = datetime.now()
    end_date = now + timedelta(days=14) # Vi henter 14 dage for en sikkerheds skyld

    for block in blocks:
        summary = ""
        dtstart = ""
        for line in block.split("\n"):
            if line.startswith("SUMMARY:"): summary = line.replace("SUMMARY:", "").strip()
            if line.startswith("DTSTART"): dtstart = line.split(":")[-1].strip()
        
        if not summary or not dtstart: continue
        
        try:
            # Parse dato (YYYYMMDD eller YYYYMMDDTHHMMSSZ)
            y, m, d = int(dtstart[:4]), int(dtstart[4:6]), int(dtstart[6:8])
            if "T" in dtstart:
                h, mi = int(dtstart[9:11]), int(dtstart[11:13])
                dt = datetime(y, m, d, h, mi)
            else:
                dt = datetime(y, m, d, 12, 0)
            
            if now <= dt <= end_date:
                events.append({
                    "summary": summary,
                    "start": dt.isoformat(),
                    "liga": liga,
                    "type": event_type
                })
        except: continue
    return events

all_events = []
for cal in CALS:
    try:
        r = requests.get(cal["url"], timeout=10)
        if r.ok:
            all_events.extend(parse_ics(r.text, cal["liga"], cal["type"]))
    except: continue

all_events.sort(key=lambda x: x["start"])

with open("kampe.json", "w", encoding="utf-8") as f:
    json.dump(all_events, f, ensure_ascii=False, indent=2)
