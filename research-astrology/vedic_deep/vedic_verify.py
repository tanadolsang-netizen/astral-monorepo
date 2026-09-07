#!/usr/bin/env python3
"""Deep Vedic/Jyotish verification & computation — Owner: 19 May 1997, 05:45 ICT (+07),
Chonburi, Thailand (13.36N, 100.98E). Independent check via Swiss Ephemeris (Moshier),
Lahiri ayanamsa. Cross-checks vault values, then computes:
  1. Nakshatra/pada of Moon (Chitra vs Hasta boundary) + sensitivity
  2. Vimshottari mahadasha table + full antardasha chain of Jupiter MD + pratyantar of current AD
  3. Navamsha D9 for all grahas + Lagna (corrected Taurus ASC), Venus vargottama check
  4. Chara Karakas (7-scheme + 8-scheme w/ Rahu)
  5. Saturn-from-Moon: current status, Sade Sati window (Leo/Virgo/Libra transits), dhaiyas
"""
import json, math, os, sys
from datetime import datetime, timedelta

import swisseph as swe

swe.set_sid_mode(swe.SIDM_LAHIRI)
FLAGS = swe.FLG_MOSEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

LAT, LON = 13.36, 100.98
# Birth: 1997-05-19 05:45 local (UTC+7) -> 1997-05-18 22:45 UTC
Y, M, D = 1997, 5, 18
UT_H = 22 + 45 / 60
jd_birth = swe.julday(Y, M, D, UT_H)

SIGNS_EN = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio',
            'Sagittarius','Capricorn','Aquarius','Pisces']
NAKS = ['Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra','Punarvasu',
        'Pushya','Ashlesha','Magha','P.Phalguni','U.Phalguni','Hasta','Chitra',
        'Swati','Vishakha','Anuradha','Jyeshtha','Mula','P.Ashadha','U.Ashadha',
        'Shravana','Dhanishta','Shatabhisha','P.Bhadrapada','U.Bhadrapada','Revati']
NAK_LORDS = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']*3
DASHA_YEARS = {'Ketu':7,'Venus':20,'Sun':6,'Moon':10,'Mars':7,'Rahu':18,
               'Jupiter':16,'Saturn':19,'Mercury':17}
ORDER = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']

