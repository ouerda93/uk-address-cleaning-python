# UK Company Address Cleaning — Python Data Project

## Présentation du projet

Ce projet a été réalisé dans le cadre de mon stage en analyse de données chez **Markethings**.

L'objectif est de nettoyer et de structurer des adresses d'entreprises britanniques afin de faciliter leur exploitation et leur analyse.

## Objectifs

- Lire des données d'adresses au format JSON.
- Extraire les numéros de rue.
- Nettoyer et structurer les noms de rue.
- Conserver les codes postaux britanniques.
- Générer un fichier CSV exploitable.

## Technologies utilisées

- Python
- Pandas
- JSON
- Expressions régulières (Regex)
- Visual Studio Code

## Fonctionnement de la démonstration

Le dossier `Demo` contient :

- `2_samples_demo.json` : jeu de données de 25 adresses.
- `nettoyage_demo.py` : script Python de nettoyage.
- `output_clean_final_demo.csv` : résultat généré.

Pour exécuter la démonstration :

```bash
pip install pandas
cd Demo
python nettoyage_demo.py
```

## Résultats

Le script traite 25 adresses et génère un fichier CSV structuré.

Une comparaison avec le fichier de résultat initial a confirmé que les 25 lignes sont reproduites à l'identique.

Cette vérification confirme la reproductibilité de la démonstration, mais ne constitue pas une validation indépendante de la qualité des adresses.

## Source des données

Exemples issus de données publiques de Companies House, Royaume-Uni.

## Contexte professionnel

Projet réalisé dans le cadre d'un stage chez Markethings, portant sur le traitement, la normalisation et la structuration des adresses britanniques.