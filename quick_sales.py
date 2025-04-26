import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from datetime import datetime, date
import time
import pandas as pd

class QuickSaleFrame(ctk.CTkFrame):
    def __init__(self, parent, data_manager, colors):
        super().__init__(parent, fg_color=colors["background"])
        self.data_manager = data_manager
        self.colors = colors
        self.parent = parent
        
        # Initialize cart
        self.cart = []
        
        # Configure grid
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Header
        self.header = ctk.CTkLabel(
            self, 
            text="Quick Sale", 
            font=("Roboto", 24, "bold"),
            text_color=self.colors["primary"]
        )
        self.header.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")
        
        # Menu items section (left side)
        self.menu_frame = ctk.CTkFrame(self, fg_color=self.colors["background"])
        self.menu_frame.grid(row=1, column=0, rowspan=2, padx=(20, 10), pady=10, sticky="nsew")
        self.menu_frame.grid_columnconfigure(0, weight=1)
        self.menu_frame.grid_rowconfigure(1, weight=1)
        
        # Menu items search
        self.search_frame = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        self.search_frame.grid(row=0, column=0, padx=10, pady=(0, 10), sticky="ew")
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
        
        # Category filter
        self.category_label = ctk.CTkLabel(
            self.search_frame, 
            text="Category:", 
            font=("Roboto", 12),
            text_color=self.colors["primary"]
        )
        self.category_label.grid(row=0, column=2, padx=(10, 5), pady=5, sticky="w")
        
        # We'll populate categories later
        self.category_var = tk.StringVar(value="All Categories")
        self.category_menu = ctk.CTkComboBox(
            self.search_frame,
            values=["All Categories"],
            variable=self.category_var,
            command=self.filter_menu_items,
            width=150
        )
        self.category_menu.grid(row=0, column=3, padx=5, pady=5)
        
        # Menu items display
        self.items_frame = ctk.CTkScrollableFrame(
            self.menu_frame, 
            fg_color=self.colors["background"]
        )
        self.items_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Shortcut info frame
        self.shortcut_frame = ctk.CTkFrame(
            self.menu_frame,
            fg_color="#E3F2FD",
            corner_radius=8
        )
        self.shortcut_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        self.shortcut_label = ctk.CTkLabel(
            self.shortcut_frame,
            text="Keyboard Shortcuts: Press the assigned key to add an item quickly",
            font=("Roboto", 12, "bold"),
            text_color=self.colors["primary"]
        )
        self.shortcut_label.grid(row=0, column=0, padx=10, pady=10)
        
        # Cart section (right side)
        self.cart_frame = ctk.CTkFrame(self, fg_color=self.colors["background"])
        self.cart_frame.grid(row=1, column=1, rowspan=2, padx=(10, 20), pady=10, sticky="nsew")
        self.cart_frame.grid_columnconfigure(0, weight=1)
        self.cart_frame.grid_rowconfigure(1, weight=1)
        
        # Cart header
        self.cart_header = ctk.CTkLabel(
            self.cart_frame, 
            text="Current Cart", 
            font=("Roboto", 18, "bold"),
            text_color=self.colors["primary"]
        )
        self.cart_header.grid(row=0, column=0, padx=10, pady=(0, 10), sticky="w")
        
        # Cart items display
        self.cart_items_frame = ctk.CTkScrollableFrame(
            self.cart_frame, 
            fg_color=self.colors["background"]
        )
        self.cart_items_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.cart_items_frame.grid_columnconfigure(0, weight=1)
        
        # Cart total and actions
        self.cart_actions_frame = ctk.CTkFrame(
            self.cart_frame,
            fg_color="#E3F2FD",
            corner_radius=8
        )
        self.cart_actions_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.cart_actions_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Total amount
        self.total_amount = 0.0
        self.total_label = ctk.CTkLabel(
            self.cart_actions_frame,
            text="Total: ₹0.00",
            font=("Roboto", 18, "bold"),
            text_color=self.colors["primary"]
        )
        self.total_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Action buttons
        self.actions_frame = ctk.CTkFrame(
            self.cart_actions_frame,
            fg_color="transparent"
        )
        self.actions_frame.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        
        # Clear cart button
        self.clear_button = ctk.CTkButton(
            self.actions_frame,
            text="Clear Cart",
            font=("Roboto", 12),
            fg_color="#E57373",
            hover_color="#C62828",
            command=self.clear_cart
        )
        self.clear_button.grid(row=0, column=0, padx=5, pady=10)
        
        # Complete sale button
        self.complete_button = ctk.CTkButton(
            self.actions_frame,
            text="Complete Sale",
            font=("Roboto", 12),
            fg_color=self.colors["accent"],
            hover_color=self.colors["secondary"],
            command=self.complete_sale
        )
        self.complete_button.grid(row=0, column=1, padx=5, pady=10)
        
        # Initialize menu items display
        self.menu_items = []
        self.shortcut_map = {}
        self.menu_buttons = []
        
        # Load menu items and categories
        self.refresh_data()
        
    def refresh_data(self):
        """Refresh menu items data and update display"""
        # Clear existing items
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        
        self.menu_buttons = []
        
        # Get updated menu items
        self.menu_items = self.data_manager.get_menu_items()
        
        # Map shortcuts
        self.shortcut_map = {}
        for item in self.menu_items:
            shortcut = item.get('shortcut')
            if shortcut:
                self.shortcut_map[shortcut.lower()] = item
        
        # Get categories
        categories = set()
        for item in self.menu_items:
            category = item.get('category', 'Uncategorized')
            categories.add(category)
        
        category_list = ["All Categories"] + sorted(list(categories))
        self.category_menu.configure(values=category_list)
        
        # Bind shortcuts
        self.bind_shortcuts()
        
        # Display menu items
        self.display_menu_items(self.menu_items)
        
        # Update cart display
        self.update_cart_display()
    
    def bind_shortcuts(self):
        """Bind keyboard shortcuts for quick item addition"""
        # Unbind any existing shortcuts
        for key in self.shortcut_map.keys():
            if len(key) == 1:  # Only bind single character shortcuts
                self.unbind(f"<{key}>", None)
                self.unbind(f"<{key.upper()}>", None)
        
        # Bind new shortcuts
        for key, item in self.shortcut_map.items():
            if len(key) == 1:  # Only bind single character shortcuts
                self.bind(f"<{key}>", lambda event, i=item: self.add_to_cart(i))
                self.bind(f"<{key.upper()}>", lambda event, i=item: self.add_to_cart(i))
    
    def filter_menu_items(self, *args):
        """Filter menu items based on search text and category"""
        search_text = self.search_var.get().lower()
        selected_category = self.category_var.get()
        
        filtered_items = []
        for item in self.menu_items:
            # Category filter
            if selected_category != "All Categories" and item.get('category', 'Uncategorized') != selected_category:
                continue
                
            # Text search
            if search_text and not (
                search_text in item.get('name', '').lower() or 
                search_text in item.get('category', '').lower() or
                search_text in str(item.get('price', '')).lower()
            ):
                continue
                
            filtered_items.append(item)
        
        self.display_menu_items(filtered_items)
    
    def display_menu_items(self, items_to_display):
        """Display menu items in a grid layout with buttons"""
        # Clear existing items
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        
        # No items message
        if not items_to_display:
            no_items_label = ctk.CTkLabel(
                self.items_frame, 
                text="No menu items found.",
                font=("Roboto", 14),
                text_color=self.colors["primary"]
            )
            no_items_label.grid(row=0, column=0, padx=20, pady=20)
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
                self.items_frame,
                text=category,
                font=("Roboto", 16, "bold"),
                text_color=self.colors["secondary"]
            )
            category_label.grid(row=row_counter, column=0, columnspan=3, padx=10, pady=(15, 5), sticky="w")
            row_counter += 1
            
            # Items grid (3 buttons per row)
            col_counter = 0
            for item in category_items:
                button = self.create_menu_button(item)
                button.grid(row=row_counter, column=col_counter, padx=5, pady=5, sticky="nsew")
                self.menu_buttons.append(button)
                
                col_counter += 1
                if col_counter >= 3:  # Start a new row after 3 items
                    col_counter = 0
                    row_counter += 1
            
            # Move to next row if we didn't fill the last row
            if col_counter != 0:
                row_counter += 1
    
    def create_menu_button(self, item):
        """Create a button for a menu item"""
        # Get inventory status
        inventory = self.data_manager.get_inventory()
        stock_quantity = 0
        for inv_item in inventory:
            if inv_item.get('name') == item.get('name'):
                stock_quantity = inv_item.get('quantity', 0)
                break
        
        # Status indicator
        stock_color = "#00B894" if stock_quantity > 5 else "#FF9800" if stock_quantity > 0 else "#FF5252"
        
        # Format button text
        button_text = f"{item.get('name', 'Unnamed')}\n₹{item.get('price', '0.00')}"
        shortcut = item.get('shortcut', '')
        if shortcut:
            button_text += f"\n[{shortcut}]"
        
        # Create button
        button = ctk.CTkButton(
            self.items_frame,
            text=button_text,
            font=("Roboto", 12),
            fg_color=self.colors["primary"] if stock_quantity > 0 else "#777777",
            hover_color=self.colors["secondary"] if stock_quantity > 0 else "#555555",
            height=80,
            width=150,
            command=lambda i=item: self.add_to_cart(i) if stock_quantity > 0 else self.show_out_of_stock()
        )
        
        # Add a border to indicate stock status
        button.configure(border_width=2, border_color=stock_color)
        
        return button
    
    def show_out_of_stock(self):
        """Show out of stock message"""
        messagebox.showinfo("Out of Stock", "This item is currently out of stock.")
    
    def add_to_cart(self, item):
        """Add an item to the cart"""
        # Check if item is already in cart
        for cart_item in self.cart:
            if cart_item['id'] == item['id']:
                # Increment quantity
                cart_item['quantity'] += 1
                self.update_cart_display()
                return
        
        # Add new item to cart
        cart_item = {
            'id': item.get('id'),
            'name': item.get('name'),
            'price': item.get('price', 0),
            'quantity': 1
        }
        self.cart.append(cart_item)
        
        # Update display
        self.update_cart_display()
    
    def update_cart_display(self):
        """Update the cart display"""
        # Clear existing cart items
        for widget in self.cart_items_frame.winfo_children():
            widget.destroy()
        
        # No items message
        if not self.cart:
            no_items_label = ctk.CTkLabel(
                self.cart_items_frame, 
                text="Your cart is empty. Add items to get started.",
                font=("Roboto", 14),
                text_color=self.colors["primary"]
            )
            no_items_label.grid(row=0, column=0, padx=20, pady=20)
            
            # Update total
            self.total_amount = 0.0
            self.total_label.configure(text=f"Total: ₹{self.total_amount:.2f}")
            
            return
        
        # Cart headers
        headers_frame = ctk.CTkFrame(self.cart_items_frame, fg_color="transparent")
        headers_frame.grid(row=0, column=0, padx=10, pady=(0, 5), sticky="ew")
        headers_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        item_header = ctk.CTkLabel(
            headers_frame, text="Item", 
            font=("Roboto", 12, "bold"),
            text_color=self.colors["primary"]
        )
        item_header.grid(row=0, column=0, padx=5, sticky="w")
        
        price_header = ctk.CTkLabel(
            headers_frame, text="Price", 
            font=("Roboto", 12, "bold"),
            text_color=self.colors["primary"]
        )
        price_header.grid(row=0, column=1, padx=5, sticky="w")
        
        qty_header = ctk.CTkLabel(
            headers_frame, text="Qty", 
            font=("Roboto", 12, "bold"),
            text_color=self.colors["primary"]
        )
        qty_header.grid(row=0, column=2, padx=5, sticky="w")
        
        total_header = ctk.CTkLabel(
            headers_frame, text="Total", 
            font=("Roboto", 12, "bold"),
            text_color=self.colors["primary"]
        )
        total_header.grid(row=0, column=3, padx=5, sticky="w")
        
        # Display cart items
        self.total_amount = 0.0
        for i, item in enumerate(self.cart):
            item_frame = self.create_cart_item_frame(item, i)
            item_frame.grid(row=i+1, column=0, padx=10, pady=5, sticky="ew")
            
            # Add to total
            self.total_amount += item['price'] * item['quantity']
        
        # Update total display
        self.total_label.configure(text=f"Total: ₹{self.total_amount:.2f}")
    
    def create_cart_item_frame(self, item, index):
        """Create a frame for a cart item"""
        frame = ctk.CTkFrame(
            self.cart_items_frame,
            fg_color=self.colors["background"],
            border_width=1,
            border_color="#E0E0E0",
            corner_radius=8
        )
        frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        # Item name
        name_label = ctk.CTkLabel(
            frame,
            text=item.get('name', 'Unnamed'),
            font=("Roboto", 12),
            text_color=self.colors["primary"]
        )
        name_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Item price
        price_label = ctk.CTkLabel(
            frame,
            text=f"₹{item.get('price', 0):.2f}",
            font=("Roboto", 12),
            text_color=self.colors["primary"]
        )
        price_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Quantity control frame
        qty_frame = ctk.CTkFrame(frame, fg_color="transparent")
        qty_frame.grid(row=0, column=2, padx=5, pady=5)
        
        # Decrease quantity button
        decrease_button = ctk.CTkButton(
            qty_frame,
            text="-",
            font=("Roboto", 12, "bold"),
            fg_color=self.colors["primary"],
            hover_color=self.colors["secondary"],
            width=25,
            height=25,
            command=lambda: self.update_cart_item_quantity(index, -1)
        )
        decrease_button.grid(row=0, column=0, padx=(0, 5))
        
        # Quantity label
        qty_label = ctk.CTkLabel(
            qty_frame,
            text=str(item.get('quantity', 1)),
            font=("Roboto", 12),
            text_color=self.colors["primary"],
            width=30
        )
        qty_label.grid(row=0, column=1)
        
        # Increase quantity button
        increase_button = ctk.CTkButton(
            qty_frame,
            text="+",
            font=("Roboto", 12, "bold"),
            fg_color=self.colors["primary"],
            hover_color=self.colors["secondary"],
            width=25,
            height=25,
            command=lambda: self.update_cart_item_quantity(index, 1)
        )
        increase_button.grid(row=0, column=2, padx=(5, 0))
        
        # Item total
        total = item.get('price', 0) * item.get('quantity', 1)
        total_label = ctk.CTkLabel(
            frame,
            text=f"₹{total:.2f}",
            font=("Roboto", 12, "bold"),
            text_color=self.colors["primary"]
        )
        total_label.grid(row=0, column=3, padx=10, pady=10, sticky="w")
        
        # Remove button
        remove_button = ctk.CTkButton(
            frame,
            text="×",
            font=("Roboto", 14, "bold"),
            fg_color="#E57373",
            hover_color="#C62828",
            width=25,
            height=25,
            command=lambda: self.remove_cart_item(index)
        )
        remove_button.grid(row=0, column=4, padx=5, pady=5, sticky="e")
        
        return frame
    
    def update_cart_item_quantity(self, index, change):
        """Update the quantity of a cart item"""
        try:
            # Get current quantity
            current_qty = self.cart[index]['quantity']
            
            # Calculate new quantity
            new_qty = current_qty + change
            
            if new_qty <= 0:
                # Remove item if quantity goes to zero
                self.remove_cart_item(index)
            else:
                # Update quantity
                self.cart[index]['quantity'] = new_qty
                self.update_cart_display()
        except IndexError:
            # Handle invalid index
            pass
    
    def remove_cart_item(self, index):
        """Remove an item from the cart"""
        try:
            self.cart.pop(index)
            self.update_cart_display()
        except IndexError:
            # Handle invalid index
            pass
    
    def clear_cart(self):
        """Clear the cart"""
        if not self.cart:
            return
            
        confirm = messagebox.askyesno("Clear Cart", "Are you sure you want to clear the cart?")
        if confirm:
            self.cart = []
            self.update_cart_display()
    
    def complete_sale(self):
        """Complete the sale"""
        if not self.cart:
            messagebox.showinfo("Empty Cart", "Your cart is empty. Add items to complete a sale.")
            return
        
        # Format sale data
        sale_data = {
            'items': [],
            'total_amount': self.total_amount,
            'date': date.today().strftime('%Y-%m-%d')
        }
        
        # Add items
        for item in self.cart:
            sale_data['items'].append({
                'name': item['name'],
                'price': item['price'],
                'quantity': item['quantity']
            })
        
        # Add the sale
        success, message = self.data_manager.add_sale(sale_data)
        
        if success:
            messagebox.showinfo("Sale Complete", f"Sale completed successfully.\nTotal: ₹{self.total_amount:.2f}")
            self.cart = []
            self.update_cart_display()
        else:
            messagebox.showerror("Error", f"Failed to complete sale: {message}")