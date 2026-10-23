# ===== Début du fichier: generate_result.py =====

import json
import re

# Liste des comtés anglais que nous voulons détecter dans le texte.
counties_list = [
    "Greater London", "Lancashire", "Cumbria", "Essex", "Kent",
    "Oxfordshire", "Berkshire", "Hertfordshire", "Surrey", "Merseyside",
    "Greater Manchester", "West Midlands", "West Yorkshire",
    "North Yorkshire"
]


def search_address(text):
    """
    Fonction principale qui extrait les informations d'adresse
    depuis un texte brut.

    Paramètre :
        text (str) : texte brut contenant potentiellement
        le nom de la société, l'adresse, etc.

    Retour :
        dict : informations extraites structurées
        (nom de la société, rue, ville, comté, pays, code postal).
    """

    # 1. Extraction du code postal avec une expression régulière UK.
    postcode_regex = r"[A-Z]{1,2}\d{1,2}[A-Z]?\s*\d[A-Z]{2}"
    postcode_match = re.search(postcode_regex, text, re.IGNORECASE)
    postcode = postcode_match.group(0).strip().upper() if postcode_match else ""

    # 2. Extraction de la ville (PostTown) juste avant le code postal.
    post_town = ""
    if postcode_match:
        before = text[:postcode_match.start()]
        # Récupérer le dernier groupe de mots commençant par une majuscule.
        town_matches = re.findall(r"([A-Z][a-zA-Z\-' ]+)$", before.strip())
        if town_matches:
            post_town = town_matches[-1].strip()

    # 3. Détection du comté s'il est présent dans le texte.
    county = ""
    for c in counties_list:
        if re.search(r"\b" + re.escape(c) + r"\b", text, re.IGNORECASE):
            county = c
            break

    country = "United Kingdom"

    # 4. Extraction de la rue.
    street_regex = r"(\d{1,4}\s+[A-Za-z0-9 ,'\-]+)"
    street_match = re.search(street_regex, text)
    street = street_match.group(0).strip() if street_match else ""

    # 5. Extraction du nom de l'entreprise.
    company = ""
    lines = text.split("\n")
    for line in lines:
        line_clean = line.strip()
        if 5 < len(line_clean) < 100:
            company = line_clean
            break

    # 6. Retour des données structurées.
    return {
        "CompanyName": company,
        "AddressLine1": street,
        "AddressLine2": "",
        "PostTown": post_town,
        "County": county,
        "Country": country,
        "PostCode": postcode
    }

# ===== Début du fichier: test_algo_cto.py =====

import pandas as pd
import re
from pathlib import Path

DEMO_DIR = Path(__file__).resolve().parent

input_file = DEMO_DIR / "output_clean_final_demo.csv"
OUTPUT_CSV = DEMO_DIR / "test_results_demo.csv"

# Fichier de référence annoté manuellement.
# Il doit contenir :
# texte_index, expected_postcode,
# expected_street_number, expected_street_name
REFERENCE_CSV = Path(__file__).resolve().parent / "reference_adresses_demo.csv"

def normalize(value):
    """
    Normalise les valeurs avant comparaison :
    - suppression des espaces inutiles ;
    - passage en majuscules ;
    - gestion des valeurs manquantes.
    """
    if pd.isna(value):
        return ""

    value = str(value).upper().strip()
    value = re.sub(r"\s+", " ", value)
    return value

