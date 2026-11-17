"""DOCX replacement and transactional batch processing."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph


@dataclass(frozen=True)
class ReplacementRule:
    find: str
    replace: str
    column: str | None = None


@dataclass(frozen=True)
class DocumentPreview:
    path: Path
    counts: tuple[int, ...]


@dataclass(frozen=True)
class DocumentResult:
    source: Path
    output: Path
    counts: tuple[int, ...]


def _coerce_rules(rules: Iterable[ReplacementRule | tuple[str, str, str | None]]) -> list[ReplacementRule]:
    normalized = [rule if isinstance(rule, ReplacementRule) else ReplacementRule(*rule) for rule in rules]
    if not normalized:
        raise ValueError("Ajoutez au moins une règle de remplacement.")
    if any(not rule.find for rule in normalized):
        raise ValueError("Le texte recherché ne peut pas être vide.")
    return normalized


def _iter_paragraphs(container: object) -> Iterable[Paragraph]:
    for paragraph in getattr(container, "paragraphs", []):
        yield paragraph
    for table in getattr(container, "tables", []):
        yield from _iter_table_paragraphs(table)


def _iter_table_paragraphs(table: Table) -> Iterable[Paragraph]:
    for row in table.rows:
        for cell in row.cells:
            yield from _iter_paragraphs(cell)


def _document_paragraphs(document: object) -> Iterable[Paragraph]:
    yield from _iter_paragraphs(document)
    for section in getattr(document, "sections", []):
        for part in (section.header, section.footer, section.first_page_header,
                     section.first_page_footer, section.even_page_header,
                     section.even_page_footer):
            yield from _iter_paragraphs(part)


def _replace_in_paragraph(paragraph: Paragraph, find: str, replacement: str) -> int:
    runs = paragraph.runs
    original = "".join(run.text for run in runs)
    count = original.count(find)
    if not count:
        return 0

    # Rebuild text across run boundaries. Existing run formatting is retained for
    # untouched text; inserted text inherits the formatting of the first match.
    pieces: list[tuple[str, int, bool]] = []
    cursor = 0
    while True:
        match = original.find(find, cursor)
        if match < 0:
            if cursor < len(original):
                pieces.append((original[cursor:], cursor, False))
            break
        if match > cursor:
            pieces.append((original[cursor:match], cursor, False))
        pieces.append((replacement, match, True))
        cursor = match + len(find)

    offsets: list[tuple[int, int, int]] = []
    position = 0
    for run_index, run in enumerate(runs):
        end = position + len(run.text)
        offsets.append((position, end, run_index))
        position = end

    run_parts: list[list[str]] = [[] for _ in runs]
    for text, source_offset, is_replacement in pieces:
        if not text:
            continue
        if is_replacement:
            run_index = next((idx for start, end, idx in offsets if start <= source_offset < end),
                             max(0, len(runs) - 1))
            run_parts[run_index].append(text)
            continue
        segment_start = source_offset
        segment_end = source_offset + len(text)
        for run_start, run_end, run_index in offsets:
            start = max(segment_start, run_start)
            end = min(segment_end, run_end)
            if start < end:
                run_parts[run_index].append(text[start - segment_start:end - segment_start])
    for index, run in enumerate(runs):
        run.text = "".join(run_parts[index])
    return count


def _apply_rules(document: object, rules: list[ReplacementRule]) -> tuple[int, ...]:
    counts = [0] * len(rules)
    for rule_index, rule in enumerate(rules):
        if not rule.column:
            for paragraph in _document_paragraphs(document):
                counts[rule_index] += _replace_in_paragraph(paragraph, rule.find, rule.replace)
        else:
            for table in _iter_document_tables(document):
                if not table.rows:
                    continue
                headers = [cell.text.strip() for cell in table.rows[0].cells]
                if rule.column not in headers:
                    continue
                column_index = headers.index(rule.column)
                for row in table.rows[1:]:
                    if column_index < len(row.cells):
                        for paragraph in _iter_paragraphs(row.cells[column_index]):
                            counts[rule_index] += _replace_in_paragraph(paragraph, rule.find, rule.replace)
    return tuple(counts)


def _iter_document_tables(document: object) -> Iterable[Table]:
    for table in getattr(document, "tables", []):
        yield table
        yield from _iter_nested_tables(table)
    for section in getattr(document, "sections", []):
        for part in (section.header, section.footer, section.first_page_header,
                     section.first_page_footer, section.even_page_header,
                     section.even_page_footer):
            for table in part.tables:
                yield table
                yield from _iter_nested_tables(table)


def _iter_nested_tables(table: Table) -> Iterable[Table]:
    for row in table.rows:
        for cell in row.cells:
            for nested in cell.tables:
                yield nested
                yield from _iter_nested_tables(nested)


def preview_documents(paths: Iterable[str | Path], replacements: Iterable[ReplacementRule | tuple[str, str, str | None]]) -> list[DocumentPreview]:
    rules = _coerce_rules(replacements)
    previews = []
    for path in paths:
        source = Path(path)
        try:
            document = Document(source)
        except Exception as error:
            raise ValueError(f"Impossible d’ouvrir {source.name} : {error}") from error
        counts = _apply_rules(document, rules)
        previews.append(DocumentPreview(source, counts))
    if not previews:
        raise ValueError("Sélectionnez au moins un document .docx.")
    return previews


def _available_output_path(source: Path, reserved: set[Path]) -> Path:
    candidate = source.with_name(f"{source.stem}_modified{source.suffix}")
    index = 2
    while candidate.exists() or candidate in reserved:
        candidate = source.with_name(f"{source.stem}_modified_{index}{source.suffix}")
        index += 1
    reserved.add(candidate)
    return candidate


def process_documents(paths: Iterable[str | Path], replacements: Iterable[ReplacementRule | tuple[str, str, str | None]]) -> list[DocumentResult]:
    rules = _coerce_rules(replacements)
    sources = [Path(path) for path in paths]
    if not sources:
        raise ValueError("Sélectionnez au moins un document .docx.")
    if len({path.resolve() for path in sources}) != len(sources):
        raise ValueError("Un même document ne peut apparaître qu’une fois dans le lot.")

    documents = []
    for source in sources:
        try:
            documents.append((source, Document(source)))
        except Exception as error:
            raise ValueError(f"Impossible d’ouvrir {source.name} : {error}") from error
    reserved: set[Path] = set()
    outputs = [_available_output_path(source, reserved) for source in sources]
    staged: list[Path] = []
    published: list[Path] = []
    reservations: list[Path] = []
    results: list[DocumentResult] = []

    try:
        for (source, document), output in zip(documents, outputs):
            try:
                counts = _apply_rules(document, rules)
            except Exception as error:
                raise ValueError(f"Échec du traitement de {source.name} : {error}") from error
            fd, temp_name = tempfile.mkstemp(prefix=f".{output.stem}_", suffix=".tmp.docx", dir=output.parent)
            os.close(fd)
            temp_path = Path(temp_name)
            staged.append(temp_path)
            try:
                document.save(temp_path)
            except Exception as error:
                raise ValueError(f"Impossible de préparer le résultat de {source.name} : {error}") from error
            results.append(DocumentResult(source, output, counts))

        for output in outputs:
            try:
                with output.open("xb"):
                    pass
            except FileExistsError:
                raise FileExistsError(f"Le fichier de sortie existe déjà : {output.name}") from None
            reservations.append(output)
        for temp_path, output in zip(staged, outputs):
            os.replace(temp_path, output)
            published.append(output)
        return results
    except Exception:
        for output in published:
            output.unlink(missing_ok=True)
        for output in reservations:
            if output.exists() and output.stat().st_size == 0:
                output.unlink(missing_ok=True)
        raise
    finally:
        for temp_path in staged:
            temp_path.unlink(missing_ok=True)


def export_rules(path: str | Path, name: str, replacements: Iterable[ReplacementRule | tuple[str, str, str | None]]) -> None:
    rules = _coerce_rules(replacements)
    payload = {
        "version": 1,
        "name": name.strip() or "Règles sans nom",
        "rules": [{"find": rule.find, "replace": rule.replace, "column": rule.column} for rule in rules],
    }
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def import_rules(path: str | Path) -> tuple[str, list[ReplacementRule]]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or payload.get("version") != 1:
            raise ValueError("Version de jeu de règles non prise en charge.")
        name = payload.get("name")
        raw_rules = payload.get("rules")
        if not isinstance(name, str) or not isinstance(raw_rules, list):
            raise ValueError("Structure de jeu de règles invalide.")
        rules = []
        for item in raw_rules:
            if not isinstance(item, dict) or not isinstance(item.get("find"), str) or not isinstance(item.get("replace"), str):
                raise ValueError("Chaque règle doit définir find et replace sous forme de texte.")
            column = item.get("column")
            if column is not None and not isinstance(column, str):
                raise ValueError("La colonne ciblée doit être du texte ou null.")
            rules.append(ReplacementRule(item["find"], item["replace"], column))
        return name, _coerce_rules(rules)
    except (json.JSONDecodeError, OSError) as error:
        raise ValueError(f"Impossible de lire le jeu de règles : {error}") from error


def replace_text_in_docx(file_path: str, replacements: Iterable[ReplacementRule | tuple[str, str, str | None]]) -> str:
    result = process_documents([file_path], replacements)[0]
    return str(result.output)
