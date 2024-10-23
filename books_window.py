from tkinter import ttk
import customtkinter as ctk
import mysql.connector
from database_manager import DatabaseManager
from borrow_book_window import BorrowBookWindow

class BooksWindow:
    def __init__(self, master, button_text):
        self.master = master
        self.window = ctk.CTkToplevel(master)  # יצירת חלון חדש
        self.window.title(button_text)
        self.db_manager = DatabaseManager()
        self.books = None
        self.setup_window(button_text)
        self.current_sort_column = None  # Track the currently sorted column
        self.sort_order_ascending = True  # Default sort order


    def setup_window(self, button_text):
        # Set the geometry for the new window
        self.window.geometry(f"1200x600")
        self.create_widgets(button_text)
        self.update_table()


    def create_widgets(self, button_text):
        header_label = ctk.CTkLabel(self.window, text=f"the book managment tool")
        header_label.pack(pady=12,padx=10)

        self.create_buttons()   # Create buttons
        self.create_table()     # Create table

        self.window.protocol("WM_DELETE_WINDOW", self.close)  # טיפול בסגירה של החלון

    def create_buttons(self):
        button_frame = ctk.CTkFrame(self.window)
        button_frame.pack(pady=12,padx=10)

        self.create_button(button_frame, "ספר הוסף", self.add_book)
        self.create_button(button_frame, "ספר מחק", self.delete_book)
        self.create_button(button_frame, "ספר השאל/החזר", self.borrow_book)
        self.create_button(button_frame, "ספר ערוך", self.edit_book)

        search_button = ctk.CTkButton(button_frame, text="חפש", command=self.search_book)
        search_button.pack(side='left', padx=(150,0))
        self.search_entry = ctk.CTkEntry(button_frame, width=200)  # Search entry box
        self.search_entry.insert(0, "ספר שם")  # Placeholder text
        self.search_entry.pack(side='left')

    def create_table(self):
        self.frame = ctk.CTkFrame(self.window)
        self.frame.pack(expand=True, fill='both')
        # Create a style for the Treeview (adjust font size here)
        style = ttk.Style()
        style.configure("Treeview", font=("Helvetica", 20), rowheight=60)  # Adjust font size
        style.configure("Treeview.Heading", font=("Helvetica", 26, "bold"))

        # Creating the Treeview
        self.tree = ttk.Treeview(self.frame, columns=(
        "Title", "Authors", "Description", "Category", "Publisher", "Publish Date (Year)", "id"), show='headings')
        self.tree.pack(side='left', expand=True, fill='both')

        # Creating Scrollbar
        scrollbar = ttk.Scrollbar(self.frame, orient='vertical', command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')

        self.tree.configure(yscrollcommand=scrollbar.set)

        for col in self.tree['columns']:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=100, stretch=True)  # Allow columns to be resized

        self.tree.column("Title", width=150)

        # Bind the column headers to sorting
        for col in self.tree['columns']:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))

        # Bind the selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        # Bind double click event
        self.tree.bind('<Double-Button-1>', self.on_double_click)

    def create_button(self, parent, text, command):
        button = ctk.CTkButton(parent, text=text, command=command)
        button.pack(side='left', padx=5)


    def on_tree_select(self, event):
        # Get selected item
        selected_item = self.tree.selection()

        # Check if something is selected
        if selected_item:
            # Get the values of the selected item
            item = self.tree.item(selected_item)
            values = item['values']

            # Display the selected values (you can handle them as needed)
            print("Selected Item:", values)


    def update_table(self):
        """Update the Treeview with data from the database."""
        try:
            self.db_manager.mysql_connect() # Connect to the database
            self.clear_treeview()  # Clear the existing data

            # Fetch all books from the database
            self.books = self.fetch_books_from_db()

            # Insert each book's data into the treeview
            self.populate_treeview(self.books)

        except mysql.connector.Error as e:
            print(f"Error updating table: {e}")  # Log the error

        finally:
            self.db_manager.close_connection()  # Ensure the connection is closed

    def fetch_books_from_db(self):
        """Fetch all books from the database."""
        self.db_manager.cursor.execute("SELECT * FROM books")
        return self.db_manager.cursor.fetchall()

    def populate_treeview(self, books):
        """Insert book data into the Treeview."""
        for book in books:
            self.tree.insert('', 'end', values=book)

    def clear_treeview(self):
        """Clear all existing entries in the Treeview."""
        self.tree.delete(*self.tree.get_children())

    def close(self):
        self.window.withdraw()  # Hide the current window
        self.master.deiconify()  # Show the main window again

    def add_book(self):
        self.create_add_book_window()


    def save_book(self, title, authors, description, category, publisher, publish_date, available_copies, add_window):
        """Save a new book to the database."""
        try:
            available_copies = int(available_copies)

            # Connect to the database and insert the book
            self.db_manager.mysql_connect()

            # Insert the book into the database
            self.insert_book(title, authors, description, category, publisher, publish_date, available_copies)

            if available_copies > 0:
                # Insert available copies into the book_copy table
                self.insert_book_copies(self.db_manager.cursor.lastrowid, available_copies)

            self.db_manager.connection.commit()
            self.update_table()

            add_window.destroy()

        except mysql.connector.Error as e:
            print("Error saving book:", e)

        finally:
            self.db_manager.close_connection()
            add_window.destroy()

    def insert_book(self, title, authors, description, category, publisher, publish_date, available_copies):
        """Insert a book into the database."""
        sql = """
            INSERT INTO books 
            (Title, Authors, Description, Category, Publisher, Publish_Date, total_copies, available_copies) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.db_manager.cursor.execute(sql, (title, authors, description, category, publisher, publish_date, available_copies, available_copies))

    def insert_book_copies(self, book_id, available_copies):
        """Insert available copies into the book_copy table."""
        sql = "INSERT INTO book_copy (book_id) VALUES " + ', '.join(['(%s)'] * available_copies)
        values = [book_id] * available_copies
        self.db_manager.cursor.execute(sql, values)

    def create_input_field(self, parent, label_text, default=None):
        """Create a label and entry field."""
        ctk.CTkLabel(parent, text=label_text).pack()
        entry = ctk.CTkEntry(parent,width=500)
        entry.pack()
        if default:
            entry.insert(0, default)
        return entry

    def delete_book(self):
        selected_item = self.tree.selection()

        # Check if something is selected
        if selected_item:
            # Get the values of the selected item
            item = self.tree.item(selected_item)
            values = item['values']
            id_to_delete = values[6]

            print(f"Attempting to delete book with ID: {id_to_delete}")  # Debug output
            self.perform_delete(id_to_delete)

        else:
            print("No item selected for deletion.")  # Debug output


    def perform_delete(self, id_to_delete):
        try:
            self.db_manager.mysql_connect()  # Establish MySQL connection
            # Execute delete copies query
            self.db_manager.cursor.execute("DELETE FROM book_copy WHERE book_id = %s", (id_to_delete,))
            # Execute delete query
            self.db_manager.cursor.execute("DELETE FROM books WHERE id = %s", (id_to_delete,))
            self.db_manager.connection.commit()  # Commit the changes
            print("Book deleted successfully.")  # Debug output
            self.update_table()  # Refresh the table to reflect changes
        except mysql.connector.Error as err:
            print(f"Error: {err}")  # Print error message for debugging
        finally:
            self.db_manager.close_connection()

    def borrow_book(self):
        selected_item = self.tree.selection()
        if selected_item:
            # Get the values of the selected item
            item = self.tree.item(selected_item)
            book = item['values']
            BorrowBookWindow(self.window,book)
        else:
            print("No Selection, Please select a book.")



    def edit_book(self):
        selected_item = self.tree.selection()

        # Check if something is selected
        if selected_item:
            # Get the values of the selected item
            item = self.tree.item(selected_item)
            values = item['values']  # This should contain all the details of the book

            # Create a new window to edit the book
            edit_window = ctk.CTkToplevel(self.window)
            edit_window.title("Edit Book")
            edit_window.geometry(f"600x400")

            # Create entry fields with current book details
            title_entry = self.create_input_field(edit_window, "Title", values[0])
            authors_entry = self.create_input_field(edit_window, "Authors", values[1])
            description_entry = self.create_input_field(edit_window, "Description", values[2])
            category_entry = self.create_input_field(edit_window, "Category", values[3])
            publisher_entry = self.create_input_field(edit_window, "Publisher", values[4])
            publish_date_entry = self.create_input_field(edit_window, "Publish Date", values[5])

            # Save button to update the book in the database
            ctk.CTkButton(edit_window, text="Save", command=lambda: self.save_edited_book(
                values[6],  # This should be the book ID for updating
                title_entry.get(),
                authors_entry.get(),
                description_entry.get(),
                category_entry.get(),
                publisher_entry.get(),
                publish_date_entry.get(),
                edit_window
            )).pack()

    def create_add_book_window(self):
        """Create a window to add a new book."""
        add_window = ctk.CTkToplevel(self.window)
        add_window.title("Add Book")
        add_window.geometry(f"600x500")

        # Create input fields
        self.title_entry = self.create_input_field(add_window, "Title")
        self.authors_entry = self.create_input_field(add_window, "Authors")
        self.description_entry = self.create_input_field(add_window, "Description")
        self.category_entry = self.create_input_field(add_window, "Category")
        self.publisher_entry = self.create_input_field(add_window, "Publisher")
        self.publish_date_entry = self.create_input_field(add_window, "Publish Date")
        self.available_copies_entry = self.create_input_field(add_window, "Available Copies", default="0")

        # Save button
        ctk.CTkButton(add_window, text="Save", command=lambda: self.save_book(
            self.title_entry.get(),
            self.authors_entry.get(),
            self.description_entry.get(),
            self.category_entry.get(),
            self.publisher_entry.get(),
            self.publish_date_entry.get(),
            self.available_copies_entry.get(),
            add_window
        )).pack()

    def save_edited_book(self, book_id, title, authors, description, category, publisher, publish_date, edit_window):
        try:
            self.db_manager.mysql_connect()
            # Update the book in the database
            self.db_manager.cursor.execute(
                "UPDATE books SET Title = %s, Authors = %s, Description = %s, Category = %s, Publisher = %s, Publish_Date = %s WHERE id = %s",
                (title, authors, description, category, publisher, publish_date, book_id)
            )
            self.db_manager.connection.commit()  # Commit the changes
            print("Book edited successfully.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")  # Debug output
            print("Failed to update the book.")

        finally:
            self.db_manager.close_connection()
            self.update_table()  # Update the table to reflect changes
            edit_window.destroy()  # Close the edit window

    def search_book(self):
        # Clear existing entries in the treeview
        self.clear_treeview()

        search_text = self.search_entry.get()
        like_pattern = f"%{search_text}%"  # Create the pattern for LIKE
        print(f"Attempting to search book that contains: {search_text}")  # Debug output

        try:
            self.db_manager.mysql_connect()  # Establish MySQL connection
            self.db_manager.cursor.execute("select * from books where title like %s", [like_pattern])

            self.books = self.db_manager.cursor.fetchall()

            # Check if any books were found
            if not self.books:
                print("No books found matching your search criteria.")  # Inform the user
                return

            # Insert each found book into the treeview
            for book in self.books:
                self.tree.insert('', 'end', values=book)  # Insert book data directly

        except mysql.connector.Error as err:
            print(f"Error: {err}")  # Print error message for debugging
        finally:
            self.db_manager.close_connection()

    def on_close(self):
        self.window.destroy()  # Close the window

    def sort_by_column(self, col):
        # Check if the same column is clicked again
        if self.current_sort_column == col:
            self.sort_order_ascending = not self.sort_order_ascending  # Toggle sort order
        else:
            self.current_sort_column = col  # Update the current sort column
            self.sort_order_ascending = True  # Reset to ascending order

        # Sort the data by the selected column
        sorted_books = sorted(
            self.books,
            key=lambda x: x[self.tree['columns'].index(col)],
            reverse=not self.sort_order_ascending  # Reverse based on sort order
        )

        # Clear the existing data in the treeview
        self.clear_treeview()

        # Insert sorted data back into the treeview
        for book in sorted_books:
            self.tree.insert('', 'end', values=book)

    def on_double_click(self, event):
        self.borrow_book()
