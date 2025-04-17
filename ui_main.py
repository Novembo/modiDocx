import tkinter as tk
from tkinter import filedialog, messagebox
from ttkbootstrap import Frame, Label, Entry, Button
from replace import replace_text_in_docx
import os

class MainApp(Frame):
    def __init__(self, master):
        super().__init__(master, padding=20)
        self.file_path = ""
        self.replacements = []

        Label(self, text="Bienvenue dans modiDocx", font=("Segoe UI", 18)).pack(pady=10)
        Button(self, text="Sélectionner un document Word", command=self.select_file).pack(pady=10)
        self.file_label = Label(self, text="Aucun fichier sélectionné")
        self.file_label.pack(pady=(10, 20))

        self.entries_frame = tk.Frame(self)
        self.entries_frame.pack(pady=10)
        self.add_entry_row()

        Button(self, text="Ajouter une autre paire", command=self.add_entry_row).pack(pady=5)

        self.replace_btn = Button(self, text="Appliquer les modifications", command=self.apply_replacements)
        self.replace_btn.pack(pady=15)

    def select_file(self):
        filetypes = [("Word Documents", "*.docx")]
        self.file_path = filedialog.askopenfilename(title="Ouvrir un document Word", filetypes=filetypes)
        if self.file_path:
            self.file_label.config(text=os.path.basename(self.file_path))

    def add_entry_row(self):
        row = tk.Frame(self.entries_frame)
        row.pack(pady=3)
        find = Entry(row, width=30)
        find.pack(side=tk.LEFT, padx=5)
        replace = Entry(row, width=30)
        replace.pack(side=tk.LEFT, padx=5)
        column = Entry(row, width=25)
        column.insert(0, "(Colonne optionnelle)")
        column.pack(side=tk.LEFT, padx=5)
        self.replacements.append((find, replace, column))

    def apply_replacements(self):
        if not self.file_path:
            messagebox.showerror("Erreur", "Veuillez choisir un fichier Word")
            return

        pairs = []
        for find, replace, column in self.replacements:
            f, r, c = find.get(), replace.get(), column.get().strip()
            if f:
                pairs.append((f, r, c if c and c != "(Colonne optionnelle)" else None))

        try:
            new_path = replace_text_in_docx(self.file_path, pairs)
            messagebox.showinfo("Succès", f"Fichier modifié :\n{new_path}")
            self.reset()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def reset(self):
        self.file_label.config(text="Aucun fichier sélectionné")
        for entry in self.entries_frame.winfo_children():
            entry.destroy()
        self.replacements = []
        self.file_path = ""
        self.add_entry_row()
