#!/usr/bin/env python3
"""Geocode the TCC property list via Nominatim, baking results into properties.js.

Respects the Nominatim usage policy: <=1 req/sec, descriptive User-Agent.
Falls back to a structured query if the freeform one returns nothing.
"""
import json, time, urllib.parse, urllib.request, sys

PROPS = [
    # (org, name, street, city, zip)
    ("ELACC", "Las Margaritas (Cummings)", "319 Cummings Ave", "Los Angeles", "90033"),
    ("ELACC", "Las Margaritas (115 N Soto)", "115 N Soto St", "Los Angeles", "90033"),
    ("ELACC", "Los Girasoles", "952 S Record Ave", "Los Angeles", "90023"),
    ("ELACC", "Cuatro Vientos", "5331 E Huntington Dr N", "Los Angeles", "90032"),
    ("ELACC", "Paseo del Sol", "417 Soto Street", "Los Angeles", "90033"),
    ("ELACC", "Boyle Hotel - Cummings Block", "1781 E 1st Street", "Los Angeles", "90033"),
    ("ELACC", "Sol y Luna", "2917 E 1st Street", "Los Angeles", "90033"),
    ("ELACC", "Las Mariposas (Evergreen)", "438 Evergreen Ave", "Los Angeles", "90023"),
    ("ELACC", "Las Mariposas (3rd St.)", "2537 E 3rd St", "Los Angeles", "90023"),
    ("ELACC", "Percy Apartments (Percy St.)", "3807 Percy Street", "Los Angeles", "90023"),
    ("ELACC", "Percy Apartments (Indiana St.)", "732 S Indiana St", "Los Angeles", "90023"),
    ("ELACC", "Beswick Senior Apts", "3553 Beswick Street", "Los Angeles", "90023"),
    ("ELACC", "Kern Villa Apartments", "200 N Kern Ave", "Los Angeles", "90022"),
    ("ELACC", "Las Flores", "1063 S Eastman Ave", "Los Angeles", "90023"),
    ("ELACC", "Linda Vista Senior Apts", "630 S St Louis St", "Los Angeles", "90022"),
    ("ELACC", "Alta Vista Apts", "5051 E 3rd Street", "Los Angeles", "90022"),
    ("ELACC", "Whittier Place", "4125 Whittier Blvd", "Los Angeles", "90023"),
    ("ELACC", "Cielito Lindo Apartments I", "2407 E 1st Street", "Los Angeles", "90033"),
    ("ELACC", "Cielito Lindo Apartments II", "2427 E 1st Street", "Los Angeles", "90033"),
    ("ELACC", "530 S Boyle Ave", "530 S Boyle Avenue", "Los Angeles", "90033"),
    ("ELACC", "Blades", "811 Blades Street", "Los Angeles", "90033"),
    ("ELACC", "Eastlake", "3211 Altura Walk", "Los Angeles", "90031"),
    ("ELACC", "Playground Apartments", "1462 N Playground St", "Los Angeles", "90031"),

    ("Esperanza", "Casa Esperanza", "206 E 23rd St", "Los Angeles", "90011"),
    ("Esperanza", "Alegria Apartments", "801 W 23rd St", "Los Angeles", "90007"),
    ("Esperanza", "Villa Esperanza", "255 E 28th St", "Los Angeles", "90011"),
    ("Esperanza", "La Estrella", "1979 Estrella Ave", "Los Angeles", "90007"),
    ("Esperanza", "Budlong", "2727 S Budlong Ave", "Los Angeles", "90007"),
    ("Esperanza", "Amistad", "1959 Estrella Ave", "Los Angeles", "90007"),
    ("Esperanza", "Senderos", "2141 Estrella Ave", "Los Angeles", "90007"),
    ("Esperanza", "39th Street", "1230 W 39th Street", "Los Angeles", "90037"),

    ("LTSC", "Epworth Apartments", "6525 S Normandie Ave", "Los Angeles", "90044"),
    ("LTSC", "Menlo Family Housing", "1230 S Menlo Ave", "Los Angeles", "90006"),
    ("LTSC", "PHD Apartments (20th St.)", "1745 W 20th St", "Los Angeles", "90007"),
    ("LTSC", "PHD Apartments (Arlington Ave.)", "1401 S Arlington Ave", "Los Angeles", "90019"),
    ("LTSC", "PHD Apartments (Kenmore Ave.)", "1400 S Kenmore Ave", "Los Angeles", "90006"),
    ("LTSC", "PHD Apartments (Kingsley Dr.)", "1020 S Kingsley Dr", "Los Angeles", "90006"),
    ("LTSC", "PHD Apartments (Magnolia Ave.)", "1810 Magnolia Ave", "Los Angeles", "90006"),
    ("LTSC", "36th Street & Broadway", "157 E 36th Street", "Los Angeles", "90011"),
    ("LTSC", "Casa Heiwa", "231 E Third St", "Los Angeles", "90013"),
    ("LTSC", "Casa Yonde", "1053 S New Hampshire Ave", "Los Angeles", "90006"),
    ("LTSC", "Cesar Chavez Gardens", "555 W Cesar E Chavez Ave", "Los Angeles", "90012"),
    ("LTSC", "Daimaru Hotel", "345 E First St", "Los Angeles", "90012"),
    ("LTSC", "Durae Senior Apts (Crenshaw)", "906 Crenshaw Blvd", "Los Angeles", "90019"),
    ("LTSC", "Durae Senior Apts (Kingsley)", "540 S Kingsley Dr", "Los Angeles", "90020"),
    ("LTSC", "Hyperion", "2449 Hyperion Ave", "Los Angeles", "90027"),
    ("LTSC", "KYC Apartments", "3987 W 7th St", "Los Angeles", "90005"),
    ("LTSC", "PWC Family Housing", "153 N Glendale Blvd", "Los Angeles", "90026"),
    ("LTSC", "Reno Apartments", "340 S Reno St", "Los Angeles", "90057"),
    ("LTSC", "San Pedro Firm Building", "112 Judge John Aiso St", "Los Angeles", "90012"),
    ("LTSC", "UCA - Union Center for the Arts", "120 Judge John Aiso St", "Los Angeles", "90012"),
]

