#!/usr/bin/env python3
"""Minimal astrology web app — beats Astra on depth, not polish.

Astra (see raw/2026-08-14-astra-life-advice-app-review.md) only does tropical
Sun/Moon/Rising + AI chat. This adds real Vedic depth on top: essential
dignities, sect, Navamsha (D9) + Vargottama, Ashtakavarga, Jaimini Chara
Karakas — all real astronomy (skyfield/JPL DE421), reusing the vault's
already-validated scripts/ (natal_chart.py, vedic_advanced.py) directly.

stdlib http.server only — no Flask/FastAPI dependency for one endpoint.

Usage: python3 server.py [port]  (default 8420)
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from natal_chart import compute_chart, local_to_utc, to_sign, BODIES  # noqa: E402
from tarot import draw_card  # noqa: E402
from vedic_advanced import sarvashtakavarga, chara_karakas, navamsha_sign, sign_index, SIGNS  # noqa: E402

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

# Classical rulerships for essential dignity (domicile/exaltation/detriment/fall).
DOMICILE = {'Sun': ['Leo'], 'Moon': ['Cancer'], 'Mercury': ['Gemini', 'Virgo'],
            'Venus': ['Taurus', 'Libra'], 'Mars': ['Aries', 'Scorpio'],
            'Jupiter': ['Sagittarius', 'Pisces'], 'Saturn': ['Capricorn', 'Aquarius']}
EXALTATION = {'Sun': 'Aries', 'Moon': 'Taurus', 'Mercury': 'Virgo', 'Venus': 'Pisces',
              'Mars': 'Capricorn', 'Jupiter': 'Cancer', 'Saturn': 'Libra'}
OPPOSITE = {i: (i + 6) % 12 for i in range(12)}
SIGN_NAMES_EN = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra',
                  'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']


def dignity(planet, sign_en):
    if planet not in DOMICILE:
        return None
    if sign_en in DOMICILE[planet]:
        return 'Domicile'
    if EXALTATION.get(planet) == sign_en:
        return 'Exaltation'
    exalt_sign = EXALTATION.get(planet)
    if exalt_sign and sign_en == SIGN_NAMES_EN[OPPOSITE[SIGN_NAMES_EN.index(exalt_sign)]]:
        return 'Fall'
    for dom_sign in DOMICILE[planet]:
        if sign_en == SIGN_NAMES_EN[OPPOSITE[SIGN_NAMES_EN.index(dom_sign)]]:
            return 'Detriment'
    return None


def sect(chart, dt_utc, lat_deg, lon_deg):
    """Day chart if the Sun is above the horizon; else night."""
    from skyfield.api import load, wgs84
    ts = load.timescale()
    eph = load('de421.bsp')
    t = ts.from_datetime(dt_utc)
    observer = eph['earth'] + wgs84.latlon(lat_deg, lon_deg)
    alt, _, _ = observer.at(t).observe(eph['sun']).apparent().altaz()
    return 'day' if alt.degrees > 0 else 'night', alt.degrees


def build_report(date_str, time_str, tz, lat, lon, name):
    dt_utc = local_to_utc(date_str, time_str, tz)
    chart = compute_chart(dt_utc, lat, lon)
    sect_label, sun_alt = sect(chart, dt_utc, lat, lon)

    bodies_out = {}
    for b in list(BODIES) + ['ASC']:
        trop_sign, trop_deg = to_sign(chart[b]['trop'])
        sid_sign, sid_deg = to_sign(chart[b]['sid'])
        entry = {
            'tropical': {'sign': trop_sign.split('(')[1].rstrip(')'), 'deg': round(trop_deg, 2)},
            'sidereal': {'sign': sid_sign.split('(')[1].rstrip(')'), 'deg': round(sid_deg, 2)},
        }
        d = dignity(b, trop_sign.split('(')[1].rstrip(')'))
        if d:
            entry['dignity_tropical'] = d
        d = dignity(b, sid_sign.split('(')[1].rstrip(')'))
        if d:
            entry['dignity_sidereal'] = d
        entry['navamsha_sidereal'] = SIGNS[navamsha_sign(chart[b]['sid'])].split('(')[1].rstrip(')')
        if bodies_out.get('Venus') and b == 'Venus':
            pass
        bodies_out[b] = entry

    for b in list(BODIES) + ['ASC']:
        vargottama = SIGN_NAMES_EN[sign_index(chart[b]['sid'])] == bodies_out[b]['navamsha_sidereal']
        bodies_out[b]['vargottama'] = vargottama

    sav = sarvashtakavarga(chart)
    ashtakavarga = [{'sign': SIGNS[i].split('(')[1].rstrip(')'), 'bindus': sav[i],
                      'strong': sav[i] > 28, 'weak': sav[i] < 25} for i in range(12)]

    karakas = [{'role': label, 'planet': planet, 'deg': round(deg, 2)}
               for label, planet, deg in chara_karakas(chart)]

    return {
        'name': name, 'birth_utc': dt_utc.isoformat(), 'ayanamsa': round(chart['_ayanamsa'], 3),
        'sect': sect_label, 'sun_altitude_deg': round(sun_alt, 2),
        'bodies': bodies_out, 'ashtakavarga': ashtakavarga, 'chara_karakas': karakas,
    }


class Handler(BaseHTTPRequestHandler):
    def _json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != '/api/chart':
            return self._json({'error': 'not found'}, 404)
        length = int(self.headers.get('Content-Length', 0))
        try:
            req = json.loads(self.rfile.read(length))
            report = build_report(req['date'], req['time'], float(req.get('tz', 7)),
                                   float(req['lat']), float(req['lon']), req.get('name', 'Subject'))
            self._json(report)
        except Exception as e:
            self._json({'error': str(e)}, 400)

    def do_GET(self):
        path = '/index.html' if self.path == '/' else self.path
        fs_path = os.path.join(STATIC_DIR, path.lstrip('/'))
        if not os.path.abspath(fs_path).startswith(os.path.abspath(STATIC_DIR)) or not os.path.isfile(fs_path):
            return self._json({'error': 'not found'}, 404)
        ctype = 'text/html' if fs_path.endswith('.html') else 'application/javascript' if fs_path.endswith('.js') else 'text/css'
        with open(fs_path, 'rb') as f:
            body = f.read()
        self.send_response(200)
        self.send_header('Content-Type', f'{ctype}; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass  # ponytail: quiet server, no per-request console spam


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8420
    print(f"Astro app: http://localhost:{port}")
    ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()
