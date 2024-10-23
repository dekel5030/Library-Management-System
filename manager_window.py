import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from datetime import datetime
import mysql.connector
from database_manager import DatabaseManager
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ManagerWindow:
    def __init__(self, master):
        self.master = master
        self.window = ctk.CTkToplevel(master)
        self.window.title("Manager - Statistics and Borrowing Activities")
        self.db_manager = DatabaseManager()
        self.setup_ui()

    def setup_ui(self):
        # Frame for overall layout
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.pack(padx=10, pady=10, fill='both', expand=True)

        # Frame for statistics and pie chart
        self.stats_frame = ctk.CTkFrame(self.main_frame)
        self.stats_frame.pack(side='top', fill='both', expand=True)

        # Frame for statistics labels
        self.stats_labels_frame = ctk.CTkFrame(self.stats_frame)
        self.stats_labels_frame.pack(side='left', padx=10, fill='y')

        ctk.CTkLabel(self.stats_labels_frame, text="Library Statistics", font=("Arial", 16)).pack(pady=10)

        # Labels for textual statistics
        self.total_books_label = ctk.CTkLabel(self.stats_labels_frame, text="Total Books Borrowed: ")
        self.total_books_label.pack(pady=5)

        self.overdue_books_label = ctk.CTkLabel(self.stats_labels_frame, text="Overdue Books: ")
        self.overdue_books_label.pack(pady=5)

        self.most_popular_book_label = ctk.CTkLabel(self.stats_labels_frame, text="Most Popular Book: ")
        self.most_popular_book_label.pack(pady=5)

        # Frame for graphical statistics (pie chart)
        self.graph_frame = ctk.CTkFrame(self.stats_frame)
        self.graph_frame.pack(side='right', padx=10, fill='both', expand=True)

        # Frame for borrowing activities
        self.borrowing_frame = ctk.CTkFrame(self.main_frame)
        self.borrowing_frame.pack(side='bottom', padx=10, pady=10, fill='both', expand=True)

        ctk.CTkLabel(self.borrowing_frame, text="Borrowing Activities", font=("Arial", 16)).pack(pady=10)

        columns = ("Book Title", "Customer", "Borrow Date", "Expected Return Date", "Actual Return Date")
        # Create a style for the Treeview (adjust font size here)
        style = ttk.Style()
        style.configure("Treeview", font=("Helvetica", 20), rowheight=60)  # Adjust font size
        style.configure("Treeview.Heading", font=("Helvetica", 26, "bold"))
        self.borrowing_tree = ttk.Treeview(self.borrowing_frame, columns=columns, show="headings", height=10)
        self.borrowing_tree.pack(pady=10, fill='both', expand=True)

        for col in columns:
            self.borrowing_tree.heading(col, text=col)

        self.update_statistics()
        self.update_borrowing_activities()

        self.window.protocol("WM_DELETE_WINDOW", self.close)  # Handle window close

    def update_statistics(self):
        """Fetch and display the statistics along with graphical data."""
        try:
            self.db_manager.mysql_connect()

            # Total books borrowed
            self.db_manager.cursor.execute("SELECT COUNT(*) FROM borrowed_books")
            total_books_borrowed = self.db_manager.cursor.fetchone()[0]
            self.total_books_label.configure(text=f"Total Books Borrowed: {total_books_borrowed}")

            # Overdue books
            self.db_manager.cursor.execute(
                "SELECT COUNT(*) FROM borrowed_books WHERE expected_return_date < %s AND actual_return_date IS NULL",
                [datetime.now()])
            overdue_books = self.db_manager.cursor.fetchone()[0]
            self.overdue_books_label.configure(text=f"Overdue Books: {overdue_books}")

            # Most popular book
            self.db_manager.cursor.execute(
                "SELECT Title, COUNT(*) as borrow_count FROM borrowed_books JOIN books ON borrowed_books.book_id = books.id GROUP BY book_id ORDER BY borrow_count DESC LIMIT 1")
            most_popular_book = self.db_manager.cursor.fetchone()
            if most_popular_book:
                self.most_popular_book_label.configure(
                    text=f"Most Popular Book: {most_popular_book[0]} ({most_popular_book[1]} borrows)")

            # Fetch data for graphical display
            self.update_graphical_stats()

        except mysql.connector.Error as e:
            print(f"Error fetching statistics: {e}")

        finally:
            self.db_manager.close_connection()

    def update_graphical_stats(self):
        """Display graphical information such as pie chart for overdue and non-overdue books."""
        try:
            self.db_manager.mysql_connect()

            # Pie chart for borrowed vs overdue books
            self.db_manager.cursor.execute('''SELECT 
                                                  (SELECT COUNT(*) FROM borrowed_books WHERE actual_return_date IS NULL AND expected_return_date >= %s) AS on_time,
                                                  (SELECT COUNT(*) FROM borrowed_books WHERE actual_return_date IS NULL AND expected_return_date < %s) AS overdue''',
                                           [datetime.now(), datetime.now()])
            on_time, overdue = self.db_manager.cursor.fetchone()

            self.plot_pie_chart(on_time, overdue)

        except mysql.connector.Error as e:
            print(f"Error fetching graphical data: {e}")

        finally:
            self.db_manager.close_connection()

    def plot_pie_chart(self, on_time, overdue):
        """Plot a pie chart showing on-time vs overdue books."""
        # Clear any previous chart
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        # Prepare data for pie chart
        labels = 'On Time', 'Overdue'
        sizes = [on_time, overdue]
        colors = ['#66b3ff', '#ff9999']
        explode = (0, 0.1)  # explode the overdue slice

        fig, ax = plt.subplots()
        fig.patch.set_facecolor('black')  # Set the figure background to dark
        ax.set_facecolor('black')  # Set the axes background to dark

        # Increase font size for percentages
        ax.pie(sizes, explode=explode, labels=labels, autopct=lambda p: f'{p:.1f}%', colors=colors, shadow=True,
               startangle=90,
               textprops=dict(color="white", fontsize=14))  # Set the font size here
        ax.axis('equal')  # Equal aspect ratio ensures the pie is drawn as a circle.

        # Display the chart in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def update_borrowing_activities(self):
        """Fetch and display the borrowing activities."""
        try:
            self.db_manager.mysql_connect()

            sql_query = '''SELECT b.Title, c.customer_name, bb.borrow_date, bb.expected_return_date, bb.actual_return_date 
                             FROM borrowed_books AS bb
                             JOIN books AS b ON bb.book_id = b.id
                             JOIN customers AS c ON bb.customer_id = c.id
                             ORDER BY bb.borrow_date DESC'''

            self.db_manager.cursor.execute(sql_query)
            borrowing_records = self.db_manager.cursor.fetchall()

            # Clear the Treeview before inserting new data
            for item in self.borrowing_tree.get_children():
                self.borrowing_tree.delete(item)

            # Populate the treeview with borrowing activities
            for record in borrowing_records:
                self.borrowing_tree.insert("", "end", values=record)

        except mysql.connector.Error as e:
            print(f"Error fetching borrowing activities: {e}")

        finally:
            self.db_manager.close_connection()

    def close(self):
        self.window.withdraw()  # Hide the current window
        self.master.deiconify()  # Show the main window again
