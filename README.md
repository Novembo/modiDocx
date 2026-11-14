# modiDocx

[![CI](https://github.com/Novembo/modiDocx/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Novembo/modiDocx/actions/workflows/ci.yml)

Application de bureau Windows pour modifier du texte dans les paragraphes et les tableaux de documents Word `.docx`.

## Prérequis

- Windows 10 ou ultérieur
- Python 3.10+

## Lancer depuis les sources

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Le programme utilise `python-docx` pour éditer les documents et `ttkbootstrap` pour son interface. Travaillez sur une copie de vos fichiers importants.

## Construire l'application

```powershell
pyinstaller modiDocx.spec --noconfirm
```

L'application construite est placée dans `dist/modiDocx/`. Le workflow GitHub Actions s'exécute sur Windows à chaque pull request vers `main` et push sur `main`; il compile le code et vérifie que le packaging PyInstaller aboutit. Aucun déploiement automatique n'est configuré.
