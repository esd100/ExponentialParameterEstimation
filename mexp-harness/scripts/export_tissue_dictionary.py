"""Write data/tissue_dictionary.json from mexp.tissue_data (the JSON release of the dictionary)."""
import json, pathlib
from mexp import tissues as TS

out = pathlib.Path(__file__).resolve().parents[1] / "data" / "tissue_dictionary.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(TS.to_json_dict(), indent=1, ensure_ascii=False) + "\n")
print("wrote", out, "entries:", len(TS.keys()), "status summary:", TS.status_summary())