def run_tests():
    """
    Compare les adresses extraites avec les valeurs
    attendues provenant d'un fichier de référence.
    """
    from pathlib import Path

    input_file = DEMO_DIR / "output_clean_final_demo.csv"

    if not input_file.is_file():
        print(f"❌ Fichier introuvable : {input_file}")
        return

   
    if not Path(REFERENCE_CSV).is_file():
        print(f"❌ Référence introuvable : {REFERENCE_CSV}")
        print(
            "Crée un CSV de référence avec les adresses "
            "vérifiées manuellement avant de lancer les tests."
        )
        return

    df = pd.read_csv(input_file, dtype=str)
    df_ref = pd.read_csv(REFERENCE_CSV, dtype=str)

    required_output = [
        "texte_index",
        "postcode",
        "street_number",
        "street_name_clean_final"
    ]

    required_reference = [
        "texte_index",
        "expected_postcode",
        "expected_street_number",
        "expected_street_name"
    ]

    missing_output = [
        col for col in required_output
        if col not in df.columns
    ]


    missing_reference = [
        col for col in required_reference
        if col not in df_ref.columns
    ]

    if missing_output:
        print(
            f"❌ Colonnes manquantes dans le CSV extrait : "
            f"{missing_output}"
        )
        return

    if missing_reference:
        print(
            f"❌ Colonnes manquantes dans la référence : "
            f"{missing_reference}"
        )
        return

    if df["texte_index"].duplicated().any():
        print("❌ Indices dupliqués dans le fichier extrait.")
        return

    if df_ref["texte_index"].duplicated().any():
        print("❌ Indices dupliqués dans le fichier de référence.")
        return

    # Associer chaque résultat à sa référence.
    merged = df.merge(
        df_ref,
        on="texte_index",
        how="left",
        indicator=True,
        validate="one_to_one"
    )

    results = []
    errors = 0
    unverified = 0

    for _, row in merged.iterrows():

        index = row["texte_index"]

        got_postcode = normalize(row["postcode"])
        got_number = normalize(row["street_number"])
        got_name = normalize(
            row["street_name_clean_final"]
        )

        # Ne pas déclarer OK lorsqu'aucune
        # référence n'existe.
        if row["_merge"] != "both":
            unverified += 1

            results.append({
                "texte_index": index,
                "expected_postcode": "",
                "got_postcode": got_postcode,
                "expected_street_number": "",
                "got_street_number": got_number,
                "expected_street_name": "",
                "got_street_name": got_name,
                "test_ok": "NON VÉRIFIÉ"
            })
            continue

        expected_postcode = normalize(
            row["expected_postcode"]
        )
        expected_number = normalize(
            row["expected_street_number"]
        )
        expected_name = normalize(
            row["expected_street_name"]
        )

        # Comparaison réelle avec les références.
        test_ok = (
            expected_postcode == got_postcode
            and expected_number == got_number
            and expected_name == got_name
        )

        if not test_ok:
            errors += 1

        results.append({
            "texte_index": index,
            "expected_postcode": expected_postcode,
            "got_postcode": got_postcode,
            "expected_street_number": expected_number,
            "got_street_number": got_number,
            "expected_street_name": expected_name,
            "got_street_name": got_name,
            "test_ok": "OK" if test_ok else "NOT OK"
        })

    # Export des résultats des tests.
    pd.DataFrame(results).to_csv(
        OUTPUT_CSV,
        index=False,
        encoding="utf-8"
    )

    total = len(merged)
    verified = total - unverified
    correct = verified - errors

    accuracy = (
        correct / verified * 100
        if verified > 0
        else 0
    )

    print("=" * 50)
    print("RÉSULTATS DES TESTS D'EXTRACTION")
    print("=" * 50)
    print(f"Total des adresses : {total}")
    print(f"Adresses vérifiées : {verified}")
    print(f"Tests corrects : {correct}")
    print(f"Tests incorrects : {errors}")
    print(f"Non vérifiés : {unverified}")

    if verified > 0:
        print(f"Précision sur les lignes vérifiées : {accuracy:.2f}%")
    else:
        print("Précision : non calculable.")

    print(f"Résultats enregistrés : {OUTPUT_CSV}")
    print("=" * 50)


if __name__ == "__main__":
    run_tests()

# ===== Fin du fichier: test_algo_cto.py =====

# ===== Début du fichier: add_city_region.py =====
# Objectif : Ajouter les colonnes "city" et "region"
# à un CSV déjà nettoyé, en utilisant une liste de
# lieux connus au Royaume-Uni.

import pandas as pd
import re
from pathlib import Path

# Dossier principal des résultats.
RESULT_DIR = Path(
    r"C:\Users\girl-\Desktop\Stage_MarketThingsdata"
    r"\Royaume-Uni-entreprises-Sirénisation\Demo"
)

# Fichiers d'entrée et de sortie.
clean_csv = RESULT_DIR / "output_clean_final_demo.csv"
places_csv = (
    RESULT_DIR.parent
    / "OpenData"
    / "uk_places_blacklist.csv"
)
output_csv = RESULT_DIR / "output_with_city_region.csv"

# Vérification des fichiers.
if not clean_csv.is_file():
    raise FileNotFoundError(f"Fichier introuvable : {clean_csv}")

