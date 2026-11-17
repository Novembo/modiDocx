# modiDocx

Application Windows locale pour prévisualiser et appliquer des remplacements à un lot de documents Word `.docx`.

## Fonctionnalités

- Sélection de plusieurs fichiers DOCX.
- Règles de remplacement réutilisables, avec ciblage facultatif d’une colonne de tableau par son en-tête.
- Prévisualisation du nombre de remplacements par document et par règle avant confirmation.
- Traitement du corps, des tableaux, des en-têtes et des pieds de page, y compris les textes répartis entre plusieurs segments Word.
- Création des résultats à côté des documents sources. Les fichiers existants ne sont pas écrasés; un suffixe numérique est ajouté en cas de conflit.
- Import et export des règles en JSON versionné pour les partager entre collègues.
- Bilan affiché à la fin du traitement. Si la préparation d’un fichier échoue, aucun résultat du lot n’est publié.

Le traitement est local et les documents ne sont envoyés à aucun service externe. La prévisualisation donne une estimation des occurrences; vérifiez toujours les documents générés avant de les partager. Les zones de texte, commentaires et notes Word ne sont pas prises en charge dans cette version.

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

## Construire l’application Windows

```powershell
python -m PyInstaller modiDocx.spec --noconfirm
```

Le dossier de sortie est `dist/modiDocx/` et l’exécutable est `dist/modiDocx/modiDocx.exe`.

## Vérification

La CI Windows compile les sources, exécute les tests unitaires et vérifie que le paquet PyInstaller se construit.

## Format des jeux de règles

Les fichiers JSON exportés utilisent la version `1` et contiennent un nom ainsi qu’une liste de règles. Chaque règle définit `find`, `replace` et `column` (`null` lorsqu’aucune colonne particulière n’est visée). Importez le fichier dans modiDocx pour le partager avec un collègue.
