"""Tkinter interface for reviewing and processing DOCX batches."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog

import ttkbootstrap as tb
from ttkbootstrap.constants import BOTH, LEFT, X

from replace import ReplacementRule, export_rules, import_rules, preview_documents, process_documents


class MainApp(tb.Frame):
    def __init__(self, master: tk.Misc):
        super().__init__(master, padding=22)
        self.file_paths: list[Path] = []
        self.rule_rows: list[tuple[tb.Entry, tb.Entry, tb.Entry, tb.Frame]] = []
        self.create_widgets()
        self.add_rule_row()

    def create_widgets(self) -> None:
        tb.Label(self, text="modiDocx", font=("Segoe UI", 24, "bold"), bootstyle="primary").pack(anchor="w")
        tb.Label(self, text="Préparez des remplacements, vérifiez leur portée, puis traitez un lot de documents.",
                 font=("Segoe UI", 11)).pack(anchor="w", pady=(2, 16))

        files = tb.Frame(self)
        files.pack(fill=X, pady=(0, 12))
        tb.Button(files, text="Sélectionner des fichiers DOCX…", command=self.select_files,
                  bootstyle="primary").pack(side=LEFT)
        self.files_label = tb.Label(files, text="Aucun document sélectionné", bootstyle="secondary")
        self.files_label.pack(side=LEFT, padx=12)

        tb.Label(self, text="Règles", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(8, 5))
        headers = tb.Frame(self)
        headers.pack(fill=X)
        for text, width in (("Texte recherché", 30), ("Remplacement", 30), ("En-tête de colonne (facultatif)", 30)):
            tb.Label(headers, text=text, width=width, anchor="w").pack(side=LEFT, padx=(0, 5))

        self.rules_frame = tb.Frame(self)
        self.rules_frame.pack(fill=BOTH, expand=True, pady=(2, 8))
        controls = tb.Frame(self)
        controls.pack(fill=X, pady=4)
        tb.Button(controls, text="＋ Ajouter une règle", command=self.add_rule_row,
                  bootstyle="info-outline").pack(side=LEFT, padx=(0, 6))
        tb.Button(controls, text="Importer JSON…", command=self.load_rules,
                  bootstyle="secondary-outline").pack(side=LEFT, padx=6)
        tb.Button(controls, text="Exporter JSON…", command=self.save_rules,
                  bootstyle="secondary-outline").pack(side=LEFT, padx=6)
        tb.Button(controls, text="Prévisualiser et traiter", command=self.preview_and_process,
                  bootstyle="success").pack(side=RIGHT)

    def add_rule_row(self, values: tuple[str, str, str | None] = ("", "", None)) -> None:
        row = tb.Frame(self.rules_frame)
        row.pack(fill=X, pady=3)
        find = tb.Entry(row)
        replacement = tb.Entry(row)
        column = tb.Entry(row)
        for widget, value in zip((find, replacement, column), values):
            if value:
                widget.insert(0, value)
        find.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        replacement.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        column.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        tb.Button(row, text="×", width=3, command=lambda: self.remove_rule_row(row),
                  bootstyle="danger-outline").pack(side=RIGHT)
        self.rule_rows.append((find, replacement, column, row))

    def remove_rule_row(self, row: tb.Frame) -> None:
        row.destroy()
        self.rule_rows = [item for item in self.rule_rows if item[3] is not row]

    def select_files(self) -> None:
        selected = filedialog.askopenfilenames(
            title="Sélectionner les documents Word", filetypes=[("Documents Word", "*.docx")]
        )
        if selected:
            self.file_paths = [Path(path) for path in selected]
            self.files_label.configure(text=f"{len(self.file_paths)} document(s) sélectionné(s)", bootstyle="success")

    def get_rules(self) -> list[ReplacementRule]:
        rules = []
        for find_entry, replacement_entry, column_entry, _ in self.rule_rows:
            find = find_entry.get()
            replacement = replacement_entry.get()
            column = column_entry.get().strip()
            if find:
                rules.append(ReplacementRule(find, replacement, column or None))
        if not rules:
            raise ValueError("Saisissez au moins un texte à rechercher.")
        if any(not rule.find.strip() for rule in rules):
            raise ValueError("Le texte recherché ne peut pas être uniquement composé d’espaces.")
        return rules

    def preview_and_process(self) -> None:
        if not self.file_paths:
            messagebox.showerror("Aucun document", "Sélectionnez au moins un fichier DOCX.", parent=self)
            return
        try:
            rules = self.get_rules()
            previews = preview_documents(self.file_paths, rules)
        except Exception as error:
            messagebox.showerror("Prévisualisation impossible", str(error), parent=self)
            return

        lines = [f"{preview.path.name} — " + ", ".join(
            f"règle {index + 1} : {count}" for index, count in enumerate(preview.counts)
        ) for preview in previews]
        total = sum(sum(preview.counts) for preview in previews)
        summary = (f"{len(previews)} document(s), {len(rules)} règle(s), "
                   f"{total} remplacement(s) estimé(s).\n\n" + "\n".join(lines))
        if not messagebox.askyesno("Vérifier le lot", summary + "\n\nCréer les documents modifiés ?", parent=self):
            return
        try:
            results = process_documents(self.file_paths, rules)
        except Exception as error:
            messagebox.showerror("Lot annulé", f"Aucun résultat du lot n’a été conservé.\n\n{error}", parent=self)
            return

        self.show_results(results)

    def show_results(self, results: list) -> None:
        lines = [f"{result.source.name} → {result.output.name} — " + ", ".join(
            f"règle {index + 1} : {count}" for index, count in enumerate(result.counts)
        ) for result in results]
        messagebox.showinfo("Lot terminé", "\n".join(lines), parent=self)

    def load_rules(self) -> None:
        path = filedialog.askopenfilename(title="Importer un jeu de règles", filetypes=[("Fichiers JSON", "*.json")])
        if not path:
            return
        try:
            name, rules = import_rules(path)
        except (ValueError, OSError) as error:
            messagebox.showerror("Import impossible", str(error), parent=self)
            return
        for _, _, _, row in self.rule_rows:
            row.destroy()
        self.rule_rows.clear()
        for rule in rules:
            self.add_rule_row((rule.find, rule.replace, rule.column))
        messagebox.showinfo("Règles importées", f"Jeu « {name} » chargé.", parent=self)

    def save_rules(self) -> None:
        try:
            rules = self.get_rules()
        except ValueError as error:
            messagebox.showerror("Export impossible", str(error), parent=self)
            return
        name = simpledialog.askstring("Nom du jeu", "Nom à donner à ce jeu de règles :", parent=self)
        if name is None:
            return
        path = filedialog.asksaveasfilename(
            title="Exporter les règles", defaultextension=".json", initialfile="modidocx-rules.json",
            filetypes=[("Fichiers JSON", "*.json")],
        )
        if not path:
            return
        try:
            export_rules(path, name, rules)
        except OSError as error:
            messagebox.showerror("Export impossible", str(error), parent=self)
            return
        messagebox.showinfo("Export terminé", f"Règles enregistrées dans {Path(path).name}.", parent=self)
