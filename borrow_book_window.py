from tkinter import ttk
import customtkinter as ctk
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import mysql.connector
from database_manager import DatabaseManager


class BorrowBookWindow:
    def __init__(self, parent_window, book):
        self.borrow_window = ctk.CTkToplevel(parent_window)
        self.borrow_window.title("Borrow Book Details")
        self.book = book
        self.db_manager = DatabaseManager()
        self.setup_ui()

    def show_date(self):
        # Example function to show the selected date
        selected_date = self.borrow_date_entry.get_date()
        print("Selected Date:", selected_date)

    def setup_ui(self):
        self.borrow_window.geometry(f"1200x700")
        self.book_frame()
        self.customer_frame()
        self.dates_frame()
        button_frame = ctk.CTkFrame(self.borrow_window)
        button_frame.pack(pady=20)

        # Create the Borrow button
        borrow_button = ctk.CTkButton(button_frame, text="Borrow", command=lambda: self.save_borrow())
        borrow_button.pack(side="left", padx=10)

        self.borrowed_books_treeview()



    def book_frame(self):
        # Frame for book details
        ctk.CTkLabel(self.borrow_window, text="Book INFO:").pack(pady=5)
        book_info_frame = ctk.CTkFrame(self.borrow_window)
        book_info_frame.pack(pady=10)

        # Labels for book information
        ctk.CTkLabel(book_info_frame, text=f"Title :\n{self.book[0]}", wraplength=200).grid(row=0, column=0, padx=5,
                                                                                           pady=5)
        ctk.CTkLabel(book_info_frame, text=f"Authors:\n{self.book[1]}", wraplength=200).grid(row=0, column=1, padx=5,
                                                                                         pady=5)
        ctk.CTkLabel(book_info_frame, text=f"Book ID:\n{self.book[6]}").grid(row=0, column=2, padx=5, pady=5)

        self.available_copy_count_label = ctk.CTkLabel(book_info_frame, text=f"Available Copies:\n{self.book[8]}")
        self.available_copy_count_label.grid(row=0, column=3, padx=5, pady=5)


    def customer_frame(self):
        # Create a frame for customer details
        customer_frame = ctk.CTkFrame(self.borrow_window)
        customer_frame.pack(pady=10)
        # Create labels for customer name and phone number

        ctk.CTkLabel(customer_frame, text="Customer ID:").grid(row=0, column=0, padx=(0, 5), sticky="w")

        self.name_title_label = ctk.CTkLabel(customer_frame, text="Full Name:", wraplength=200)
        self.name_title_label.grid(row=0, column=1, padx=(5, 20))

        self.phone_title_label = ctk.CTkLabel(customer_frame, text="Phone Number:", wraplength=200)
        self.phone_title_label.grid(row=0, column=2, padx=(5, 0))

        self.name_label = ctk.CTkLabel(customer_frame,text="", wraplength=200)
        self.name_label.grid(row=1, column=1, padx=(5, 20))

        self.phone_label = ctk.CTkLabel(customer_frame,text="", wraplength=200)
        self.phone_label.grid(row=1, column=2, padx=(5, 0))

        # Create ComboBox
        self.searchbox = ctk.CTkComboBox(customer_frame, values=[])  # Start with no values
        self.searchbox.grid(row=1, column=0, padx=(0, 5))
        self.searchbox.set("")

        # Bind the key release event to the filter function
        self.searchbox.bind("<ButtonPress>", self.auto_fill)

        # Bind Enter key event to process the selected value
        self.searchbox.bind("<Return>", self.process_selection)

        # Bind the selection event to a function
        self.searchbox.bind("<KeyRelease>", self.on_combobox_select)

    def dates_frame(self):
        frame = ctk.CTkFrame(self.borrow_window)
        frame.pack(padx=10, pady=10)
        ctk.CTkLabel(frame, text="Borrow Date:").pack(pady=5)

        # Use DateEntry for date selection
        self.borrow_date_entry = DateEntry(frame,
                                           width=12,
                                           background='darkblue',
                                           foreground='white',
                                           borderwidth=2,
                                           date_pattern='yyyy-mm-dd',
                                           font=("Arial", 24))
        self.borrow_date_entry.pack(pady=5)

        ctk.CTkLabel(frame, text="expected_return_date:").pack(pady=5)
        # Set default return date to one week ahead
        self.return_date_entry = DateEntry(frame,
                                           width=12,
                                           background='darkblue',
                                           foreground='white',
                                           borderwidth=2,
                                           date_pattern='yyyy-mm-dd',
                                           font=("Arial", 24))
        self.return_date_entry.pack(pady=5)

        # Calculate the default return date (one week from today)
        default_return_date = datetime.now() + timedelta(weeks=1)
        self.return_date_entry.set_date(default_return_date)

    def borrowed_books_treeview(self):
        self.borrowed_label = ctk.CTkLabel(self.borrow_window, text="List of books borrowed by")
        self.borrowed_label.pack(pady=10)
        columns = ("Book title", "Book ID", "copy number", "Borrow Date", "Expected Return Date", "Actual Return Date")
        self.borrowed_books_tree = ttk.Treeview(self.borrow_window, columns=columns, show="headings",height=5 )

        for col in columns:
            self.borrowed_books_tree.heading(col, text=col)
        self.borrowed_books_tree.pack(pady=10, fill=ctk.BOTH, expand=True)

        # Add a button to return the selected copy
        self.return_button = ctk.CTkButton(self.borrow_window, text="Return Selected Copy",
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
                    self.db_manager.cursor.execute('''UPDATE borrowed_books
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
                    self.book_info_update()

            else:
                print("The selected Copy is already returned.")

        else:
            print("No book copy selected for return.")


    def save_borrow(self):
        # Implement the logic to save the borrowing details

        if(self.book[8] > 0): # Check if there are available copies
            try:
                self.db_manager.mysql_connect()
                selected_id = self.searchbox.get()
                self.db_manager.cursor.execute('''SELECT * FROM customers WHERE id = %s''', [selected_id])
                customer = self.db_manager.cursor.fetchone()

                if(customer is None):
                    print("Customer not found")
                    return

                # Update the available copies of the book
                self.db_manager.cursor.execute('''UPDATE books
                                        SET available_copies = available_copies - 1
                                        WHERE (id = %s);''',[self.book[6]])

                # Get an available book copy
                self.db_manager.cursor.execute('''SELECT * FROM book_copy
                                       WHERE book_id = %s
                                       and available = TRUE
                                       LIMIT 1''', [self.book[6]])

                book_copy = self.db_manager.cursor.fetchone()

                if book_copy is None:
                    print("No available book copy found")
                    return

                # Mark the book copy as borrowed
                self.db_manager.cursor.execute('''UPDATE book_copy
                                       SET available = FALSE
                                       where book_id = %s
                                       and copy_number = %s''',[book_copy[0], book_copy[1]])

                # Insert borrowing details
                self.db_manager.cursor.execute('''INSERT INTO borrowed_books
                                       (book_id,copy_number,customer_id,borrow_date,expected_return_date)
                                       VALUES (%s, %s, %s,%s,%s);''',
                                       [book_copy[0],book_copy[1],customer[2],
                                       self.borrow_date_entry.get(),
                                       self.return_date_entry.get()])
                # Commit changes
                self.db_manager.connection.commit()
                print("Borrowing details saved successfully.")

                self.borrowed_list_update()
                self.book_info_update()

            except mysql.connector.Error as e:
                print(f"Error during database operation: {e}")

            finally:
                self.db_manager.close_connection()  # Ensure the connection is closed
                # Refresh the UI
                self.borrowed_list_update()
                self.book_info_update()


        else:
            print("There are no copies available to borrow")


    def search_customer(self, input):
        try:
            self.db_manager.mysql_connect()  # Ensure you have an active MySQL connection

            # Prepare the SQL query to search by customer ID
            sql_query = "SELECT * FROM customers WHERE id LIKE %s LIMIT 20"
            self.db_manager.cursor.execute(sql_query, (input + "%",))
            result = self.db_manager.cursor.fetchall()  # Fetch all results

            return result

        except mysql.connector.Error as e:
            print(f"Error searching customer: {e}")
            return []  # Return an empty list in case of an error

        finally:
            self.db_manager.close_connection()  # Ensure the connection is always closed

    def auto_fill(self, event):
        print("we are in the auto_fill method")
        try:
            # Get the current input in the ComboBox
            typed_text = self.searchbox.get()

            # Fetch matching customer results
            query_result = self.search_customer(typed_text)
            if(query_result):
                # Update the values of the ComboBox with new results
                new_values = [str(r[2]) for r in query_result]
                self.searchbox.configure(values=new_values)  # Use configure method

                # Open the drop-down menu automatically after updating the values
                self.searchbox.event_generate('<Down>')
            else:
                # If no result found, clear the ComboBox values
                self.searchbox.configure(values=[])

        except Exception as e:
            print(f"Error during auto-fill: {e}")

    def process_selection(self, event):
        print("we are in the process_selection method")
        self.auto_fill(event)
        if self.searchbox.get():
            # Set the current value to the first result in the list
            self.searchbox.set(self.searchbox.get())
        else:
            print("No matching customer found.")

    def on_combobox_select(self, event):
        print("we are in the on_combobox_select method")
        selected_id = self.searchbox.get()

        # Check if the selected ID is valid before proceeding
        if not selected_id:
            print("No customer ID selected.")
            return

        try:
            self.db_manager.mysql_connect()  # Ensure you have an active MySQL connection

            # Fetch customer details
            sql_query = "SELECT * FROM customers WHERE id = %s"
            self.db_manager.cursor.execute(sql_query, [selected_id])
            result = self.db_manager.cursor.fetchone()

            if result:
                # Update name and phone labels

                self.name_label.configure(text=f"{result[0]}");
                self.phone_label.configure(text= f"{result[1]}")

                # Update borrowed books label and list
                self.borrowed_label.configure(text=(f"List of books borrowed by {result[0]}:"))
                self.borrowed_list_update()

            else:
                print("Customer not found.")

        except mysql.connector.Error as e:
            print(f"Error fetching customer details: {e}")

        finally:
            self.db_manager.close_connection()  # Always close the connection

    def borrowed_list_update(self):
        # Clear the current list of borrowed books
        self.borrowed_books_tree.delete(*self.borrowed_books_tree.get_children())

        selected_id = self.searchbox.get()
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

            # Define an 'overdue' tag with a red background to highlight overdue rows
            self.borrowed_books_tree.tag_configure('overdue', background='red')

            today = datetime.now().date()  # Get today's date

            # Populate the tree with the borrowed books data
            for borrow in borrowed_books:
                title, book_id, copy_number, borrow_date, expected_return_date, actual_return_date = borrow

                # Check if the expected return date is earlier than today's date and actual_return_date is still NULL
                if expected_return_date < today and actual_return_date is None:
                    # Highlight overdue books by applying the 'overdue' tag
                    self.borrowed_books_tree.insert("", "end", values=borrow, tags=('overdue',))
                else:
                    # Regular insertion without highlighting
                    self.borrowed_books_tree.insert("", "end", values=borrow)

        except mysql.connector.Error as e:
            print(f"Error fetching borrowed books: {e}")

        finally:
            self.db_manager.close_connection()  # Always close the connection

    def book_info_update(self):
        try:
            self.db_manager.mysql_connect()
            self.db_manager.cursor.execute("SELECT * FROM BOOKS WHERE id = %s", [self.book[6]])
            book_info = self.db_manager.cursor.fetchone()

            if book_info:
                self.book = book_info
                self.available_copy_count_label.configure(text=f"Available Copies:\n{self.book[8]}")

            else:
                print(f"Book with ID {self.book[6]} not found.")
                self.available_copy_count_label.configure(text="Book not found.")

        except mysql.connector.Error as e:
            print(f"Error fetching book information: {e}")

        finally:
            self.db_manager.close_connection()  # Ensure connection is always closed

