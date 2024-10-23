import customtkinter as ctk
from tkinter import ttk
from datetime import datetime
import mysql.connector
from database_manager import DatabaseManager


class CustomerInfoWindow:
    def __init__(self, parent_window, customer):
        self.customer_info_window = ctk.CTkToplevel(parent_window)
        self.customer_info_window.title("Customer Details")
        self.customer = customer
        self.db_manager = DatabaseManager()
        self.setup_ui()

    def setup_ui(self):
        self.customer_info_window.geometry(f"1200x600")
        self.customer_info_frame()
        self.borrowed_books_treeview()
        self.borrowed_list_update()

    def customer_info_frame(self):
        # Frame for customer details
        ctk.CTkLabel(self.customer_info_window, text="Customer INFO:").pack(pady=5)
        customer_info_frame = ctk.CTkFrame(self.customer_info_window)
        customer_info_frame.pack(pady=10)

        # Labels for book information
        ctk.CTkLabel(customer_info_frame, text=f"Name :\n{self.customer[0]}", wraplength=200).grid(row=0, column=0, padx=5,
                                                                                           pady=5)
        ctk.CTkLabel(customer_info_frame, text=f"Phone Number:\n{self.customer[1]}", wraplength=200).grid(row=0, column=1, padx=5,
                                                                                         pady=5)
        ctk.CTkLabel(customer_info_frame, text=f"Customer ID:\n{self.customer[2]}").grid(row=0, column=2, padx=5, pady=5)


    def borrowed_books_treeview(self):
        self.borrowed_label = ctk.CTkLabel(self.customer_info_window, text=f"List of books borrowed by {self.customer[0]}")
        self.borrowed_label.pack(pady=10)
        columns = ("Book title", "Book ID", "copy number", "Borrow Date", "Expected Return Date", "Actual Return Date")
        self.borrowed_books_tree = ttk.Treeview(self.customer_info_window, columns=columns, show="headings")

        for col in columns:
            self.borrowed_books_tree.heading(col, text=col)
        self.borrowed_books_tree.pack(pady=10, fill=ctk.BOTH, expand=True)

        # Add a button to return the selected copy
        self.return_button = ctk.CTkButton(self.customer_info_window, text="Return Selected Copy",
                                       command=self.return_selected_copy)
        self.return_button.pack(pady=10)

    def return_selected_copy(self):
        """Return the selected borrowed book copy."""
        selected_item = self.borrowed_books_tree.selection()
        if selected_item:
            # Get the values of the selected item
            item = self.borrowed_books_tree.item(selected_item)
            borrow = item['values']
            actual_return_date = borrow[5]

            if actual_return_date in [None, "", "None"]:
                try:
                    self.db_manager.mysql_connect()

                    # Update available copies
                    self.db_manager.cursor.execute('''UPDATE books
                                           SET available_copies = available_copies + 1
                                           WHERE id = %s''', [borrow[1]])

                    # Update book copy availability
                    self.db_manager.cursor.execute('''UPDATE book_copy
                                           SET available = TRUE
                                           WHERE book_id = %s and copy_number = %s''', [borrow[1], borrow[2]])

                    # Update the actual return date
                    self.db_manager.cursor.execute('''UPDATE borroFwed_books
                                           SET actual_return_date = %s
                                           WHERE book_id = %s and copy_number = %s and actual_return_date IS NULL''',
                                        [datetime.now(), borrow[1], borrow[2]])

                    self.db_manager.connection.commit()

                    # Provide user feedback
                    print("Book copy returned successfully.")

                except mysql.connector.Error as e:
                    print(f"Error while returning the book: {e}")

                finally:
                    self.db_manager.close_connection()  # Ensure connection is closed
                    # Refresh the UI
                    self.borrowed_list_update()

            else:
                print("The selected Copy is already returned.")

        else:
            print("No book copy selected for return.")


    def borrowed_list_update(self):
        # Clear the current list of borrowed books
        self.borrowed_books_tree.delete(*self.borrowed_books_tree.get_children())

        selected_id = self.customer[2]
        if not selected_id:
            print("No customer ID selected.")
            return

        sql_query = '''SELECT Title, book_id, copy_number, borrow_date, expected_return_date, actual_return_date 
                                                FROM borrowed_books AS bb
                                                JOIN books AS b ON b.id = bb.book_id
                                                WHERE customer_id = %s
                                                ORDER BY actual_return_date IS NOT NULL'''

        try:
            self.db_manager.mysql_connect()
            self.db_manager.cursor.execute(sql_query, [selected_id])
            borrowed_books = self.db_manager.cursor.fetchall()

            if not borrowed_books:
                print("This customer has no borrowed books.")
                return

            # Populate the tree with the borrowed books data
            for borrow in borrowed_books:
                self.borrowed_books_tree.insert("", "end", values=borrow)

        except mysql.connector.Error as e:
            print(f"Error fetching borrowed books: {e}")

        finally:
            self.db_manager.close_connection()  # Always close the connection
