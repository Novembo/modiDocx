import tkinter as tk
from ttkbootstrap import Frame, Label, Button
from PIL import Image, ImageTk

class OnboardingFrame(Frame):
    def __init__(self, master, on_finish_callback):
        super().__init__(master, padding=10)
        master.master.resizable(True, True)

        self.on_finish_callback = on_finish_callback
        self.index = 0
        self.slides = [
            {"image": "assets/slide2.png", "text": "modiDocx - Votre assistant de traitement de documents\n\nModifiez des documents Word en masse grâce à une interface intuitive"},
            {"image": "assets/slide1.png", "text": "Ajoutez autant de règles de remplacement que nécessaire\n\nCiblez des colonnes spécifiques dans les tableaux"},
            {"image": "assets/slide0.png", "text": "Générez un nouveau fichier propre en un clic\n\nHistorique des modifications automatique"}
        ]

        self.image_label = Label(self)
        self.image_label.pack(pady=10, expand=True)

        self.text_label = Label(self, text="", font=("Segoe UI", 14), wraplength=860)
        self.text_label.pack(pady=10)

        # Boutons Précédent / Suivant / Commencer
        nav = tk.Frame(self)
        nav.pack(pady=5)
        self.prev_btn = Button(nav, text="← Précédent", bootstyle="primary", command=self.prev_slide)
        self.next_btn = Button(nav, text="Suivant →",  bootstyle="success",   command=self.next_slide)
        self.prev_btn.grid(row=0, column=0, padx=10)
        self.next_btn.grid(row=0, column=1, padx=10)

        self.show_slide()

    def show_slide(self):
        slide = self.slides[self.index]
        image = Image.open(slide["image"])
        image = image.resize((900, 520), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=photo)
        self.image_label.image = photo

        self.text_label.config(text=slide["text"])
        # Mettre à jour le bouton suivant
        if self.index == 0:
            self.prev_btn.state(["disabled"])
        else:
            self.prev_btn.state(["!disabled"])
        if self.index == len(self.slides)-1:
            self.next_btn.config(text="Commencer →")
        else:
            self.next_btn.config(text="Suivant →")

    def next_slide(self):
        if self.index < len(self.slides)-1:
            self.index += 1
            self.show_slide()
        else:
            self.on_finish_callback()

    def prev_slide(self):
        if self.index > 0:
            self.index -= 1
            self.show_slide()