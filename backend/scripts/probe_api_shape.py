import sys
import inspect
sys.path.insert(0, ".")

from src.services import parans_service as ps

out = []
out.append("=== public/module functions in parans_service ===")
for nm in sorted(dir(ps)):
    if nm.startswith("__"):
        continue
    obj = getattr(ps, nm)
    if callable(obj) and getattr(obj, "__module__", "") == ps.__name__:
        try:
            sig = str(inspect.signature(obj))
        except (TypeError, ValueError):
            sig = "(?)"
        out.append(f"  {nm}{sig}")

out.append("")
out.append("=== brady_parans return shape ===")
c = ps.brady_parans("1997-05-19", "05:45", 7.0, 13.3611, 100.9847, orb_minutes=8)
out.append(f"  top-level keys: {sorted(c)}")
for k, v in c.items():
    if k == "parans":
        out.append(f"  parans: list of {len(v)} dicts")
        if v:
            out.append(f"    entry keys: {sorted(v[0])}")
            for e in v[:5]:
                out.append("    " + repr(e))
    elif isinstance(v, (list, tuple)):
        out.append(f"  {k}: {type(v).__name__} len={len(v)} first={v[:2]}")
    elif isinstance(v, dict):
        out.append(f"  {k}: dict keys={sorted(v)}")
        for kk, vv in list(v.items())[:6]:
            out.append(f"    {kk} = {vv!r}")
    else:
        out.append(f"  {k}: {type(v).__name__} = {v!r}")

out.append("")
out.append("=== star_positions shape ===")
sp = ps.star_positions(2450587.448636389)
k0 = sorted(sp)[0]
out.append(f"  keys={sorted(sp)}")
out.append(f"  first entry: {k0} -> {sp[k0]!r}")

with open("C:/AI/hermes/data/cache/scratch/api_shape.txt", "w", encoding="utf-8") as fh:
    fh.write("\n".join(out) + "\n")
print("written", len(out), "lines")
