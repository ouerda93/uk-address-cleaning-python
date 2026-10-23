# UK Address Cleaning & Enrichment Pipeline
### Projet Data Analyst — Python, Pandas, SQL & MySQL

## 1. Présentation du projet

Ce projet a été réalisé dans le cadre de mon stage en analyse de données chez **Markethings**.

Il porte sur le traitement, le nettoyage, la structuration et l'enrichissement d'adresses d'entreprises britanniques, notamment à partir de données de **Companies House**.

Les données sources sont hétérogènes (CSV, JSON), parfois incomplètes, bruitées ou non normalisées.

**Objectif principal :** transformer ces données brutes en informations structurées, cohérentes et exploitables pour l'analyse, les croisements de données et les traitements métiers.

## 2. Objectifs techniques

- Explorer et traiter plusieurs millions d'enregistrements.
- Détecter et contrôler les codes postaux britanniques (*postcodes*).
- Extraire les numéros et les noms de rues.
- Nettoyer et normaliser les adresses.
- Identifier les villes et les communes.
- Enrichir les informations géographiques (county, région).
- Réduire les faux positifs à l'aide de listes de référence et d'exclusion.
- Contrôler les résultats à partir d'échantillons JSON annotés.
- Préparer les données pour leur exploitation en CSV et MySQL.

## 3. Technologies utilisées

| Technologie | Utilisation |
|---|---|
| Python | Développement des scripts de traitement |
| Pandas | Nettoyage et manipulation des données |
| SQL / MySQL | Stockage, exploration et contrôle des données |
| Regex | Détection des codes postaux et extraction textuelle |
| JSON / CSV | Lecture, traitement et export des données |
| Visual Studio Code | Environnement de développement |
| Git / GitHub | Versionnement et présentation du projet |

## 4. Données utilisées

### Données brutes

- Fichiers CSV contenant des informations d'entreprises britanniques.
- Fichiers JSON contenant des textes d'adresses et des exemples annotés.

### Données de référence

- Référentiel de codes postaux britanniques.
- Listes de villes, communes et régions du Royaume-Uni.
- Listes d'exclusion (*blacklists*) pour limiter les correspondances incorrectes.

## 5. Architecture du pipeline

Le pipeline décrit dans la documentation technique suit une logique séquentielle.

### Étape 1 — Détection des codes postaux

Identification des postcodes britanniques dans les textes à l'aide d'expressions régulières et comparaison avec une base de référence.

### Étape 2 — Extraction du numéro de rue

Recherche des numéros de rue en distinguant les éléments d'adresse des informations parasites telles que `FLAT`, `UNIT` ou `BUILDING`.

### Étape 3 — Nettoyage du nom de rue

Normalisation du texte et extraction du nom de rue, en tenant compte des éléments administratifs ou géographiques pouvant apparaître dans l'adresse.

### Étape 4 — Détection de la ville

Recherche des villes et communes à partir du texte nettoyé et des listes de référence.

### Étape 5 — Enrichissement géographique

Utilisation des informations disponibles pour identifier ou compléter les champs relatifs aux villes, counties et régions.

### Étape 6 — Contrôle et validation

Comparaison des valeurs extraites avec des références annotées, identification des anomalies et analyse des résultats.

L'ordre de traitement vise à limiter les faux positifs et à améliorer la cohérence des informations extraites.

## 6. Scripts documentés dans le projet professionnel

La documentation technique du projet décrit notamment les composants suivants :

| Script | Fonction décrite |
|---|---|
| `detect_postcode.py` | Détection et validation des codes postaux |
| `clean_street_number.py` | Extraction des numéros de rue |
| `clean_street_name.py` | Nettoyage des noms de rues |
| `prepare_communes.py` | Préparation des listes de communes |
| `add_city_region.py` | Détection des villes et régions |
| `step_city_from_raw_text.py` | Exploitation du texte brut et des métadonnées |
| `step_test_city_region.py` | Comparaison des résultats avec les références JSON |
| `corriger_ok.py` | Analyse et correction des classifications |

**Remarque :** cette section décrit les composants mentionnés dans la documentation du stage. Elle ne signifie pas que tous ces scripts sont inclus ou directement exécutables dans ce dépôt public.

## 7. Traitement des données à grande échelle

Le projet a mobilisé des bases de données MySQL contenant plusieurs millions d'enregistrements.