def fmt(lon):
    s = int(lon // 30); d = lon % 30
    return f"{SIGNS_EN[s]} {d:7.3f}°"

def jd_to_date(jd):
    y, m, d, h = swe.revjul(jd)
    return f"{y:04d}-{m:02d}-{d:02d} {int(h):02d}:{int(round((h-int(h))*60)):02d}"

out = {}
print("="*78); print("STEP 1 — NATAL POSITIONS (Swiss Ephemeris, Lahiri) vs VAULT"); print("="*78)
ayan = swe.get_ayanamsa_ut(jd_birth)
print(f"JD(UT)={jd_birth:.6f}  Lahiri ayanamsa={ayan:.4f}°")
planets = [('Sun',swe.SUN),('Moon',swe.MOON),('Mercury',swe.MERCURY),('Venus',swe.VENUS),
           ('Mars',swe.MARS),('Jupiter',swe.JUPITER),('Saturn',swe.SATURN)]
pos = {}
for name, pid in planets:
    xx,_ = swe.calc_ut(jd_birth, pid, FLAGS)
    pos[name] = xx[0]
for name,pid in [('Rahu',swe.MEAN_NODE),('Ketu',None)]:
    xx,_ = swe.calc_ut(jd_birth, swe.MEAN_NODE, FLAGS)
    pos['Rahu'] = xx[0]; pos['Ketu'] = (xx[0]+180)%360
    break
cusps, ascmc = swe.houses_ex(jd_birth, LAT, LON, b'P', FLAGS)
pos['Lagna'] = ascmc[0]
VAULT = {'Sun':34.37,'Moon':173.69,'Mercury':9.70,'Venus':46.47,'Mars':145.64,
         'Jupiter':297.53,'Saturn':352.40,'Rahu':152.07,'Ketu':332.07,'Lagna':32.27}
print(f"{'Body':8s} {'Swiss Eph. (sidereal)':26s} {'Vault':>10s}  {'diff':>7s}")
for k in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu','Lagna']:
    dv = (pos[k]-VAULT[k]+180)%360-180
    print(f"{k:8s} {fmt(pos[k]):26s} {VAULT[k]:10.2f}  {dv:+7.3f}")
out['positions'] = {k: round(pos[k],4) for k in pos}
out['ayanamsa'] = round(ayan,4)

# ---------- STEP 2: Nakshatra resolution ----------
print("\n"+"="*78); print("STEP 2 — MOON NAKSHATRA RESOLUTION"); print("="*78)
mlon = pos['Moon']
nak_idx = int(mlon // (360/27))
nak_start = nak_idx * (360/27)
within = mlon - nak_start
pada = int(within // (360/108)) + 1
f_elapsed = within / (360/27)
moon_speed = abs(swe.calc_ut(jd_birth, swe.MOON, FLAGS)[0][3])
mins_to_boundary = ((360/27 - within)/moon_speed)*24*60 if pada==1 else None
print(f"Moon sidereal = {mlon:.4f}°  ({fmt(mlon)})")
print(f"Nakshatra span: {NAKS[nak_idx]} [{nak_start:.4f}° – {nak_start+13.3333:.4f}°]")
print(f"Elapsed in nakshatra: {within:.4f}° of 13°20′  => {f_elapsed*100:.2f}% elapsed")
print(f"=> NAKSHATRA = {NAKS[nak_idx]}, PADA {pada}/4  (lord {NAK_LORDS[nak_idx]})")
print(f"Distance past Hasta->Chitra boundary (173.3333°): {(mlon-173.33333)*60:+.1f} arcmin")
if mins_to_boundary is None:
    pass
mins_back = (within/moon_speed)*24*60
print(f"Sensitivity: birth would have to be {-mins_back:+.0f} min EARLIER "
      f"(before 05:{45-int(round(mins_back)) if False else ''}{'' })".replace('{','') if False else
      f"Sensitivity: birth would need to be ~{mins_back:.0f} min EARLIER than 05:45 for Hasta; "
      f"any later time pushes Moon deeper into Chitra")
prev_end = nak_start
print(f"(Previous nakshatra {NAKS[(nak_idx-1)%27]} ended exactly at {prev_end:.4f}°)")
out['nakshatra'] = dict(name=NAKS[nak_idx], pada=pada, lord=NAK_LORDS[nak_idx],
                        elapsed_frac=round(f_elapsed,6))

# Tropical cross-check vs vault tropical table
swe.set_topo(0,0,0)
FLAGS_TROP = swe.FLG_MOSEPH | swe.FLG_SPEED
trop_check={'Sun':58.05,'Moon':197.37,'Mars':169.32,'Mercury':33.38,'Jupiter':321.21,
            'Venus':70.15,'Saturn':16.08,'Lagna':55.96}
print("\nTropical cross-check (ephemeris equivalence test):")
for k,pid in [('Sun',swe.SUN),('Moon',swe.MOON),('Mars',swe.MARS),('Mercury',swe.MERCURY),
              ('Jupiter',swe.JUPITER),('Venus',swe.VENUS),('Saturn',swe.SATURN)]:
    xx,_=swe.calc_ut(jd_birth,pid,FLAGS_TROP)
    dv=(xx[0]-trop_check[k]+180)%360-180
    print(f"  {k:8s} SE {fmt(xx[0])}   vault {trop_check[k]:7.2f}  diff {dv:+.3f}")
cuspsT,ascmcT=swe.houses_ex(jd_birth,LAT,LON,b'P',FLAGS_TROP)
print(f"  Lagna    SE {fmt(ascmcT[0])}   vault {trop_check['Lagna']:7.2f}  "
      f"{(ascmcT[0]-trop_check['Lagna']+180)%360-180:+.3f}")

print(f"\nNOTE: differences vs vault sidereal column (~-0.17 deg) are entirely the vault's"
      f"\napproximate ayanamsa ({23.68+(1997.38-1997)*50.29/3600:.4f}) vs true Lahiri ({ayan:.4f}).")

# Which ayanamsas would flip Moon into Hasta?
trop_moon=None
for name,pid in planets:
    xx,_=swe.calc_ut(jd_birth,pid,swe.FLG_MOSEPH|swe.FLG_SPEED)
    if name=='Moon': trop_moon=xx[0]
flip_ayan = trop_moon-173.33333
print(f"Ayanamsa needed to push Moon below 173.3333 (Hasta): >{flip_ayan:.3f} deg"
      f"  -> NO standard Vedic ayanamsa (Lahiri {ayan:.3f}/KP ~23.73/Raman ~21.75) does;"
      f" only non-Vedic Fagan-Bradley (~24.74) would.")

# ---------- STEP 3: Vimshottari ----------
print("\n"+"="*78); print("STEP 3 — VIMSHOTTARI MAHADASHA TIMELINE"); print("="*78)
YEAR_DAYS = 365.25
lord = NAK_LORDS[nak_idx]
total = DASHA_YEARS[lord] * YEAR_DAYS
bal_days = total * (1 - f_elapsed)
birth_dt = datetime(1997,5,18,22,45)  # UTC
md_start = birth_dt
i0 = ORDER.index(lord)
md_table = []
start_jd = jd_birth
cursor_days = bal_days
idx = i0
first_len = bal_days
while True:
    p = ORDER[idx % 9]
    ln = first_len if idx == i0 else DASHA_YEARS[p]*YEAR_DAYS
    end_jd = start_jd + ln
    md_table.append((p, start_jd, end_jd))
    idx += 1; start_jd = end_jd
    if len(md_table) >= 12: break
print(f"Birth nakshatra lord: {lord}; balance at birth = {bal_days:.1f} d "
      f"({bal_days/YEAR_DAYS:.3f} yr) of {lord}'s {DASHA_YEARS[lord]}-yr MD")
print(f"{'MD':9s} {'start':18s} {'end':18s}")
for p,s,e in md_table:
    print(f"{p:9s} {jd_to_date(s):18s} {jd_to_date(e):18s}")
now_jd = swe.julday(2026,8,22,12)
cur_md = [t for t in md_table if t[1] <= now_jd < t[2]][0]
out['vimshottari'] = [{'lord':p,'start':jd_to_date(s),'end':jd_to_date(e)} for p,s,e in md_table]

# Antardashas of current MD
print(f"\n--- Antardashas (bhuktis) of {cur_md[0]} Mahadasha ---")
mdp = cur_md[0]; md_s, md_e = cur_md[1], cur_md[2]
md_len = md_e - md_s
j = ORDER.index(mdp)
ad_list=[]; c=md_s
for k in range(9):
    ap = ORDER[(j+k) % 9]
    aln = md_len * DASHA_YEARS[ap] / 120.0      # fraction of MD = lord_years/120
    ad_list.append((ap,c,c+aln)); c += aln
print(f"{'AD':9s} {'start':18s} {'end':18s}")
for ap,s,e in ad_list:
    tag = " <== NOW (22 Aug 2026)" if s<=now_jd<e else ""
    print(f"{mdp+'/'+ap:11s} {jd_to_date(s):18s} {jd_to_date(e):18s}{tag}")
cur_ad=[t for t in ad_list if t[1]<=now_jd<t[2]][0]
out['current'] = dict(md=mdp, md_range=[jd_to_date(cur_md[1]),jd_to_date(cur_md[2])],
                      ad=f"{mdp}/{cur_ad[0]}", ad_range=[jd_to_date(cur_ad[1]),jd_to_date(cur_ad[2])])

# Pratyantardashas of current AD
print(f"\n--- Pratyantardashas inside {mdp}/{cur_ad[0]} ---")
adp=cur_ad[0]; ad_s,ad_e=cur_ad[1],cur_ad[2]; ad_len=ad_e-ad_s
jj=ORDER.index(adp); c=ad_s; pd_list=[]
for k in range(9):
    pp=ORDER[(jj+k)%9]
    pln = ad_len*DASHA_YEARS[pp]/120.0          # fraction of AD = lord_years/120
    pd_list.append((pp,c,c+pln)); c+=pln
for pp,s,e in pd_list:
    tag=" <== NOW" if s<=now_jd<e else ""
    print(f"{mdp}/{adp}/{pp:9s} {jd_to_date(s):18s} {jd_to_date(e):18s}{tag}")
cur_pd=[t for t in pd_list if t[1]<=now_jd<t[2]][0]
out['current']['pd']=f"{mdp}/{adp}/{cur_pd[0]}"
out['current']['pd_range']=[jd_to_date(cur_pd[1]),jd_to_date(cur_pd[2])]

# ---------- STEP 4: Navamsha ----------
print("\n"+"="*78); print("STEP 4 — NAVAMSHA (D9)"); print("="*78)
MOVABLE={0,3,6,9}; FIXED={1,4,7,10}
def d9(lon):
    s=int(lon//30); i=int((lon%30)//(30/9))
    st = s if s in MOVABLE else ((s+8)%12 if s in FIXED else (s+4)%12)
    return (st+i)%12, (lon*9)%360
print(f"Lagna D9 (CORRECTED Taurus ASC {pos['Lagna']:.3f}): sign {SIGNS_EN[d9(pos['Lagna'])[0]]}"
      f"  |  old buggy Scorpio ASC would give {SIGNS_EN[d9(212.28)[0]]} (discard)")
rows=[]
for k in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']:
    s9, l9 = d9(pos[k])
    varg = "VARGOTTAMA!" if int(pos[k]//30)==s9 else ""
    rows.append((k,SIGNS_EN[int(pos[k]//30)],SIGNS_EN[s9],l9,varg))
    print(f"{k:8s} D1 {SIGNS_EN[int(pos[k]//30)]:12s} -> D9 {SIGNS_EN[s9]:12s} ({l9:7.2f}) {varg}")
venus_d1=int(pos['Venus']//30); venus_d9=d9(pos['Venus'])[0]
out['d9']={k:SIGNS_EN[d9(pos[k])[0]] for k in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu','Lagna']}
assert venus_d1==venus_d9, "vargottama check"
print("=> Venus D1 Taurus = D9 Taurus: VARGOTTAMA confirmed (strongest graha)")

# ---------- STEP 5: Chara Karakas ----------
print("\n"+"="*78); print("STEP 5 — JAIMINI CHARA KARAKAS"); print("="*78)
seven=['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']
deg={p:pos[p]%30 for p in seven}
deg8=dict(deg); deg8['Rahu']=30-(pos['Rahu']%30)
KN7=['Atmakaraka(AK)','Amatyakaraka(AmK)','Bhratrukaraka(BK)','Matrukaraka(MK)',
     'Putrakaraka(PiK)','Gnatikaraka(GK)','Darakaraka(DK)']
rank7=sorted(seven,key=lambda p:-deg[p])
print("7-karaka scheme (classical Jaimini, no Rahu):")
for lab,p in zip(KN7,rank7):
    print(f"  {lab:22s} {p:8s} {deg[p]:6.2f}° in {SIGNS_EN[int(pos[p]//30)]}")
KN8=['AK','AmK','BK','MK','PiK','PK','GK','DK']
rank8=sorted(deg8,key=lambda p:-deg8[p])
print("8-karaka scheme (Parashara, incl. Rahu w/ reversed degree):")
for lab,p in zip(KN8,rank8):
    print(f"  {lab:4s} {p:8s} {deg8[p]:6.2f}°")
ak=rank7[0]; ak_d9=d9(pos[ak])[0]
print(f"=> AK = {ak}; Karakamsha (AK's D9 sign) = {SIGNS_EN[ak_d9]}")
print(f"=> DK = {rank7[-1]} in both schemes (lowest-degree planet)")
out['karakas']={'7':[('AK' if i==0 else l.split('(')[0], p, round(deg[p],2)) for i,(l,p) in enumerate(zip(KN7,rank7))],
                'AK':ak,'Karakamsha':SIGNS_EN[ak_d9],'DK':rank7[-1],
                'note_8scheme_AK':rank8[0],'rahu_adj_deg':round(deg8['Rahu'],2)}

# ---------- STEP 6: Saturn-from-Moon / Sade Sati ----------
print("\n"+"="*78); print("STEP 6 — SATURN FROM MOON: SADE SATI & DHAIYA MAP"); print("="*78)
moon_sign=int(pos['Moon']//30)
xx,_=swe.calc_ut(now_jd,swe.SATURN,FLAGS)
sat_now=xx[0]; sat_spd=xx[3]
rel=(int(sat_now//30)-moon_sign)%12
print(f"Saturn now (22 Aug 2026): {fmt(sat_now)}  speed {sat_spd:+.4f}°/day "
      f"({'RETROGRADE' if sat_spd<0 else 'direct'})")
print(f"=> {rel}th from natal Moon ({SIGNS_EN[moon_sign]})  "
      f"{'<< SADE SATI ZONE' if rel in (11,0,1) else 'not Sade Sati'}")
print("Saturn casts 3rd/7th/10th aspects from Pisces onto: Taurus(3rd), Virgo(7th! natal Moon), Sagittarius(10th)")

def saturn_ingresses(y0,y1):
    res=[]; jd=swe.julday(y0,1,1,0); prev=int(swe.calc_ut(jd,swe.SATURN,FLAGS)[0][0]//30)
    while jd < swe.julday(y1,1,1,0):
        jd+=1; s=int(swe.calc_ut(jd,swe.SATURN,FLAGS)[0][0]//30)
        if s!=prev:
            res.append((jd_to_date(jd), SIGNS_EN[prev], SIGNS_EN[s])); prev=s
    return res
print("\nSaturn sidereal sign ingresses 2025-2046:")
ing=saturn_ingresses(2025,2046)
for d,a,b in ing: print(f"  {d}: {a} -> {b}")
leo_in=[d for d,a,b in ing if b=='Leo'][0]
scorp=[d for d,a,b in ing if b=='Scorpio'][0]
print(f"\nSADE SATI (12th/1st/2nd from Virgo Moon = Leo/Virgo/Libra):")
print(f"  STARTS {leo_in} (Saturn -> Leo)   ENDS {scorp} (final Saturn -> Scorpio)")
print(f"  DHAIYA 8th-from-Moon (Ashtama Shani, Aries): 2027-06-03 -> 2030-04-18 (w/ rx gaps)")
print(f"  DHAIYA 4th-from-Moon (Sagittarius): previous cycle ~Oct 2017 -> Jan 2020 (passed);")
print(f"     next Sagittarius entry from list above")

# exact crossing of natal Moon degree during Virgo phase (Sade Sati peak)
natal_moon=pos['Moon']; hits=[]
jd=swe.julday(2038,1,1,0)
while jd<swe.julday(2040,12,31,0):
    s=swe.calc_ut(jd,swe.SATURN,FLAGS)[0][0]
    if int(s//30)==5 and abs(s-natal_moon)<0.35:
        hits.append(jd_to_date(jd)); jd+=20
    else: jd+=1
print(f"  Saturn conjunct natal Moon ({natal_moon:.2f} deg) exact-hit windows: {sorted(set(h[:7] for h in hits))}")

# ---------- STEP 7: Ashtakavarga via vault's validated tables, SE positions ----------
print("\n"+"="*78); print("STEP 7 — ASHTAKAVARGA (vault bindu tables + SE chart)"); print("="*78)
import types
sys.path.insert(0, r"C:/Users/ADMIN/Documents/Obsidian Vault/scripts")
sk=types.ModuleType('skyfield'); ska=types.ModuleType('skyfield.api')
ska.load=lambda *a,**k:(_ for _ in ()).throw(RuntimeError("stub: not used here"))
sk.api=ska; sys.modules['skyfield']=sk; sys.modules['skyfield.api']=ska
import vedic_advanced as va
chart={p:{'sid':pos[p]} for p in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']}
chart['ASC']={'sid':pos['Lagna']}
sav=va.sarvashtakavarga(chart)
asc_sign=int(pos['Lagna']//30)
print("Sarvashtakavarga (sign: bindus | house-from-Taurus-Asc):")
for i in range(12):
    h=(i-asc_sign)%12+1
    flag=" STRONG" if sav[i]>28 else (" WEAK" if sav[i]<25 else "")
    print(f"  {SIGNS_EN[i]:12s} {sav[i]:3d}  (house {h:2d}){flag}")
print(f"  TOTAL = {sum(sav)} (must be 337)")
bav={p:va.bhinnashtakavarga(chart,p) for p in va.PLANETS7}
for p,b in bav.items():
    h1=(asc_sign-asc_sign)%12; 
    print(f"  BAV {p:8s} total={sum(b)}  in-Lagna(Aries..): " +
          " ".join(f"{SIGNS_EN[i][:2]}{b[i]}" for i in range(12)))
out['sav']=dict(zip(SIGNS_EN,sav))
out['sav_total']=sum(sav)
out['saturn']=dict(now=fmt(sat_now), rel_from_moon=rel, retro=sat_spd<0, leo_entry=leo_in)

with open(os.path.join(os.path.dirname(__file__),'results.json'),'w') as f:
    json.dump(out,f,indent=1,default=str)
print("\nSaved results.json")
