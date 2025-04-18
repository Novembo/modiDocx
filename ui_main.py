import tkinter as tk
from tkinter import filedialog, messagebox
from ttkbootstrap import Frame, Label, Entry, Button, Scrollbar, Style, Separator
from replace import replace_text_in_docx
import os
import json

class ScrollableFrame(Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.scrollbar = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas)
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.window_id, width=canvas_width)

class MainApp(Frame):
    def __init__(self, master, username):
        super().__init__(master, padding=20)
        self.file_path = ""
        self.replacements = []
        self.username = username
        self.style = Style()
        
        # Configuration des styles personnalisés
        self.style.configure('card.TFrame', background='#ffffff', relief='flat', 
                           borderwidth=1, bordercolor='#e0e0e0')
        self.style.configure('muted.TLabel', foreground='#6c757d')
        
        self.create_widgets()
        self.add_entry_row()

    def create_widgets(self):
        main_container = Frame(self)
        main_container.pack(expand=True, fill="both", padx=20)
        
        # En-tête
        header_frame = Frame(main_container)
        header_frame.pack(fill="x", pady=(0, 20))
        Label(header_frame, text=f"👋 Bienvenue {self.username} !", 
             font=("Segoe UI", 22, "bold"), bootstyle="primary").pack(pady=5)
        Label(header_frame, text="Modifiez vos documents Word en 3 étapes simples :",
             font=("Segoe UI", 12), bootstyle="dark").pack()
        
        # Section fichier
        file_frame = Frame(main_container)
        file_frame.pack(fill="x", pady=15)
        Button(file_frame, text="📁 Sélectionner un document", 
              command=self.select_file, bootstyle="primary", width=25).pack()
        self.file_label = Label(file_frame, text="Aucun fichier sélectionné", 
                              font=("Segoe UI", 10), bootstyle="muted")
        self.file_label.pack(pady=8)
        
        # Zone des règles
        scroll_frame = ScrollableFrame(main_container)
        scroll_frame.pack(fill="both", expand=True, pady=10)
        self.entries_frame = scroll_frame.scrollable_frame
        
        # Boutons d'action
        btn_frame = Frame(main_container)
        btn_frame.pack(fill="x", pady=20)
        Button(btn_frame, text="➕ Ajouter une règle", 
              command=self.add_entry_row, bootstyle="info-outline").pack(side="left", padx=5)
        Button(btn_frame, text="✨ Appliquer les modifications", 
              command=self.apply_replacements, bootstyle="success").pack(side="right", padx=5)

    def add_entry_row(self):
        card = Frame(self.entries_frame, style='card.TFrame')
        card.pack(fill="x", pady=(0, 15), padx=5)
        
        # Conteneur principal avec largeur fixe
        content_frame = Frame(card)
        content_frame.pack(pady=10, padx=10, anchor="center")
        
        # Configuration des tailles fixes
        entry_width = 80  # Largeur fixe en caractères
        label_width = 60   # Largeur fixe pour l'alignement
        
        # Texte à remplacer
        Label(content_frame, text="Texte original", 
             font=("Segoe UI", 10, "bold"), width=label_width, anchor="w").grid(row=0, column=0, sticky="w")
        find_entry = Entry(content_frame, font=("Segoe UI", 11), width=entry_width)
        find_entry.grid(row=1, column=0, pady=(0, 10), sticky="w")
        
        # Remplacer par
        Label(content_frame, text="Nouveau texte", 
             font=("Segoe UI", 10, "bold"), width=label_width, anchor="w").grid(row=2, column=0, sticky="w")
        replace_entry = Entry(content_frame, font=("Segoe UI", 11), width=entry_width)
        replace_entry.grid(row=3, column=0, pady=(0, 10), sticky="w")
        
        # Colonne optionnelle
        Label(content_frame, text="Colonne spécifique (optionnel)", font=("Segoe UI", 9, "bold"), width=label_width, anchor="w").grid(row=4, column=0, sticky="w")
        column_entry = Entry(content_frame, font=("Segoe UI", 11), width=entry_width)
        column_entry.insert(0, "Ex: Colonne B")
        column_entry.configure(foreground="#6c757d")
        column_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(e.widget))
        column_entry.grid(row=5, column=0, pady=(0, 5), sticky="w")

        self.replacements.append((find_entry, replace_entry, column_entry))

    def clear_placeholder(self, entry):
        if entry.get() == "Ex: Colonne B":
            entry.delete(0, "end")
            entry.configure(foreground="#000000")

    def select_file(self):
        filetypes = [("Word Documents", "*.docx")]
        self.file_path = filedialog.askopenfilename(title="Ouvrir un document Word", filetypes=filetypes)
        if self.file_path:
            self.file_label.config(text=os.path.basename(self.file_path))
            self.file_label.configure(bootstyle="success")

    def apply_replacements(self):
        if not self.file_path:
            messagebox.showerror("Erreur", "Veuillez choisir un fichier Word")
            return

        pairs = []
        for find, replace, column in self.replacements:
            f = find.get().strip()
            r = replace.get().strip()
            c = column.get().strip()
            
            if f:  # Ignore les lignes vides
                clean_c = c if c and c != "Ex: Colonne B" else None
                pairs.append((f, r, clean_c))

        if not pairs:
            messagebox.showwarning("Avertissement", "Aucune règle de remplacement à appliquer !")
            return

        try:
            new_path = replace_text_in_docx(self.file_path, pairs)
            messagebox.showinfo("Succès", 
                f"Document modifié avec succès !\n\nNouveau fichier :\n{os.path.basename(new_path)}", 
                parent=self)
            self.reset()
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue :\n{str(e)}", parent=self)

    def reset(self):
        self.file_label.config(text="Aucun fichier sélectionné", bootstyle="secondary")
        for widget in self.entries_frame.winfo_children():
            if isinstance(widget, Frame):
                widget.destroy()
        self.replacements = []
        self.add_entry_row()
