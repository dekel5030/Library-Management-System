import customtkinter as ctk
from library_app import LibraryApp

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

if __name__ == "__main__":
    #root = tk.Tk()
    root = ctk.CTk()
    app = LibraryApp(root)
    root.mainloop()
