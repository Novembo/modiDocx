"""Application entry point."""

import ttkbootstrap as tb

from ui_main import MainApp


def main() -> None:
    app = tb.Window(themename="litera")
    app.title("modiDocx — traitement DOCX en lot")
    app.geometry("1120x680")
    app.minsize(820, 520)
    MainApp(app).pack(fill="both", expand=True)
    app.mainloop()


if __name__ == "__main__":
    main()
