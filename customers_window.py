from tkinter import ttk
import customtkinter as ctk
import mysql.connector
from database_manager import DatabaseManager
from customer_info_window import CustomerInfoWindow

class ColorScheme:
    PRIMARY_BACKGROUND = "#384B70"
    BUTTON_BACKGROUND = "#4A628A"
    BUTTON_TEXT_COLOR = "#FFFFFF"

class CustomersWindow:
    def __init__(self, master, button_text):
        self.master = master
        self.window = ctk.CTkToplevel(master)  # יצירת חלון חדש
        self.window.title(button_text)
        self.db_manager = DatabaseManager()
        self.customers = None
        self.setup_window(button_text)
        self.current_sort_column = None  # Track the currently sorted column
        self.sort_order_ascending = True  # Default sort order

    def setup_window(self, button_text):
        self.window.geometry(f"1200x600")
        self.create_widgets(button_text)
        self.update_table()

    def create_widgets(self, button_text):
        header_label = ctk.CTkLabel(self.window, text=f"the customers managment tool")
        header_label.pack(pady=20)

        self.create_buttons()   # Create buttons
        self.create_table()     # Create table

        self.window.protocol("WM_DELETE_WINDOW", self.close)

    def create_buttons(self):
        button_frame = ctk.CTkFrame(self.window)
        button_frame.pack(pady=10)

        self.create_button(button_frame, "לקוח הוסף", self.add_customer)
        self.create_button(button_frame, "לקוח מחק", self.delete_customer)
        self.create_button(button_frame, "לקוח ערוך", self.edit_customer)

        search_button = ctk.CTkButton(button_frame, text="חפש", command=self.search_customer)
        search_button.pack(side='left', padx=(150,0))
        self.search_entry = ctk.CTkEntry(button_frame, width=200)  # Search entry box
        self.search_entry.insert(0, "שם/טלפון")  # Placeholder text
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
        "Name", "Phone Number", "ID"), show='headings')
        self.tree.pack(side='left', expand=True, fill='both')

        # Creating Scrollbar
        scrollbar = ttk.Scrollbar(self.frame, orient='vertical', command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')

        self.tree.configure(yscrollcommand=scrollbar.set)

        for col in self.tree['columns']:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=100, stretch=True)  # Allow columns to be resized


        # Bind the column headers to sorting
        for col in self.tree['columns']:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))

        # Bind the selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        # Bind double click event
        self.tree.bind('<Double-Button-1>', self.on_double_click)


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

            # Fetch all customers from the database
            self.customers = self.fetch_customers_from_db()

            # Insert each customer's data into the treeview
            self.populate_treeview(self.customers)

        except mysql.connector.Error as e:
            print(f"Error updating table: {e}")  # Log the error

        finally:
            self.db_manager.close_connection()  # Ensure the connection is closed

    def fetch_customers_from_db(self):
        """Fetch all customers from the database."""
        self.db_manager.cursor.execute("SELECT * FROM customers")
        return self.db_manager.cursor.fetchall()

    def populate_treeview(self, customers):
        """Insert customers data into the Treeview."""
        for customer in customers:
            self.tree.insert('', 'end', values=customer)

    def clear_treeview(self):
        """Clear all existing entries in the Treeview."""
        self.tree.delete(*self.tree.get_children())

    def create_button(self, parent, text, command):
        button = ctk.CTkButton(parent, text=text, command=command)
        button.pack(side='left', padx=5)

    def close(self):
        self.window.withdraw()  # Hide the current window
        self.master.deiconify()  # Show the main window again

    def add_customer(self):
        self.create_add_customer_window()


    def save_customer(self, name, phone_number, add_window):
        """Save a new customer to the database."""
        try:
            # Connect to the database and insert the customer
            self.db_manager.mysql_connect()

            # Insert the customer into the database
            self.insert_customer(name, phone_number)

            self.db_manager.connection.commit()
            self.update_table()

            add_window.destroy()

        except mysql.connector.Error as e:
            print("Error saving customer:", e)

        finally:
            self.db_manager.close_connection()
            add_window.destroy()

    def insert_customer(self, name, phone_number):
        """Insert a customer into the database."""
        sql = """
            INSERT INTO customers 
            (customer_name, phone_number) 
            VALUES (%s, %s)
        """
        self.db_manager.cursor.execute(sql, (name, phone_number))

    def create_input_field(self, parent, label_text, default=None):
        """Create a label and entry field."""
        ctk.CTkLabel(parent, text=label_text).pack()
        entry = ctk.CTkEntry(parent)
        entry.pack()
        if default:
            entry.insert(0, default)
        return entry

    def delete_customer(self):
        selected_item = self.tree.selection()

        # Check if something is selected
        if selected_item:
            # Get the values of the selected item
            item = self.tree.item(selected_item)
            values = item['values']
            id_to_delete = values[2]

            print(f"Attempting to delete customer with ID: {id_to_delete}")  # Debug output
            self.perform_delete(id_to_delete)

        else:
            print("No item selected for deletion.")  # Debug output

    def perform_delete(self, id_to_delete):
        try:
            self.db_manager.mysql_connect()  # Establish MySQL connection
            # CHEKC IF THERE IS AN UNRETURNED BOOK BEFORE DELETION
            ###################################
            # Execute delete query
            self.db_manager.cursor.execute("DELETE FROM customers WHERE id = %s", (id_to_delete,))
            self.db_manager.connection.commit()  # Commit the changes
            print("customer deleted successfully.")  # Debug output
            self.update_table()  # Refresh the table to reflect changes
        except mysql.connector.Error as err:
            print(f"Error: {err}")  # Print error message for debugging
        finally:
            self.db_manager.close_connection()


    def edit_customer(self):
        selected_item = self.tree.selection()

        # Check if something is selected
        if selected_item:
            # Get the values of the selected item
            item = self.tree.item(selected_item)
            values = item['values']  # This should contain all the details of the customer

            # Create a new window to edit the customer
            edit_window = ctk.CTkToplevel(self.window)
            edit_window.geometry(f"200x150")
            edit_window.title("Edit Customer")

            # Create entry fields with current Customer details
            name_entry = self.create_input_field(edit_window, "Name", values[0])
            phone_entry = self.create_input_field(edit_window, "Phone Number", values[1])

            # Save button to update the customer in the database
            ctk.CTkButton(edit_window, text="Save", command=lambda: self.save_edited_customer(
                values[2],  # This should be the customer ID for updating
                name_entry.get(),
                phone_entry.get(),
                edit_window
            )).pack()

    def save_edited_customer(self,customer_id, customer_name, phone_number, edit_window):
        try:
            self.db_manager.mysql_connect()
            # Update the customer in the database
            self.db_manager.cursor.execute(
                "UPDATE customers SET customer_name = %s, phone_number = %s WHERE id = %s",
                (customer_name, phone_number,customer_id)
            )
            self.db_manager.connection.commit()  # Commit the changes
            print("Customer edited successfully.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")  # Debug output
            print("Failed to update the Customer.")

        finally:
            self.db_manager.close_connection()
            self.update_table()  # Update the table to reflect changes
            edit_window.destroy()  # Close the edit window


    def create_add_customer_window(self):
        """Create a window to add a new customer."""
        add_window = ctk.CTkToplevel(self.window)
        add_window.geometry(f"200x150")
        add_window.title("Add customer")

        # Create input fields
        self.name_entry = self.create_input_field(add_window, "Name")
        self.phone_entry = self.create_input_field(add_window, "Phone Number")

        # Save button
        ctk.CTkButton(add_window, text="Save", command=lambda: self.save_customer(
            self.name_entry.get(),
            self.phone_entry.get(),
            add_window
        )).pack()


    def search_customer(self):
        # Clear existing entries in the treeview
        self.clear_treeview()

        search_text = self.search_entry.get()
        like_pattern = f"%{search_text}%"  # Create the pattern for LIKE
        print(f"Attempting to search customer that contains: {search_text}")  # Debug output

        try:
            self.db_manager.mysql_connect()  # Establish MySQL connection
            self.db_manager.cursor.execute('''select * from customers
                                              where phone_number LIKE %s or customer_name LIKE %s''', [like_pattern,like_pattern])

            self.customers = self.db_manager.cursor.fetchall()

            # Check if any customers were found
            if not self.customers:
                print("No customers found matching your search criteria.")  # Inform the user
                return

            # Insert each found customers into the treeview
            for customer in self.customers:
                self.tree.insert('', 'end', values=customer)  # Insert customer data directly

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
        sorted_customers = sorted(
            self.customers,
            key=lambda x: x[self.tree['columns'].index(col)],
            reverse=not self.sort_order_ascending  # Reverse based on sort order
        )

        # Clear the existing data in the treeview
        self.clear_treeview()

        # Insert sorted data back into the treeview
        for customer in sorted_customers:
            self.tree.insert('', 'end', values=customer)

    def on_double_click(self, event):
        self.customer_info()

    def customer_info(self):
        selected_item = self.tree.selection()
        if selected_item:
            # Get the values of the selected item
            item = self.tree.item(selected_item)
            customer = item['values']
            CustomerInfoWindow(self.window,customer)
        else:
            print("No Selection, Please select a customer.")




