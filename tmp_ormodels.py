import json, sys
data = json.load(sys.stdin)
models = data.get("data", [])
z_models = [m for m in models if "z-ai" in m.get("id","").lower() or "glm" in m.get("id","").lower()]
for m in z_models: print(f"{m[\"id\"]} | {m.get(\"name\",\"\")}")
print("--- FREE ---")
free = [m for m in models if ":free" in m.get("id","")]
for m in free: print(f"{m[\"id\"]} | {m.get(\"name\",\"\")}")