if not places_csv.is_file():
    raise FileNotFoundError(f"Fichier introuvable : {places_csv}")

# Chargement des données.
df = pd.read_csv(clean_csv, dtype=str).fillna("")
places_df = pd.read_csv(places_csv, dtype=str).fillna("")

# Vérification des colonnes nécessaires.
if "street_name_clean_final" not in df.columns:
    raise ValueError(
        "Colonne manquante : street_name_clean_final"
    )

if "name" not in places_df.columns:
    raise ValueError(
        "Colonne manquante : name"
    )

# Normalisation des noms de lieux.
places_df["name"] = (
    places_df["name"].str.upper().str.strip()
)

# La région peut être absente du fichier blacklist.
if "region" not in places_df.columns:
    places_df["region"] = ""

# Supprimer les noms vides.
places_df = places_df[
    places_df["name"] != ""
].copy()

# Trier les noms les plus longs en premier.
places_df["length"] = places_df["name"].str.len()
places_df = places_df.sort_values(
    by="length",
    ascending=False
)

# Préparer la liste des lieux.
places_list = list(
    places_df[["name", "region"]].itertuples(
        index=False,
        name=None
    )
)


def detect_city_region(text):
    """
    Détecte une ville et sa région à partir
    d'un texte contenant une adresse.

    Les noms les plus longs sont prioritaires.
    """
    if pd.isna(text):
        return "", ""

    text_upper = str(text).upper().strip()

    for city, region in places_list:
        pattern = (
            r"(?<![A-Z0-9])"
            + re.escape(city)
            + r"(?![A-Z0-9])"
        )

        if re.search(pattern, text_upper):
            return city, region

    return "", ""


# Détection des villes et régions.
cities = []
regions = []

for street_name in df["street_name_clean_final"]:
    city, region = detect_city_region(street_name)
    cities.append(city)
    regions.append(region)

# Ajout des colonnes.
df["city"] = cities
df["region"] = regions

# Export final.
df.to_csv(
    output_csv,
    index=False,
    encoding="utf-8"
)

print(f"✅ CSV avec ville et région généré : {output_csv}")

# ===== Fin du fichier: add_city_region.py =====


# ===== Début du fichier: prepare_communes.py =====
# Objectif : Préparer une liste de communes
# à partir de la blacklist des lieux UK.

import pandas as pd
import re

# Chargement de la blacklist.
communes_source = (
    RESULT_DIR.parent
    / "OpenData"
    / "uk_places_blacklist.csv"
)
communes_output = RESULT_DIR / "uk_communes_only.csv"

df_communes = pd.read_csv(
    communes_source,
    dtype=str
).fillna("")

# Normalisation.
df_communes["name"] = (
    df_communes["name"].str.upper().str.strip()
)

# Mots à exclure.
forbidden_words = [
    "STREET", "ROAD", "RD", "AVENUE", "AVE",
    "PARK", "ESTATE", "INDUSTRIAL", "MARKET",
    "CLOSE", "SQUARE", "BRIDGE", "BRIDGES",
    "COMMERCIAL", "GREATER", "COUNTY",
    "SHIRE", "MIDLANDS", "MERSEYSIDE",
    "LANCASHIRE", "YORKSHIRE"
]

# Exclure les noms contenant des mots interdits.
pattern = (
    r"\b(?:"
    + "|".join(map(re.escape, forbidden_words))
    + r")\b"
)

mask = ~df_communes["name"].str.contains(
    pattern,
    regex=True,
    na=False
)

df_communes = df_communes[mask].copy()

# Conserver les noms contenant un espace ou un tiret.
# Attention : ce filtre exclut aussi des villes
# valides composées d'un seul mot.
df_communes = df_communes[
    df_communes["name"].str.contains(
        r"[\s-]",
        regex=True,
        na=False
    )
]

# Supprimer les doublons.
df_communes = df_communes.drop_duplicates(
    subset=["name"]
)

# Trier par longueur décroissante.
df_communes["length"] = (
    df_communes["name"].str.len()
)

df_communes = df_communes.sort_values(
    by="length",
    ascending=False
)

# Export des communes.
df_communes[["name"]].to_csv(
    communes_output,
    index=False,
    encoding="utf-8"
)

print(
    f"✅ Étape 1 terminée : {communes_output}"
)

# ===== Fin du fichier: prepare_communes.py =====


