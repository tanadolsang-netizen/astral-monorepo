from skyfield.api import load
from datetime import datetime, timezone

ts = load.timescale()
eph = load('de421.bsp')
earth = eph['earth']

now_utc = datetime.now(timezone.utc)
t = ts.from_datetime(now_utc)

signs = ['เมษ','พฤษภ','เมถุน','กรกฎ','สิงห์','กันย์','ตุลย์','พิจิก','ธนู','มังกร','กุมภ์','มีน']

def to_sign(lon):
    idx = int(lon // 30)
    deg = lon % 30
    return signs[idx], deg

bodies = {
    'Sun': 'sun',
    'Moon': 'moon',
    'Mercury': 'mercury',
    'Venus': 'venus',
    'Mars': 'mars',
    'Jupiter': 'jupiter barycenter',
    'Saturn': 'saturn barycenter',
    'Uranus': 'uranus barycenter',
    'Neptune': 'neptune barycenter',
    'Pluto': 'pluto barycenter',
}

year_now = now_utc.year + now_utc.timetuple().tm_yday / 365.25
ayanamsa = 23.68 + (year_now - 1997) * (50.29 / 3600)

print("UTC now:", now_utc.isoformat())
print("Lahiri ayanamsa approx:", round(ayanamsa, 2))
print()
print("%-10s %-18s %-18s" % ("Body", "Tropical", "Sidereal(Thai)"))

for name, key in bodies.items():
    astrometric = earth.at(t).observe(eph[key])
    lat, lon, dist = astrometric.ecliptic_latlon()
    trop_lon = lon.degrees % 360
    sid_lon = (trop_lon - ayanamsa) % 360
    ts_, td_ = to_sign(trop_lon)
    ss_, sd_ = to_sign(sid_lon)
    print("%-10s %s %5.2f deg      %s %5.2f deg" % (name, ts_, td_, ss_, sd_))
