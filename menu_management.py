import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
import json
from PIL import Image, ImageTk
import os

class MenuManagementFrame(ctk.CTkFrame):
    def __init__(self, parent, data_manager, colors):
        super().__init__(parent, fg_color=colors["background"])
        self.data_manager = data_manager
        self.colors = colors
        self.parent = parent
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Menu items list takes most space
        
        # Header
        self.header = ctk.CTkLabel(
            self, 
            text="Menu Management", 
            font=("Roboto", 24, "bold"),
            text_color=self.colors["primary"]
        )
        self.header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Buttons frame
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Add item button
        self.add_button = ctk.CTkButton(
            self.button_frame,
            text="Add Item (Ctrl+N)",
            font=("Roboto", 12),
            fg_color=self.colors["accent"],
            hover_color=self.colors["secondary"],
            command=self.add_new_item
        )
        self.add_button.grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        
        # Edit item button
        self.edit_button = ctk.CTkButton(
            self.button_frame,
            text="Edit Selected",
            font=("Roboto", 12),
            fg_color=self.colors["secondary"],
            hover_color="#0771c0",
            command=self.edit_selected_item
        )
        self.edit_button.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        # Delete item button
        self.delete_button = ctk.CTkButton(
            self.button_frame,
            text="Delete Selected",
            font=("Roboto", 12),
            fg_color="#E57373",
            hover_color="#C62828",
            command=self.delete_selected_item
        )
        self.delete_button.grid(row=0, column=2, padx=5, pady=10, sticky="ew")
        
        # Export button
        self.export_button = ctk.CTkButton(
            self.button_frame,
            text="Export Menu (Ctrl+E)",
            font=("Roboto", 12),
            fg_color=self.colors["primary"],
            hover_color="#1e2526",
            command=self.export_data
        )
        self.export_button.grid(row=0, column=3, padx=5, pady=10, sticky="ew")
        
        # Search frame
        self.search_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.search_frame.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.search_frame.grid_columnconfigure(1, weight=1)
        
        # Search label
        self.search_label = ctk.CTkLabel(
            self.search_frame, 
            text="Search:", 
            font=("Roboto", 12),
            text_color=self.colors["primary"]
        )
        self.search_label.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="w")
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_menu_items)
        self.search_entry = ctk.CTkEntry(
            self.search_frame, 
            font=("Roboto", 12),
            textvariable=self.search_var,
            placeholder_text="Search menu items..."
        )
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Menu items frame
        self.menu_items_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color=self.colors["background"]
        )
        self.menu_items_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.menu_items_frame.grid_columnconfigure(0, weight=1)
        
        # Initialize menu items display
        self.menu_items = []
        self.menu_item_frames = []
        self.selected_item = None
        
        # Load menu items
        self.refresh_data()
    
    def refresh_data(self):
        """Refresh menu items data and update display"""
        # Clear existing items
        for frame in self.menu_item_frames:
            frame.destroy()
        
        self.menu_item_frames = []
        
        # Get updated menu items
        self.menu_items = self.data_manager.get_menu_items()
        
        # Display menu items
        self.display_menu_items(self.menu_items)
    
    def filter_menu_items(self, *args):
        """Filter menu items based on search text"""
        search_text = self.search_var.get().lower()
        
        if not search_text:
            # If search is empty, display all items
            self.display_menu_items(self.menu_items)
        else:
            # Filter items
            filtered_items = [
                item for item in self.menu_items
                if search_text in item.get('name', '').lower() or 
                   search_text in item.get('category', '').lower() or
                   search_text in str(item.get('price', '')).lower()
            ]
            self.display_menu_items(filtered_items)
    
    def display_menu_items(self, items_to_display):
        """Display menu items in the scrollable frame"""
        # Clear existing items
        for frame in self.menu_item_frames:
            frame.destroy()
        
        self.menu_item_frames = []
        
        # No items message
        if not items_to_display:
            no_items_label = ctk.CTkLabel(
                self.menu_items_frame, 
                text="No menu items found. Add a new item to get started.",
                font=("Roboto", 14),
                text_color=self.colors["primary"]
            )
            no_items_label.grid(row=0, column=0, padx=20, pady=20)
            self.menu_item_frames.append(no_items_label)
            return
        
        # Sort items by category and name
        sorted_items = sorted(items_to_display, key=lambda x: (x.get('category', ''), x.get('name', '')))
        
        # Group items by category
        categories = {}
        for item in sorted_items:
            category = item.get('category', 'Uncategorized')
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        # Display items by category
        row_counter = 0
        for category, category_items in categories.items():
            # Category header
            category_label = ctk.CTkLabel(
                self.menu_items_frame,
                text=category,
                font=("Roboto", 16, "bold"),
                text_color=self.colors["secondary"]
            )
            category_label.grid(row=row_counter, column=0, padx=10, pady=(15, 5), sticky="w")
            self.menu_item_frames.append(category_label)
            row_counter += 1
            
            # Item headers (column titles)
            headers_frame = ctk.CTkFrame(self.menu_items_frame, fg_color="transparent")
            headers_frame.grid(row=row_counter, column=0, padx=10, pady=(0, 5), sticky="ew")
            headers_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
            
            name_header = ctk.CTkLabel(
                headers_frame, text="Item Name", 
                font=("Roboto", 12, "bold"),
                text_color=self.colors["primary"]
            )
            name_header.grid(row=0, column=0, padx=5, sticky="w")
            
            price_header = ctk.CTkLabel(
                headers_frame, text="Price", 
                font=("Roboto", 12, "bold"),
                text_color=self.colors["primary"]
            )
            price_header.grid(row=0, column=1, padx=5, sticky="w")
            
            shortcut_header = ctk.CTkLabel(
                headers_frame, text="Shortcut", 
                font=("Roboto", 12, "bold"),
                text_color=self.colors["primary"]
            )
            shortcut_header.grid(row=0, column=2, padx=5, sticky="w")
            
            stock_header = ctk.CTkLabel(
                headers_frame, text="In Stock", 
                font=("Roboto", 12, "bold"),
                text_color=self.colors["primary"]
            )
            stock_header.grid(row=0, column=3, padx=5, sticky="w")
            
            self.menu_item_frames.append(headers_frame)
            row_counter += 1
            
            # Items
            for item in category_items:
                item_frame = self.create_menu_item_frame(item)
                item_frame.grid(row=row_counter, column=0, padx=10, pady=5, sticky="ew")
                self.menu_item_frames.append(item_frame)
                row_counter += 1
    
    def create_menu_item_frame(self, item):
        """Create a frame for a single menu item"""
        frame = ctk.CTkFrame(
            self.menu_items_frame,
            fg_color=self.colors["background"],
            border_width=1,
            border_color="#E0E0E0",
            corner_radius=8
        )
        frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Store item ID in the frame for reference
        frame.item_id = item.get('id')
        
        # Item name
        name_label = ctk.CTkLabel(
            frame,
            text=item.get('name', 'Unnamed'),
            font=("Roboto", 14),
            text_color=self.colors["primary"]
        )
        name_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Price
        price_text = f"₹{item.get('price', '0.00')}"
        price_label = ctk.CTkLabel(
            frame,
            text=price_text,
            font=("Roboto", 14),
            text_color=self.colors["primary"]
        )
        price_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Keyboard shortcut
        shortcut = item.get('shortcut', '-')
        shortcut_label = ctk.CTkLabel(
            frame,
            text=shortcut,
            font=("Roboto", 14),
            text_color=self.colors["secondary"]
        )
        shortcut_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        
        # Stock status
        inventory = self.data_manager.get_inventory()
        stock_quantity = 0
        
        for inv_item in inventory:
            if inv_item.get('name') == item.get('name'):
                stock_quantity = inv_item.get('quantity', 0)
                break
        
        stock_color = "#00B894" if stock_quantity > 0 else "#FF5252"
        stock_text = f"{stock_quantity} in stock"
        
        stock_label = ctk.CTkLabel(
            frame,
            text=stock_text,
            font=("Roboto", 14),
            text_color=stock_color
        )
        stock_label.grid(row=0, column=3, padx=10, pady=10, sticky="w")
        
        # Add selection behavior
        frame.bind("<Button-1>", lambda event, f=frame: self.select_item(f))
        name_label.bind("<Button-1>", lambda event, f=frame: self.select_item(f))
        price_label.bind("<Button-1>", lambda event, f=frame: self.select_item(f))
        shortcut_label.bind("<Button-1>", lambda event, f=frame: self.select_item(f))
        stock_label.bind("<Button-1>", lambda event, f=frame: self.select_item(f))
        
        # Double-click to edit
        frame.bind("<Double-1>", lambda event, f=frame: self.edit_item(f.item_id))
        name_label.bind("<Double-1>", lambda event, f=frame: self.edit_item(f.item_id))
        price_label.bind("<Double-1>", lambda event, f=frame: self.edit_item(f.item_id))
        shortcut_label.bind("<Double-1>", lambda event, f=frame: self.edit_item(f.item_id))
        stock_label.bind("<Double-1>", lambda event, f=frame: self.edit_item(f.item_id))
        
        return frame
    
    def select_item(self, frame):
        """Handle item selection"""
        # Deselect previously selected item
        if self.selected_item:
            self.selected_item.configure(
                fg_color=self.colors["background"],
                border_color="#E0E0E0"
            )
        
        # Select new item
        frame.configure(
            fg_color="#E3F2FD",
            border_color=self.colors["secondary"]
        )
        self.selected_item = frame
    
    def add_new_item(self):
        """Open dialog to add a new menu item"""
        self.item_dialog = ItemDialog(self, self.colors, self.data_manager)
        self.wait_window(self.item_dialog)
        self.refresh_data()
    
    def edit_selected_item(self):
        """Edit the selected menu item"""
        if not self.selected_item:
            messagebox.showinfo("Select Item", "Please select an item to edit")
            return
        
        self.edit_item(self.selected_item.item_id)
    
    def edit_item(self, item_id):
        """Open dialog to edit a menu item"""
        # Find the item data
        item_data = None
        for item in self.menu_items:
            if item.get('id') == item_id:
                item_data = item
                break
        
        if not item_data:
            messagebox.showerror("Error", "Item not found")
            return
        
        self.item_dialog = ItemDialog(self, self.colors, self.data_manager, item_data)
        self.wait_window(self.item_dialog)
        self.refresh_data()
    
    def delete_selected_item(self):
        """Delete the selected menu item"""
        if not self.selected_item:
            messagebox.showinfo("Select Item", "Please select an item to delete")
            return
        
        item_id = self.selected_item.item_id
        
        # Find item name for confirmation
        item_name = "this item"
        for item in self.menu_items:
            if item.get('id') == item_id:
                item_name = item.get('name')
                break
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to delete '{item_name}'?"
        )
        
        if confirm:
            success, message = self.data_manager.delete_menu_item(item_id)
            
            if success:
                messagebox.showinfo("Success", message)
                self.refresh_data()
            else:
                messagebox.showerror("Error", message)
    
    def export_data(self):
        """Export menu data to Excel"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Export Menu to Excel"
        )
        
        if not filepath:
            return  # User cancelled
        
        success, message = self.data_manager.export_menu_to_excel(filepath)
        
        if success:
            messagebox.showinfo("Export Successful", message)
        else:
            messagebox.showerror("Export Failed", message)


class ItemDialog(ctk.CTkToplevel):
    def __init__(self, parent, colors, data_manager, item_data=None):
        super().__init__(parent)
        
        self.colors = colors
        self.data_manager = data_manager
        self.parent = parent
        self.item_data = item_data  # None for new item, dict for editing
        
        # Configure window
        self.title("Add Menu Item" if not item_data else "Edit Menu Item")
        self.geometry("500x550")
        self.resizable(False, False)
        
        # Make it modal
        self.transient(parent)
        self.grab_set()
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        self.header = ctk.CTkLabel(
            self, 
            text="Add New Menu Item" if not item_data else f"Edit {item_data.get('name', 'Item')}",
            font=("Roboto", 18, "bold"),
            text_color=self.colors["primary"]
        )
        self.header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Form container
        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.form_frame.grid_columnconfigure(1, weight=1)
        
        # Item name
        self.name_label = ctk.CTkLabel(
            self.form_frame,
            text="Item Name:",
            font=("Roboto", 14),
            text_color=self.colors["primary"]
        )
        self.name_label.grid(row=0, column=0, padx=5, pady=10, sticky="w")
        
        self.name_var = tk.StringVar(value=item_data.get('name', '') if item_data else '')
        self.name_entry = ctk.CTkEntry(
            self.form_frame,
            font=("Roboto", 14),
            textvariable=self.name_var,
            placeholder_text="Enter item name"
        )
        self.name_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        # Category
        self.category_label = ctk.CTkLabel(
            self.form_frame,
            text="Category:",
            font=("Roboto", 14),
            text_color=self.colors["primary"]
        )
        self.category_label.grid(row=1, column=0, padx=5, pady=10, sticky="w")
        
        # Get existing categories
        menu_items = self.data_manager.get_menu_items()
        categories = sorted(list(set(item.get('category', 'Uncategorized') for item in menu_items)))
        if not categories:
            categories = ['Drinks', 'Food', 'Snacks', 'Desserts']
        if 'Uncategorized' not in categories:
            categories.append('Uncategorized')
        
        self.category_var = tk.StringVar(value=item_data.get('category', 'Uncategorized') if item_data else 'Uncategorized')
        self.category_combobox = ctk.CTkComboBox(
            self.form_frame,
            font=("Roboto", 14),
            values=categories,
            variable=self.category_var
        )
        self.category_combobox.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        
        # Price
        self.price_label = ctk.CTkLabel(
            self.form_frame,
            text="Price (₹):",
            font=("Roboto", 14),
            text_color=self.colors["primary"]
        )
        self.price_label.grid(row=2, column=0, padx=5, pady=10, sticky="w")
        
        self.price_var = tk.StringVar(value=str(item_data.get('price', '0.00')) if item_data else '0.00')
        self.price_entry = ctk.CTkEntry(
            self.form_frame,
            font=("Roboto", 14),
            textvariable=self.price_var,
            placeholder_text="Enter price"
        )
        self.price_entry.grid(row=2, column=1, padx=5, pady=10, sticky="ew")
        
        # Description
        self.desc_label = ctk.CTkLabel(
            self.form_frame,
            text="Description:",
            font=("Roboto", 14),
            text_color=self.colors["primary"]
        )
        self.desc_label.grid(row=3, column=0, padx=5, pady=10, sticky="w")
        
        self.desc_var = tk.StringVar(value=item_data.get('description', '') if item_data else '')
        self.desc_entry = ctk.CTkEntry(
            self.form_frame,
            font=("Roboto", 14),
            textvariable=self.desc_var,
            placeholder_text="Enter description (optional)"
        )
        self.desc_entry.grid(row=3, column=1, padx=5, pady=10, sticky="ew")
        
        # Keyboard shortcut
        self.shortcut_label = ctk.CTkLabel(
            self.form_frame,
            text="Keyboard Shortcut:",
            font=("Roboto", 14),
            text_color=self.colors["primary"]
        )
        self.shortcut_label.grid(row=4, column=0, padx=5, pady=10, sticky="w")
        
        self.shortcut_var = tk.StringVar(value=item_data.get('shortcut', '') if item_data else '')
        self.shortcut_entry = ctk.CTkEntry(
            self.form_frame,
            font=("Roboto", 14),
            textvariable=self.shortcut_var,
            placeholder_text="e.g., Ctrl+S (optional)"
        )
        self.shortcut_entry.grid(row=4, column=1, padx=5, pady=10, sticky="ew")
        
        # Initial stock
        self.stock_label = ctk.CTkLabel(
            self.form_frame,
            text="Initial Stock:",
            font=("Roboto", 14),
            text_color=self.colors["primary"]
        )
        self.stock_label.grid(row=5, column=0, padx=5, pady=10, sticky="w")
        
        # Get current stock if editing
        initial_stock = 0
        if item_data:
            inventory = self.data_manager.get_inventory()
            for inv_item in inventory:
                if inv_item.get('name') == item_data.get('name'):
                    initial_stock = inv_item.get('quantity', 0)
                    break
        
        self.stock_var = tk.StringVar(value=str(initial_stock))
        self.stock_entry = ctk.CTkEntry(
            self.form_frame,
            font=("Roboto", 14),
            textvariable=self.stock_var,
            placeholder_text="Enter initial stock quantity"
        )
        self.stock_entry.grid(row=5, column=1, padx=5, pady=10, sticky="ew")
        
        # Buttons frame
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=2, column=0, padx=20, pady=(20, 20), sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Cancel button
        self.cancel_button = ctk.CTkButton(
            self.button_frame,
            text="Cancel",
            font=("Roboto", 14),
            fg_color="#E0E0E0",
            text_color=self.colors["primary"],
            hover_color="#BDBDBD",
            command=self.destroy
        )
        self.cancel_button.grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        
        # Save button
        self.save_button = ctk.CTkButton(
            self.button_frame,
            text="Save Item",
            font=("Roboto", 14),
            fg_color=self.colors["accent"],
            hover_color=self.colors["secondary"],
            command=self.save_item
        )
        self.save_button.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
    
    def save_item(self):
        """Save or update the menu item"""
        # Validate input
        if not self.name_var.get().strip():
            messagebox.showerror("Error", "Item name is required")
            return
        
        try:
            price = float(self.price_var.get())
            if price < 0:
                raise ValueError("Price must be positive")
        except ValueError:
            messagebox.showerror("Error", "Price must be a valid number")
            return
        
        try:
            stock = int(self.stock_var.get())
            if stock < 0:
                raise ValueError("Stock must be positive")
        except ValueError:
            messagebox.showerror("Error", "Stock must be a valid integer")
            return
        
        # Prepare item data
        item_data = {
            'name': self.name_var.get().strip(),
            'category': self.category_var.get(),
            'price': float(self.price_var.get()),
            'description': self.desc_var.get().strip(),
            'shortcut': self.shortcut_var.get().strip(),
            'initial_stock': int(self.stock_var.get())
        }
        
        if self.item_data:  # Editing existing item
            success, message = self.data_manager.update_menu_item(self.item_data['id'], item_data)
        else:  # Adding new item
            success, message = self.data_manager.add_menu_item(item_data)
        
        if success:
            messagebox.showinfo("Success", message)
            self.destroy()
        else:
            messagebox.showerror("Error", message)
