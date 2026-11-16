# modiDocx

[![CI](https://github.com/Novembo/modiDocx/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Novembo/modiDocx/actions/workflows/ci.yml)

Application de bureau Windows qui remplace du texte dans les paragraphes et les tableaux de documents Word `.docx`.

## Fonctionnalités

- Sélection d’un document `.docx` depuis l’interface graphique.
- Ajout de plusieurs règles « texte recherché → texte de remplacement ».
- Remplacement dans les paragraphes et les cellules de tableaux; une règle peut cibler les lignes d’une colonne par son en-tête.
- Création d’un fichier `_modified.docx` et d’un journal texte dans `logs/`.

L’application traite les textes présents dans les segments (runs) Word; une phrase répartie sur plusieurs segments peut ne pas être remplacée. Travaillez sur une copie de vos fichiers importants.

## Prérequis

- Windows 10 ou ultérieur.
- Python 3.10 ou ultérieur.

## Lancer depuis les sources

Depuis PowerShell, à la racine du dépôt :

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

L’application utilise Tkinter/ttkbootstrap pour l’interface et `python-docx` pour lire et écrire les documents. Au premier lancement, l’assistant présente les étapes principales avant l’écran de connexion et de traitement.

## Construire l’application Windows

```powershell
python -m PyInstaller modiDocx.spec --noconfirm
```

Le dossier de sortie est `dist/modiDocx/` et l’exécutable est `dist/modiDocx/modiDocx.exe`. Le script `build.bat` lance la même commande.

## Vérification

Le workflow GitHub Actions s’exécute sous Windows sur chaque push et pull request vers `main`. Il compile les sources Python et vérifie que le packaging PyInstaller aboutit; le dépôt ne contient pas actuellement de suite de tests unitaires.

## Limites et données locales

- Le projet n’a pas de déploiement web ni de version publiée configurée.
- Les comptes sont stockés localement dans `users.json`; l’authentification est une fonction de démonstration, pas une protection adaptée à des comptes ou documents sensibles.
- Les journaux `logs/` contiennent les chemins de fichiers et les valeurs recherchées/remplacées; protégez-les comme les documents traités.
- Les remplacements doivent être vérifiés avant de partager le document produit. Le fichier source n’est pas remplacé volontairement.
