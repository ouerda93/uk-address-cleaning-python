
import json
import re
import pandas as pd
from pathlib import Path

DOSSIER = Path(__file__).resolve().parent

input_json_path = DOSSIER / "2_samples_demo.json"
output_csv_path = DOSSIER / "output_clean_final_demo.csv"

with open(input_json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

rows = []

for i, item in enumerate(data):
    postcode = str(item.get("RegAddress.PostCode") or "").strip()
    line1 = str(item.get("RegAddress.AddressLine1") or "").strip()
    line2 = str(item.get("RegAddress.AddressLine2") or "").strip()

    match = re.match(r"^(\d+[A-Za-z]?(-\d+)?)(\s|,|$)", line1)

    if match:
        street_number = match.group(1)
        street_name = line1[len(street_number):].strip(", ").strip()
    else:
        street_number = ""
        street_name = line1

    if line2:
        if street_number:
            street_name_final = f"{street_number} {street_name}, {line2}".strip()
        else:
            street_name_final = f"{street_name}, {line2}".strip()
    else:
        street_name_final = (
            f"{street_number} {street_name}".strip()
            if street_number else street_name
        )

    rows.append({
        "texte_index": i,
        "postcode": postcode,
        "street_number": street_number,
        "street_name": street_name,
        "street_name_clean": street_name_final,
        "street_name_clean_final": street_name_final
    })

df = pd.DataFrame(rows)
df.to_csv(output_csv_path, index=False, encoding="utf-8")

print(f"Nettoyage terminé : {len(df)} adresses traitées.")
print(f"CSV généré : {output_csv_path.name}")