Les volumes suivants ont été retrouvés lors de l'exploration des bases :

| Table MySQL | Volume |
|---|---:|
| `uk_companies.final_addresses_checked` | 5 681 537 lignes — comptage exact |
| `uk_companies.final_addresses_validated` | 5 681 543 lignes — comptage exact |
| `addresses_validation.final_uk_addresses` | Environ 19,2 millions de lignes — estimation |
| `addresses_validation.validated_companies` | Environ 16,7 millions de lignes — estimation |

Ces tables correspondent à différentes étapes ou représentations des données. Leurs volumes ne sont pas additionnés, car des enregistrements peuvent être présents dans plusieurs tables.

Ces chiffres illustrent l'échelle des données étudiées, mais ne constituent pas une mesure de précision de l'algorithme.

## 8. Validation et analyse de la qualité des données

Les contrôles portent notamment sur :

- La présence et le format des codes postaux.
- Leur comparaison avec une base de référence.
- La cohérence des informations extraites.
- L'identification de valeurs manquantes ou non reconnues.
- L'analyse des anomalies et des faux positifs.

### Exemple d'anomalie identifiée

Une vérification SQL a montré qu'un code postal enregistré dans la table des entreprises était bien présent dans la base de référence, alors que l'indicateur de validation associé affichait une non-correspondance.

Cette incohérence met en évidence la nécessité de contrôler les règles de rapprochement, la qualité des référentiels et les indicateurs produits par les traitements.

Aucun taux global de précision n'est annoncé sans évaluation indépendante sur un jeu de référence fiable.
Les tests du script complémentaire sont en cours de consolidation. Les résultats sur les 25 exemples ne constituent pas une estimation de la précision globale du pipeline.

## 9. Démonstration Python reproductible

Le dossier `Demo` contient une version simplifiée et partageable du traitement, basée sur **25 exemples d'adresses**.

### Fichiers disponibles

- `2_samples_demo.json` : jeu de données de démonstration.
- `nettoyage_demo.py` : script de nettoyage.
- `output_clean_final_demo.csv` : résultat généré.

### Exécution

```bash
pip install pandas
cd Demo
python nettoyage_demo.py
```

Le script traite les 25 exemples et génère un fichier CSV structuré.

Une comparaison avec un résultat précédemment généré a confirmé que les 25 lignes étaient reproduites à l'identique.

Cette vérification démontre la reproductibilité de la démonstration, mais pas la précision globale du pipeline professionnel.

**Script complémentaire de validation**

Le fichier `code_com_demo_corrige.py` regroupe plusieurs étapes de traitement, d'enrichissement géographique et de validation des adresses britanniques.

Les tests de démonstration portent sur 25 adresses. Ils permettent de comparer les informations extraites avec des valeurs de référence et d'identifier les écarts.

Les résultats montrent que certaines règles d'extraction et de détection des villes nécessitent encore des améliorations.

Ce script complémentaire nécessite des fichiers de référence qui ne sont pas tous inclus dans le dépôt public. Il n'est donc pas présenté comme une démonstration entièrement autonome.

## 10. Organisation du projet GitHub


uk-address-cleaning-python/
│
├── README.md
├── .gitignore
│
└── Demo/
    ├── 2_samples_demo.json
    ├── nettoyage_demo.py
    ├── code_com_demo_corrige.py
    └── output_clean_final_demo.csv

Ce dépôt présente une démonstration simplifiée du projet professionnel.

Les bases MySQL volumineuses, les fichiers internes et les éventuelles informations confidentielles de l'entreprise ne sont pas publiés.

## 11. Compétences développées

- Exploration et préparation de données volumineuses.
- Nettoyage et normalisation de données textuelles.
- Extraction d'informations avec Python et Regex.
- Manipulation de fichiers JSON et CSV.
- Requêtes SQL et utilisation de MySQL.
- Contrôle de qualité et détection d'anomalies.
- Analyse et documentation de traitements de données.
- Organisation d'un projet Data Analyst.

## 12. Perspectives d'amélioration

- Renforcer les tests automatisés sur des exemples annotés.
- Améliorer la gestion des valeurs manquantes.
- Vérifier les règles de rapprochement des codes postaux.
- Mesurer les performances sur un jeu de validation indépendant.
- Optimiser le traitement des données volumineuses.

---

**Projet réalisé dans le cadre d'un stage en analyse de données chez Markethings.**
