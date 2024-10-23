import customtkinter as ctk
from books_window import BooksWindow
from customers_window import CustomersWindow
from manager_window import ManagerWindow

class ColorScheme:
    PRIMARY_BACKGROUND = "#384B70"
    BUTTON_BACKGROUND = "#DBE2EF"
    BUTTON_TEXT_COLOR = "#5C3C10"

class LibraryApp:
    def __init__(self, master):
        self.master = master
        self.master.title("מערכת לניהול הספרייה")
        self.setup_window()
        self.create_widgets()
        self.books_window = None
        self.customers_window = None
        self.manager_window = None

    def setup_window(self):
        window_width = 600
        window_height = 500
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.master.geometry(f"{window_width}x{window_height}+{x}+{y}")
        #self.master.config(bg=ColorScheme.PRIMARY_BACKGROUND)  # Set background color

    def create_widgets(self):
        # Header
        frame = ctk.CTkFrame(master = self.master)
        frame.pack(pady = 20, padx=20, fill="both", expand=True)

        self.header = ctk.CTkLabel(master = frame, text="Library Management System")
        self.header.pack(pady=12,padx=10)

        # Create buttons with flat modern style
        self.create_button(frame,"ספרים", self.open_books_window)
        self.create_button(frame,"לקוחות", self.open_customers_window)
        self.create_button(frame,"מנהל", self.open_manager_window)

        # Footer text
        self.footer = ctk.CTkLabel(master=frame, text="Library Management System - All Rights Reserved © 2024")
        self.footer.pack(side="bottom", pady=20)

    def create_button(self, frame, text, command):
        # Create button
        button = ctk.CTkButton(master = frame, text=text, command=lambda: command(text),
                                width = 200,
                                height = 80)

        button.pack(pady=12,padx=10)

    def open_books_window(self, button_text):
        self.master.withdraw()
        if self.books_window:
            self.books_window.window.deiconify()
        else:
            self.books_window = BooksWindow(self.master, "ספרים")


    def open_customers_window(self, button_text):
        self.master.withdraw()
        if self.customers_window:
            self.customers_window.window.deiconify()
        else:
            self.customers_window = CustomersWindow(self.master, "לקוחות")

    def open_manager_window(self, button_text):
        self.master.withdraw()
        if self.manager_window:
            self.manager_window.window.deiconify()
            self.manager_window.update_statistics()
            self.manager_window.update_graphical_stats()
        else:
            self.manager_window = ManagerWindow(self.master)