UA = "TCC-R6-PlanningMap/1.0 (danny@sustento.co)"

def query(params):
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def geocode(street, city, zip_):
    # structured query first (most reliable)
    for params in (
        {"street": street, "city": city, "state": "CA", "postalcode": zip_,
         "country": "USA", "format": "json", "limit": 1},
        {"q": f"{street}, {city}, CA {zip_}", "format": "json", "limit": 1},
        {"q": f"{street}, {city}, CA", "format": "json", "limit": 1},
    ):
        try:
            res = query(params)
        except Exception as e:
            print(f"   ! request error: {e}", file=sys.stderr)
            res = []
        time.sleep(1.1)
        if res:
            return float(res[0]["lat"]), float(res[0]["lon"])
    return None, None

out = []
for i, (org, name, street, city, zip_) in enumerate(PROPS, 1):
    lat, lon = geocode(street, city, zip_)
    status = f"{lat:.5f},{lon:.5f}" if lat else "FAILED"
    print(f"[{i:>2}/{len(PROPS)}] {org:9} {name:34} -> {status}")
    out.append({"org": org, "name": name,
                "address": f"{street}, {city}, CA {zip_}",
                "lat": lat, "lon": lon})

with open("properties.json", "w") as f:
    json.dump(out, f, indent=2)

fails = [p for p in out if p["lat"] is None]
print(f"\nDone. {len(out)-len(fails)}/{len(out)} geocoded. {len(fails)} failed.")
for p in fails:
    print("  FAILED:", p["name"], "-", p["address"])
