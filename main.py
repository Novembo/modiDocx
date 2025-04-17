import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from auth import AuthFrame
from onboarding import OnboardingFrame

class App(tb.Window):
    def __init__(self):
        super().__init__(themename="litera")
        self.title("modiDocx - Login")
        self.geometry("900x800")
        self.resizable(True, True)

        self.container = tk.Frame(self)
        self.container.pack(fill=BOTH, expand=True)

        self.show_onboarding()

    def show_onboarding(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        OnboardingFrame(self.container, self.show_auth).pack(fill=BOTH, expand=True)

    def show_auth(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        AuthFrame(self.container).pack(fill=BOTH, expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()
