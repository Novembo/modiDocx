# auth.py
import json, os, tkinter as tk, hashlib, re
from tkinter import messagebox
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap import Frame, Label, Entry, Button, Notebook, Style
from ui_main import MainApp
import hashlib

USER_FILE = "users.json"

class AuthFrame(Frame):
    def __init__(self, master):
        super().__init__(master, padding=20)
        self.master = master

        # Variables pour connexion
        self.login_user = tk.StringVar()
        self.login_pass = tk.StringVar()

        # Variables pour inscription
        self.reg_user = tk.StringVar()
        self.reg_pass = tk.StringVar()

        # Style personnalisé
        self.style = Style()
        self.style.theme_use("litera")

        # Créer le notebook
        self.nb = ttk.Notebook(self)
        self.login_frame = Frame(self.nb, padding=20)
        self.register_frame = Frame(self.nb, padding=20)

        self.nb.add(self.login_frame, text="Connexion")
        self.nb.add(self.register_frame, text="Inscription")
        self.nb.pack(fill="both", expand=True)

        # Initialisation des formulaires
        self.init_login_tab()
        self.init_register_tab()

        # Ajoute la logique de changement de style
        self.nb.bind("<<NotebookTabChanged>>", self.update_tab_style)
        self.update_tab_style()  # Initial

    def update_tab_style(self, event=None):
        style = ttk.Style()
        style.configure("TNotebook.Tab", padding=[10, 5], font=('Segoe UI', 10, 'bold'))
        style.map("TNotebook.Tab",
                  background=[("selected", "#2c3e50")],
                  foreground=[("selected", "white")])

    def init_login_tab(self):
        inner = Frame(self.login_frame)
        inner.place(relx=0.5, rely=0.5, anchor="center")

        Label(inner, text="Connexion", font=("Segoe UI", 18, "bold")).pack(pady=(0, 10))
        Label(inner, text="Veuillez entrer vos identifiants pour accéder à l'application").pack(pady=(0, 15))

        Label(inner, text="Nom d'utilisateur").pack(anchor="w")
        Entry(inner, textvariable=self.login_user, width=45).pack(pady=5)

        Label(inner, text="Mot de passe").pack(anchor="w")
        Entry(inner, textvariable=self.login_pass, show="*", width=45).pack(pady=5)

        Button(inner, text="Se connecter", command=self.login, width=45).pack(pady=15)

    def init_register_tab(self):
        inner = Frame(self.register_frame)
        inner.place(relx=0.5, rely=0.5, anchor="center")

        Label(inner, text="Inscription", font=("Segoe UI", 18, "bold")).pack(pady=(0, 10))
        Label(inner, text="Veuillez créer un compte pour utiliser l'application").pack(pady=(0, 15))

        Label(inner, text="Nom d'utilisateur").pack(anchor="w")
        Entry(inner, textvariable=self.reg_user, width=45).pack(pady=5)

        Label(inner, text="Mot de passe").pack(anchor="w")
        Entry(inner, textvariable=self.reg_pass, show="*", width=45).pack(pady=5)

        Button(inner, text="S'inscrire", command=self.register, width=45).pack(pady=15)

    def load_users(self):
        if not os.path.exists(USER_FILE) or os.stat(USER_FILE).st_size == 0:
            with open(USER_FILE, 'w') as f:
                json.dump({}, f)
            return {}
        with open(USER_FILE, 'r') as f:
            return json.load(f)

    def save_users(self, users):
        with open(USER_FILE, 'w') as f: json.dump(users, f, indent=4)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def is_strong_password(self, pw):
        if len(pw) < 8: return False
        if not re.search(r"\d", pw): return False
        if not re.search(r"[a-z]", pw): return False
        if not re.search(r"[A-Z]", pw): return False
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", pw): return False
        return True

    def login(self):
        users = self.load_users()
        u = self.login_user.get().strip()
        p = self.login_pass.get()
        hp = self.hash_password(p)
        if u in users and users[u] == hp:
            self.open_main_interface()
        else:
            messagebox.showerror("Erreur", "Identifiants invalides")

    def register(self):
        users = self.load_users()
        u = self.reg_user.get().strip()
        p = self.reg_pass.get()
        if u in users:
            messagebox.showerror("Erreur", "Utilisateur existe déjà")
        elif not self.is_strong_password(p):
            messagebox.showerror(
                "Erreur",
                "Mot de passe trop faible : 8+ caractères, chiffres, majuscules et car. spéciaux requis."
            )
        else:
            users[u] = self.hash_password(p)
            self.save_users(users)
            messagebox.showinfo("Succès", "Inscription réussie !")

    def open_main_interface(self):
        for w in self.master.winfo_children():
            w.destroy()
        MainApp(self.master).pack(fill="both", expand=True)