# ===== Début du fichier: step_city_from_raw_text.py =====
# Objectif : Détecter la ville et la région
# à partir du texte brut des adresses.

import pandas as pd
import json
import re

# Fichiers sources.
csv_input_path = RESULT_DIR / "output_with_city_region.csv"
json_input_path = RESULT_DIR / "2_samples_demo.json"
communes_csv_path = RESULT_DIR / "uk_communes_only.csv"
csv_output_path = RESULT_DIR / "output_with_city_region.csv"

# Chargement du CSV.
df = pd.read_csv(
    csv_input_path,
    dtype=str
).fillna("")

# Chargement du JSON.
with open(json_input_path, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# Chargement des communes.
communes_df = pd.read_csv(
    communes_csv_path,
    dtype=str
).fillna("")

communes_list = sorted(
    communes_df["name"].dropna().str.upper().tolist(),
    key=len,
    reverse=True
)

# Création du dictionnaire des textes bruts.
raw_dict = {}

for item in raw_data:
    postcode = str(
        item.get("RegAddress.PostCode") or ""
    ).upper().strip()

    if not postcode:
        continue

    raw_dict[postcode] = {
        "raw_text": str(item.get("raw_text") or ""),
        "region": str(
            item.get("RegAddress.County") or ""
        )
    }


def detect_city(raw_text):
    """
    Recherche une ville dans le texte brut,
    à partir de la liste des communes UK.
    """
    if not raw_text:
        return ""

    text_upper = str(raw_text).upper()

    for commune in communes_list:
        pattern = (
            r"(?<![A-Z0-9])"
            + re.escape(commune)
            + r"(?![A-Z0-9])"
        )

        if re.search(pattern, text_upper):
            return commune

    return ""


# Détection des villes et régions.
cities = []
regions = []

for _, row in df.iterrows():

    postcode = str(
        row.get("postcode") or ""
    ).upper().strip()

    reference = raw_dict.get(postcode, {})

    raw_text = reference.get("raw_text", "")
    region = reference.get("region", "")

    city_found = detect_city(raw_text)

    # Conserver la ville existante si aucune
    # nouvelle ville n'a été détectée.
    existing_city = str(row.get("city") or "")

    city_final = (
        city_found if city_found else existing_city
    )

    cities.append(city_final)
    regions.append(region.upper().strip())

# Ajout des colonnes.
df["city"] = cities
df["region"] = regions

# Export des résultats.
df.to_csv(
    csv_output_path,
    index=False,
    encoding="utf-8"
)

print(f"✅ Fichier généré : {csv_output_path}")

# ===== Fin du fichier: step_city_from_raw_text.py =====

# ===== Début du fichier: add_city_region.py =====
# Deuxième occurrence dans le fichier original.
# Objectif : ajouter les colonnes city et region.

# Cette section reprend le traitement précédent.
# Pour éviter de relire et de réécrire les mêmes fichiers,
# elle reste ici comme repère de ton code original.
#
# Fichiers utilisés :
# - Demo/output_clean_final_demo.csv
# - Demo/uk_places_blacklist.csv
# - Demo/output_with_city_region.csv

# ===== Fin du fichier: add_city_region.py =====


# ===== Début du fichier: prepare_communes.py =====
# Deuxième occurrence dans le fichier original.
# Objectif : préparer la liste des communes UK.

# Ce traitement a déjà été défini dans la partie précédente.
# On évite de l'exécuter une deuxième fois.
#
# Entrée :
# Demo/uk_places_blacklist.csv
#
# Sortie :
# Demo/uk_communes_only.csv

# ===== Fin du fichier: prepare_communes.py =====


# ===== Début du fichier: step_city_from_raw_text.py =====
# Deuxième occurrence dans le fichier original.
# Objectif : détecter les villes dans les textes bruts.

# Le traitement a déjà été exécuté dans la partie précédente.
# Cette répétition est conservée comme repère.
#
# Entrées :
# - Demo/output_with_city.csv
# - Demo/2_samples_demo.json
# - Demo/uk_communes_only.csv
#
# Sortie :
# Demo/output_with_city_region.csv

# ===== Fin du fichier: step_city_from_raw_text.py =====


# ===== Début du fichier: step_test_city_region.py =====
# Objectif : vérifier la qualité de la détection
# des villes et des régions.
#
# Comparaison entre :
# - la ville détectée dans le texte brut ;
# - la ville officielle du fichier JSON.
#
# La région officielle est également conservée
# dans le CSV de résultats.

import json
import pandas as pd
import re
from pathlib import Path

# Fichiers d'entrée et de sortie.
json_file_path = RESULT_DIR / "2_samples_demo.json"
uk_cities_csv_path = RESULT_DIR / "uk_communes_only.csv"
output_csv_path = RESULT_DIR / "output_with_city_region_final.csv"

# Vérification des fichiers.
if not json_file_path.is_file():
    raise FileNotFoundError(
        f"Fichier JSON introuvable : {json_file_path}"
    )

if not uk_cities_csv_path.is_file():
    raise FileNotFoundError(
        f"Fichier des communes introuvable : {uk_cities_csv_path}"
    )


def normalize_city_region(text):
    """
    Normalise les noms des villes et régions :
    - passage en majuscules ;
    - remplacement des tirets et virgules ;
    - suppression des espaces multiples.
    """
    if not isinstance(text, str):
        return ""

    text = text.upper()
    text = re.sub(r"[-,]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# Lecture du JSON.
with open(json_file_path, "r", encoding="utf-8") as f:
    data_json = json.load(f)

# Lecture des communes UK.
df_ref = pd.read_csv(
    uk_cities_csv_path,
    dtype=str
).fillna("")

# Vérifier la présence de la colonne name.
if "name" not in df_ref.columns:
    raise ValueError(
        "La colonne 'name' est absente du fichier des communes."
    )

# Normalisation des noms de villes.
cities_list = (
    df_ref["name"]
    .apply(normalize_city_region)
    .drop_duplicates()
    .tolist()
)

# Retirer les noms vides.
cities_list = [
    city for city in cities_list if city
]

# Trier les noms les plus longs en premier.
cities_list.sort(key=len, reverse=True)

results = []

# Compteurs pour les résultats.
total_tests = 0
tests_ok = 0
tests_not_ok = 0
tests_without_reference = 0

# Parcours des entrées du JSON.
for idx, entry in enumerate(data_json):

    # Texte brut.
    raw_text = normalize_city_region(
        entry.get("raw_text", "")
    )

    # Ville officielle.
    json_city = normalize_city_region(
        entry.get("RegAddress.PostTown", "")
    )

    # Région officielle.
    json_region = normalize_city_region(
        entry.get("RegAddress.County", "")
    )

    # Détection automatique de la ville.
    detected_city = ""

    for city in cities_list:

        pattern = (
            r"(?<![A-Z0-9])"
            + re.escape(city)
            + r"(?![A-Z0-9])"
        )

        if re.search(pattern, raw_text):
            detected_city = city
            break

    # Comparaison avec la ville officielle.
    # Si la référence est absente, on ne déclare
    # pas le test comme réussi.
    if not json_city:
        test_city_region = "NON VÉRIFIÉ"
        tests_without_reference += 1

    elif detected_city == json_city:
        test_city_region = "OK"
        tests_ok += 1
        total_tests += 1

    else:
        test_city_region = "NOT OK"
        tests_not_ok += 1
        total_tests += 1

    # Enregistrement du résultat.
    results.append({
        "texte_index": idx,
        "postcode": entry.get(
            "RegAddress.PostCode", ""
        ),
        "street_name": entry.get(
            "RegAddress.AddressLine1", ""
        ),
        "city_detected": detected_city,
        "city_json": json_city,
        "region_json": json_region,
        "test_city_region": test_city_region
    })

# Création du DataFrame final.
df_results = pd.DataFrame(
    results,
    columns=[
        "texte_index",
        "postcode",
        "street_name",
        "city_detected",
        "city_json",
        "region_json",
        "test_city_region"
    ]
)

# Export CSV.
df_results.to_csv(
    output_csv_path,
    index=False,
    encoding="utf-8"
)

# Calcul du taux de réussite sur les lignes vérifiées.
accuracy = (
    tests_ok / total_tests * 100
    if total_tests > 0
    else 0
)

print("=" * 50)
print("RÉSULTATS DES TESTS VILLE")
print("=" * 50)
print(f"Total des adresses : {len(data_json)}")
print(f"Tests vérifiés : {total_tests}")
print(f"Tests OK : {tests_ok}")
print(f"Tests NOT OK : {tests_not_ok}")
print(f"Références absentes : {tests_without_reference}")

if total_tests > 0:
    print(f"Taux de réussite ville : {accuracy:.2f}%")
else:
    print("Taux de réussite : non calculable.")

print(f"CSV généré : {output_csv_path}")
print("=" * 50)

# ===== Fin du fichier: step_test_city_region.py =====

# ===== Début du fichier: ton_script.py =====
# Objectif : compléter la colonne "city" à partir
# du texte brut et de la liste des communes UK.
# Les villes déjà renseignées sont conservées.

import pandas as pd
import json
import re
from pathlib import Path

json_file = RESULT_DIR / "2_samples_demo.json"
communes_file = RESULT_DIR / "uk_communes_only.csv"
output_file = RESULT_DIR / "output_with_city_filled.csv"

# Lecture des communes.
df_communes = pd.read_csv(
    communes_file,
    dtype=str
).fillna("")

communes = sorted(
    {
        name.upper().strip()
        for name in df_communes["name"]
        if name.strip()
    },
    key=len,
    reverse=True
)

# Lecture du JSON.
with open(json_file, "r", encoding="utf-8") as f:
    data_json = json.load(f)

df = pd.DataFrame(data_json)

# Ajouter la colonne city si elle n'existe pas.
if "city" not in df.columns:
    df["city"] = ""


def detect_city_from_text(text):
    """
    Détecte une commune dans un texte brut.
    Priorité aux noms les plus longs.
    """
    if not isinstance(text, str) or not text.strip():
        return ""

    text_upper = text.upper()

    for commune in communes:
        pattern = (
            r"(?<![A-Z0-9])"
            + re.escape(commune)
            + r"(?![A-Z0-9])"
        )

        if re.search(pattern, text_upper):
            return commune

    return ""


def complete_city(row):
    """
    Conserve la ville existante si elle est renseignée.
    Sinon, recherche une ville dans raw_text.
    """
    existing_city = row.get("city", "")

    if pd.notna(existing_city) and str(existing_city).strip():
        return str(existing_city).strip()

    return detect_city_from_text(
        row.get("raw_text", "")
    )


# Compléter les villes manquantes.
df["city"] = df.apply(
    complete_city,
    axis=1
)

# Supprimer raw_text du CSV de sortie.
# Le fichier JSON source n'est pas modifié.
if "raw_text" in df.columns:
    df = df.drop(columns=["raw_text"])

# Export CSV.
df.to_csv(
    output_file,
    index=False,
    encoding="utf-8"
)

print(f"✅ Fichier généré : {output_file}")

# ===== Fin du fichier: ton_script.py =====


# ===== Début du fichier: corriger_ok_csv.py =====
# Objectif : conserver les vrais résultats des tests
# sans remplacer artificiellement NOT OK par OK.

import pandas as pd

input_csv = RESULT_DIR / "output_with_city_region_final.csv"
output_csv = RESULT_DIR / "output_test_ok_corrected.csv"

# Lecture du CSV.
df = pd.read_csv(
    input_csv,
    dtype=str
).fillna("")

# Vérification des colonnes.
if "test_city_region" not in df.columns:
    raise ValueError(
        "Colonne manquante : test_city_region"
    )

if "postcode" not in df.columns:
    raise ValueError(
        "Colonne manquante : postcode"
    )

# Normaliser les résultats existants.
df["test_city_region"] = (
    df["test_city_region"]
    .str.upper()
    .str.strip()
)

# Ne jamais forcer les résultats à OK.


def classify_row(row):
    """
    Classe les lignes selon le résultat du test.

    Cette classification ne prétend pas calculer
    les vrais positifs et vrais négatifs sans
    données de référence suffisantes.
    """
    test_result = row["test_city_region"]

    if test_result == "OK":
        return "Correspondance correcte"

    if test_result in ("NOT OK", "NON OK", "KO"):
        return "Correspondance incorrecte"

    return "Non vérifié"


# Ajouter le type de résultat.
df["type_test"] = df.apply(
    classify_row,
    axis=1
)

# Export CSV.
df.to_csv(
    output_csv,
    index=False,
    encoding="utf-8"
)

print(f"✅ CSV corrigé généré : {output_csv}")

# ===== Fin du fichier: corriger_ok_csv.py =====
