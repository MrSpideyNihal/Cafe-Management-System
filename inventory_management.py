import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
import json
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class InventoryManagementFrame(ctk.CTkFrame):
    def __init__(self, parent, data_manager, colors):
        super().__init__(parent, fg_color=colors["background"])
        self.data_manager = data_manager
        self.colors = colors
        self.parent = parent
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)  # Inventory list takes most space
        
        # Header
        self.header = ctk.CTkLabel(
            self, 
            text="Inventory Management", 
            font=("Roboto", 24, "bold"),
            text_color=self.colors["primary"]
        )
        self.header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Buttons frame
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Add inventory button
        self.add_button = ctk.CTkButton(
            self.button_frame,
            text="Add Stock (Ctrl+N)",
            font=("Roboto", 12),
            fg_color=self.colors["accent"],
            hover_color=self.colors["secondary"],
            command=self.add_inventory
        )
        self.add_button.grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        
        # Adjust inventory button
        self.adjust_button = ctk.CTkButton(
            self.button_frame,
            text="Adjust Selected",
            font=("Roboto", 12),
            fg_color=self.colors["secondary"],
            hover_color="#0771c0",
            command=self.adjust_selected_inventory
        )
        self.adjust_button.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        # Low stock alert button
        self.alert_button = ctk.CTkButton(
            self.button_frame,
            text="Low Stock Alert",
            font=("Roboto", 12),
            fg_color="#E57373",
            hover_color="#C62828",
            command=self.show_low_stock_alert
        )
        self.alert_button.grid(row=0, column=2, padx=5, pady=10, sticky="ew")
        
        # Export button
        self.export_button = ctk.CTkButton(
            self.button_frame,
            text="Export Inventory (Ctrl+E)",
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
        self.search_var.trace("w", self.filter_inventory_items)
        self.search_entry = ctk.CTkEntry(
            self.search_frame, 
            font=("Roboto", 12),
            textvariable=self.search_var,
            placeholder_text="Search inventory items..."
        )
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Main content frame with tabs
        self.content_frame = ctk.CTkTabview(
            self,
            fg_color=self.colors["background"],
            segmented_button_fg_color=self.colors["primary"],
            segmented_button_selected_color=self.colors["secondary"],
            segmented_button_selected_hover_color="#0771c0",
            segmented_button_unselected_hover_color="#424c4e",
            segmented_button_unselected_color=self.colors["primary"]
        )
        self.content_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        
        # Add tabs
        self.content_frame.add("Current Inventory")
        self.content_frame.add("Inventory Analytics")
        
        # Configure tab content
        self.setup_inventory_tab()
        self.setup_analytics_tab()
        
        # Initialize inventory items display
        self.inventory_items = []
        self.inventory_item_frames = []
        self.selected_item = None
        
        # Load inventory items
        self.refresh_data()
    
    def refresh_data(self):
        """Refresh inventory data and update display"""
        # Get updated inventory items
        self.inventory_items = self.data_manager.get_inventory()
        
        # Display inventory items
        self.display_inventory_items(self.inventory_items)
        
        # Update analytics
        self.update_analytics()
    
    def setup_inventory_tab(self):
        """Set up the current inventory tab UI"""
        tab = self.content_frame.tab("Current Inventory")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Inventory items scrollable frame
        self.inventory_items_frame = ctk.CTkScrollableFrame(
            tab,
            fg_color=self.colors["background"]
        )
        self.inventory_items_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.inventory_items_frame.grid_columnconfigure(0, weight=1)
    
    def setup_analytics_tab(self):
        """Set up the inventory analytics tab UI"""
        tab = self.content_frame.tab("Inventory Analytics")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        # Analytics options frame
        self.analytics_options_frame = ctk.CTkFrame(
            tab,
            fg_color="transparent"
        )
        self.analytics_options_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Analytics type selector
        self.analytics_type_label = ctk.CTkLabel(
            self.analytics_options_frame,
            text="View:",
            font=("Roboto", 14),
            text_color=self.colors["primary"]
        )
        self.analytics_type_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.analytics_type_var = tk.StringVar(value="Stock Levels")
        self.analytics_type_menu = ctk.CTkComboBox(
            self.analytics_options_frame,
            values=["Stock Levels", "Low Stock Items", "Stock Value"],
            variable=self.analytics_type_var,
            command=self.update_analytics
        )
        self.analytics_type_menu.grid(row=0, column=1, padx=5, pady=5)
        
        # Chart frame
        self.chart_frame = ctk.CTkFrame(
            tab,
            fg_color=self.colors["background"]
        )
        self.chart_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Create a placeholder for the chart
        self.figure = plt.Figure(figsize=(6, 4), dpi=100, facecolor=self.colors["background"])
        self.canvas = FigureCanvasTkAgg(self.figure, self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Summary frame
        self.summary_frame = ctk.CTkFrame(
            tab,
            fg_color="#E3F2FD",
            corner_radius=8
        )
        self.summary_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.summary_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Total items
        self.total_items_label = ctk.CTkLabel(
            self.summary_frame,
            text="Total Items: 0",
            font=("Roboto", 14, "bold"),
            text_color=self.colors["primary"]
        )
        self.total_items_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Low stock items
        self.low_stock_label = ctk.CTkLabel(
            self.summary_frame,
            text="Low Stock Items: 0",
            font=("Roboto", 14, "bold"),
            text_color="#E57373"
        )
        self.low_stock_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Total inventory value
        self.inventory_value_label = ctk.CTkLabel(
            self.summary_frame,
            text="Total Value: ₹0.00",
            font=("Roboto", 14, "bold"),
            text_color=self.colors["primary"]
        )
        self.inventory_value_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")
    
    def filter_inventory_items(self, *args):
        """Filter inventory items based on search text"""
        search_text = self.search_var.get().lower()
        
        if not search_text:
            # If search is empty, display all items
            self.display_inventory_items(self.inventory_items)
        else:
            # Filter items
            filtered_items = [
                item for item in self.inventory_items
                if search_text in item.get('name', '').lower()
            ]
            self.display_inventory_items(filtered_items)
    
    def display_inventory_items(self, items_to_display):
        """Display inventory items in the scrollable frame"""
        # Clear existing items
        for frame in self.inventory_item_frames:
            frame.destroy()
        
        self.inventory_item_frames = []
        
        # No items message
        if not items_to_display:
            no_items_label = ctk.CTkLabel(
                self.inventory_items_frame, 
                text="No inventory items found. Add stock items to get started.",
                font=("Roboto", 14),
                text_color=self.colors["primary"]
            )
            no_items_label.grid(row=0, column=0, padx=20, pady=20)
            self.inventory_item_frames.append(no_items_label)
            return
        
        # Sort items by name
        sorted_items = sorted(items_to_display, key=lambda x: x.get('name', ''))
        
        # Create headers (column titles)
        headers_frame = ctk.CTkFrame(self.inventory_items_frame, fg_color="transparent")
        headers_frame.grid(row=0, column=0, padx=10, pady=(0, 5), sticky="ew")
        headers_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        name_header = ctk.CTkLabel(
            headers_frame, text="Item Name", 
            font=("Roboto", 12, "bold"),
            text_color=self.colors["primary"]
        )
        name_header.grid(row=0, column=0, padx=5, sticky="w")
        
        quantity_header = ctk.CTkLabel(
            headers_frame, text="Quantity", 
            font=("Roboto", 12, "bold"),
            text_color=self.colors["primary"]
        )
        quantity_header.grid(row=0, column=1, padx=5, sticky="w")
        
        status_header = ctk.CTkLabel(
            headers_frame, text="Status", 
            font=("Roboto", 12, "bold"),
            text_color=self.colors["primary"]
        )
        status_header.grid(row=0, column=2, padx=5, sticky="w")
        
        updated_header = ctk.CTkLabel(
            headers_frame, text="Last Updated", 
            font=("Roboto", 12, "bold"),
            text_color=self.colors["primary"]
        )
        updated_header.grid(row=0, column=3, padx=5, sticky="w")
        
        self.inventory_item_frames.append(headers_frame)
        
        # Display inventory items
        for i, item in enumerate(sorted_items):
            item_frame = self.create_inventory_item_frame(item)
            item_frame.grid(row=i+1, column=0, padx=10, pady=5, sticky="ew")
            self.inventory_item_frames.append(item_frame)
    
    def create_inventory_item_frame(self, item):
        """Create a frame for a single inventory item"""
        frame = ctk.CTkFrame(
            self.inventory_items_frame,
            fg_color=self.colors["background"],
            border_width=1,
            border_color="#E0E0E0",
            corner_radius=8
        )
        frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Store item name in the frame for reference
        frame.item_name = item.get('name')
        
        # Item name
        name_label = ctk.CTkLabel(
            frame,
            text=item.get('name', 'Unnamed'),
            font=("Roboto", 14),
            text_color=self.colors["primary"]
        )
        name_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Quantity
        quantity = item.get('quantity', 0)
        quantity_label = ctk.CTkLabel(
            frame,
            text=str(quantity),
            font=("Roboto", 14),
            text_color=self.colors["primary"]
        )
        quantity_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Status
        status_color = "#00B894" if quantity > 5 else "#FF9800" if quantity > 0 else "#FF5252"
        status_text = "In Stock" if quantity > 5 else "Low Stock" if quantity > 0 else "Out of Stock"
        
        status_label = ctk.CTkLabel(
            frame,
            text=status_text,
            font=("Roboto", 14),
            text_color=status_color
        )
        status_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        
        # Last updated
        last_updated = item.get('last_updated', 'Never')
        updated_label = ctk.CTkLabel(
            frame,
            text=last_updated,
            font=("Roboto", 14),
            text_color=self.colors["primary"]
        )
        updated_label.grid(row=0, column=3, padx=10, pady=10, sticky="w")
        
        # Add selection behavior
        frame.bind("<Button-1>", lambda event, f=frame: self.select_item(f))
        name_label.bind("<Button-1>", lambda event, f=frame: self.select_item(f))
        quantity_label.bind("<Button-1>", lambda event, f=frame: self.select_item(f))
        status_label.bind("<Button-1>", lambda event, f=frame: self.select_item(f))
        updated_label.bind("<Button-1>", lambda event, f=frame: self.select_item(f))
        
        # Double-click to edit
        frame.bind("<Double-1>", lambda event, f=frame: self.adjust_inventory(f.item_name))
        name_label.bind("<Double-1>", lambda event, f=frame: self.adjust_inventory(f.item_name))
        quantity_label.bind("<Double-1>", lambda event, f=frame: self.adjust_inventory(f.item_name))
        status_label.bind("<Double-1>", lambda event, f=frame: self.adjust_inventory(f.item_name))
        updated_label.bind("<Double-1>", lambda event, f=frame: self.adjust_inventory(f.item_name))
        
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
    
    def add_inventory(self):
        """Open dialog to add new inventory"""
        self.inventory_dialog = InventoryDialog(self, self.colors, self.data_manager)
        self.wait_window(self.inventory_dialog)
        self.refresh_data()
    
    def adjust_selected_inventory(self):
        """Adjust the selected inventory item"""
        if not self.selected_item:
            messagebox.showinfo("Select Item", "Please select an item to adjust")
            return
        
        self.adjust_inventory(self.selected_item.item_name)
    
    def adjust_inventory(self, item_name):
        """Open dialog to adjust inventory for an item"""
        # Find the item data
        item_data = None
        for item in self.inventory_items:
            if item.get('name') == item_name:
                item_data = item
                break
        
        if not item_data:
            messagebox.showerror("Error", "Item not found in inventory")
            return
        
        self.inventory_dialog = InventoryDialog(self, self.colors, self.data_manager, item_data)
        self.wait_window(self.inventory_dialog)
        self.refresh_data()
    
    def show_low_stock_alert(self):
        """Show a dialog with low stock items"""
        # Get low stock items (quantity <= 5)
        low_stock_items = [item for item in self.inventory_items if item.get('quantity', 0) <= 5]
        
        if not low_stock_items:
            messagebox.showinfo("Low Stock Alert", "No items are currently low in stock.")
            return
        
        # Create alert dialog
        alert_dialog = LowStockAlertDialog(self, self.colors, low_stock_items, self.data_manager)
        self.wait_window(alert_dialog)
        self.refresh_data()
    
    def update_analytics(self, *args):
        """Update the analytics chart based on selected type"""
        analytics_type = self.analytics_type_var.get()
        
        # Clear previous chart
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Get menu items for price information
        menu_items = self.data_manager.get_menu_items()
        
        # Create a price lookup dictionary
        price_lookup = {item.get('name'): item.get('price', 0) for item in menu_items}
        
        if analytics_type == "Stock Levels":
            self.generate_stock_levels_chart(ax)
        elif analytics_type == "Low Stock Items":
            self.generate_low_stock_chart(ax)
        elif analytics_type == "Stock Value":
            self.generate_stock_value_chart(ax, price_lookup)
        
        # Update canvas
        self.canvas.draw()
        
        # Update summary statistics
        total_items = len(self.inventory_items)
        low_stock_count = sum(1 for item in self.inventory_items if item.get('quantity', 0) <= 5)
        
        # Calculate total inventory value
        total_value = 0
        for item in self.inventory_items:
            item_name = item.get('name')
            quantity = item.get('quantity', 0)
            price = price_lookup.get(item_name, 0)
            total_value += quantity * price
        
        self.total_items_label.configure(text=f"Total Items: {total_items}")
        self.low_stock_label.configure(text=f"Low Stock Items: {low_stock_count}")
        self.inventory_value_label.configure(text=f"Total Value: ₹{total_value:.2f}")
    
    def generate_stock_levels_chart(self, ax):
        """Generate chart showing stock levels for all items"""
        if not self.inventory_items:
            ax.text(0.5, 0.5, "No inventory data available", 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=12, color=self.colors["primary"])
            return
        
        # Sort items by quantity (descending)
        sorted_items = sorted(self.inventory_items, key=lambda x: x.get('quantity', 0), reverse=True)
        
        # Take top 15 items for better readability
        display_items = sorted_items[:15]
        
        # Extract names and quantities
        item_names = [item.get('name', 'Unnamed')[:15] + '...' if len(item.get('name', 'Unnamed')) > 15 
                      else item.get('name', 'Unnamed') for item in display_items]
        quantities = [item.get('quantity', 0) for item in display_items]
        
        # Define colors based on quantity
        colors = ['#00B894' if q > 5 else '#FF9800' if q > 0 else '#FF5252' for q in quantities]
        
        # Create horizontal bar chart
        bars = ax.barh(item_names, quantities, color=colors)
        
        # Add data labels
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                   f'{width:.0f}', ha='left', va='center')
        
        # Set chart title and labels
        ax.set_title('Current Stock Levels', color=self.colors["primary"])
        ax.set_xlabel('Quantity', color=self.colors["primary"])
        
        # Style the chart
        ax.set_facecolor(self.colors["background"])
        self.figure.set_facecolor(self.colors["background"])
        
        # Set x axis to start at 0
        ax.set_xlim(left=0)
        
        # Add grid lines
        ax.grid(axis='x', linestyle='--', alpha=0.7)
    
    def generate_low_stock_chart(self, ax):
        """Generate chart showing only low stock items"""
        # Filter for low stock items (quantity <= 5)
        low_stock_items = [item for item in self.inventory_items if item.get('quantity', 0) <= 5]
        
        if not low_stock_items:
            ax.text(0.5, 0.5, "No low stock items", 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=12, color=self.colors["primary"])
            return
        
        # Sort by quantity (ascending)
        sorted_items = sorted(low_stock_items, key=lambda x: x.get('quantity', 0))
        
        # Extract names and quantities
        item_names = [item.get('name', 'Unnamed')[:15] + '...' if len(item.get('name', 'Unnamed')) > 15 
                      else item.get('name', 'Unnamed') for item in sorted_items]
        quantities = [item.get('quantity', 0) for item in sorted_items]
        
        # Define colors based on quantity
        colors = ['#FF9800' if q > 0 else '#FF5252' for q in quantities]
        
        # Create horizontal bar chart
        bars = ax.barh(item_names, quantities, color=colors)
        
        # Add data labels
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                   f'{width:.0f}', ha='left', va='center')
        
        # Set chart title and labels
        ax.set_title('Low Stock Items (Quantity ≤ 5)', color=self.colors["primary"])
        ax.set_xlabel('Quantity', color=self.colors["primary"])
        
        # Style the chart
        ax.set_facecolor(self.colors["background"])
        self.figure.set_facecolor(self.colors["background"])
        
        # Set x axis to start at 0
        ax.set_xlim(left=0)
        
        # Add grid lines
        ax.grid(axis='x', linestyle='--', alpha=0.7)
        
        # Set a maximum x-limit for better visibility
        ax.set_xlim(right=6)
    
    def generate_stock_value_chart(self, ax, price_lookup):
        """Generate chart showing inventory value by item"""
        if not self.inventory_items:
            ax.text(0.5, 0.5, "No inventory data available", 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=12, color=self.colors["primary"])
            return
        
        # Calculate value for each item
        item_values = []
        for item in self.inventory_items:
            item_name = item.get('name')
            quantity = item.get('quantity', 0)
            price = price_lookup.get(item_name, 0)
            value = quantity * price
            
            if value > 0:  # Only include items with value > 0
                item_values.append((item_name, value))
        
        if not item_values:
            ax.text(0.5, 0.5, "No items with value found", 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=12, color=self.colors["primary"])
            return
        
        # Sort by value (descending)
        sorted_values = sorted(item_values, key=lambda x: x[1], reverse=True)
        
        # Take top 10 items for readability
        display_items = sorted_values[:10]
        
        # Extract names and values
        item_names = [name[:15] + '...' if len(name) > 15 else name for name, _ in display_items]
        values = [value for _, value in display_items]
        
        # Create horizontal bar chart
        bars = ax.barh(item_names, values, color=self.colors["secondary"])
        
        # Add data labels
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 5, bar.get_y() + bar.get_height()/2,
                   f'₹{width:.0f}', ha='left', va='center')
        
        # Set chart title and labels
        ax.set_title('Inventory Value by Item', color=self.colors["primary"])
        ax.set_xlabel('Value (₹)', color=self.colors["primary"])
        
        # Style the chart
        ax.set_facecolor(self.colors["background"])
        self.figure.set_facecolor(self.colors["background"])
        
        # Set x axis to start at 0
        ax.set_xlim(left=0)
        
        # Add grid lines
        ax.grid(axis='x', linestyle='--', alpha=0.7)
    
    def export_data(self):
        """Export inventory data to Excel"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Export Inventory to Excel"
        )
        
        if not filepath:
            return  # User cancelled
        
        success, message = self.data_manager.export_inventory_to_excel(filepath)
        
        if success:
            messagebox.showinfo("Export Successful", message)
        else:
            messagebox.showerror("Export Failed", message)


class InventoryDialog(ctk.CTkToplevel):
    def __init__(self, parent, colors, data_manager, item_data=None):
        super().__init__(parent)
        
        self.colors = colors
        self.data_manager = data_manager
        self.parent = parent
        self.item_data = item_data  # None for new item, dict for adjusting
        
        # Configure window
        self.title("Add Inventory Item" if not item_data else "Adjust Inventory")
        self.geometry("450x400")
        self.resizable(False, False)
        
        # Make it modal
        self.transient(parent)
        self.grab_set()
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        self.header = ctk.CTkLabel(
            self, 
            text="Add New Inventory Item" if not item_data else f"Adjust Stock for {item_data.get('name', 'Item')}",
            font=("Roboto", 18, "bold"),
            text_color=self.colors["primary"]
        )
        self.header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Form container
        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.form_frame.grid_columnconfigure(1, weight=1)
        
        # If adding new item
        if not item_data:
            # Item name
            self.name_label = ctk.CTkLabel(
                self.form_frame,
                text="Item Name:",
                font=("Roboto", 14),
                text_color=self.colors["primary"]
            )
            self.name_label.grid(row=0, column=0, padx=5, pady=10, sticky="w")
            
            # Get menu items for dropdown
            menu_items = self.data_manager.get_menu_items()
            menu_item_names = [item.get('name') for item in menu_items]
            
            if not menu_item_names:
                menu_item_names = ["No menu items available"]
            
            self.name_var = tk.StringVar(value=menu_item_names[0] if menu_item_names else "")
            self.name_combobox = ctk.CTkComboBox(
                self.form_frame,
                font=("Roboto", 14),
                values=menu_item_names,
                variable=self.name_var,
                state="readonly" if menu_item_names and menu_item_names[0] != "No menu items available" else "disabled"
            )
            self.name_combobox.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
            
            # Create new item option
            self.new_item_var = tk.IntVar(value=0)
            self.new_item_check = ctk.CTkCheckBox(
                self.form_frame,
                text="Item not in menu",
                font=("Roboto", 12),
                checkbox_width=20,
                checkbox_height=20,
                command=self.toggle_new_item_entry,
                variable=self.new_item_var
            )
            self.new_item_check.grid(row=1, column=0, columnspan=2, padx=5, pady=(0, 10), sticky="w")
            
            # New item name entry (hidden by default)
            self.new_name_var = tk.StringVar()
            self.new_name_entry = ctk.CTkEntry(
                self.form_frame,
                font=("Roboto", 14),
                textvariable=self.new_name_var,
                placeholder_text="Enter new item name"
            )
            
            # Initial quantity
            quantity_row = 2
        else:
            # Using existing item name
            self.name_var = tk.StringVar(value=item_data.get('name', ''))
            
            # Current quantity display
            self.current_label = ctk.CTkLabel(
                self.form_frame,
                text="Current Quantity:",
                font=("Roboto", 14),
                text_color=self.colors["primary"]
            )
            self.current_label.grid(row=0, column=0, padx=5, pady=10, sticky="w")
            
            self.current_display = ctk.CTkLabel(
                self.form_frame,
                text=str(item_data.get('quantity', 0)),
                font=("Roboto", 14, "bold"),
                text_color=self.colors["secondary"]
            )
            self.current_display.grid(row=0, column=1, padx=5, pady=10, sticky="w")
            
            quantity_row = 1
        
        # Quantity adjustment
        self.quantity_label = ctk.CTkLabel(
            self.form_frame,
            text="Quantity to Add:" if not item_data else "Adjust Quantity:",
            font=("Roboto", 14),
            text_color=self.colors["primary"]
        )
        self.quantity_label.grid(row=quantity_row, column=0, padx=5, pady=10, sticky="w")
        
        self.quantity_var = tk.StringVar(value="0")
        self.quantity_entry = ctk.CTkEntry(
            self.form_frame,
            font=("Roboto", 14),
            textvariable=self.quantity_var
        )
        self.quantity_entry.grid(row=quantity_row, column=1, padx=5, pady=10, sticky="ew")
        
        # If adjusting, add adjustment type
        if item_data:
            self.adjustment_type_label = ctk.CTkLabel(
                self.form_frame,
                text="Adjustment Type:",
                font=("Roboto", 14),
                text_color=self.colors["primary"]
            )
            self.adjustment_type_label.grid(row=quantity_row+1, column=0, padx=5, pady=10, sticky="w")
            
            self.adjustment_type_var = tk.StringVar(value="Add")
            self.add_radio = ctk.CTkRadioButton(
                self.form_frame,
                text="Add Stock",
                font=("Roboto", 12),
                variable=self.adjustment_type_var,
                value="Add",
                fg_color=self.colors["accent"]
            )
            self.add_radio.grid(row=quantity_row+1, column=1, padx=5, pady=(10, 0), sticky="w")
            
            self.remove_radio = ctk.CTkRadioButton(
                self.form_frame,
                text="Remove Stock",
                font=("Roboto", 12),
                variable=self.adjustment_type_var,
                value="Remove",
                fg_color=self.colors["accent"]
            )
            self.remove_radio.grid(row=quantity_row+2, column=1, padx=5, pady=(0, 10), sticky="w")
            
            # Notes for adjustment
            self.notes_label = ctk.CTkLabel(
                self.form_frame,
                text="Notes:",
                font=("Roboto", 14),
                text_color=self.colors["primary"]
            )
            self.notes_label.grid(row=quantity_row+3, column=0, padx=5, pady=10, sticky="w")
            
            self.notes_var = tk.StringVar()
            self.notes_entry = ctk.CTkEntry(
                self.form_frame,
                font=("Roboto", 14),
                textvariable=self.notes_var,
                placeholder_text="Optional adjustment notes"
            )
            self.notes_entry.grid(row=quantity_row+3, column=1, padx=5, pady=10, sticky="ew")
        
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
            text="Save" if not item_data else "Update Inventory",
            font=("Roboto", 14),
            fg_color=self.colors["accent"],
            hover_color=self.colors["secondary"],
            command=self.save_inventory
        )
        self.save_button.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
    
    def toggle_new_item_entry(self):
        """Toggle between dropdown and entry for new item"""
        if self.new_item_var.get() == 1:
            # Hide dropdown, show entry
            self.name_combobox.grid_forget()
            self.new_name_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        else:
            # Hide entry, show dropdown
            self.new_name_entry.grid_forget()
            self.name_combobox.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
    
    def save_inventory(self):
        """Save or update the inventory item"""
        # Validate input
        try:
            quantity = int(self.quantity_var.get())
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a valid integer")
            return
        
        # Get item name
        if self.item_data:
            # Adjusting existing item
            item_name = self.item_data.get('name')
            
            # Determine if adding or removing
            is_addition = self.adjustment_type_var.get() == "Add"
            
            # Update inventory
            success, message = self.data_manager.update_inventory(item_name, quantity, is_addition)
        else:
            # Adding new item or stock
            if self.new_item_var.get() == 1:
                # Using custom name
                item_name = self.new_name_var.get().strip()
                if not item_name:
                    messagebox.showerror("Error", "Item name is required")
                    return
            else:
                # Using dropdown selection
                item_name = self.name_var.get()
                if item_name == "No menu items available":
                    messagebox.showerror("Error", "Please add menu items first or create a new inventory item")
                    return
            
            # Update inventory (always an addition for new items)
            success, message = self.data_manager.update_inventory(item_name, quantity, True)
        
        if success:
            messagebox.showinfo("Success", message)
            self.destroy()
        else:
            messagebox.showerror("Error", message)


class LowStockAlertDialog(ctk.CTkToplevel):
    def __init__(self, parent, colors, low_stock_items, data_manager):
        super().__init__(parent)
        
        self.colors = colors
        self.data_manager = data_manager
        self.low_stock_items = low_stock_items
        
        # Configure window
        self.title("Low Stock Alert")
        self.geometry("500x400")
        self.resizable(True, True)
        
        # Make it modal
        self.transient(parent)
        self.grab_set()
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        self.header = ctk.CTkLabel(
            self, 
            text="Low Stock Items",
            font=("Roboto", 18, "bold"),
            text_color="#FF5252"
        )
        self.header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Items scrollable frame
        self.items_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=self.colors["background"]
        )
        self.items_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.items_frame.grid_columnconfigure(0, weight=1)
        
        # Display low stock items
        for i, item in enumerate(sorted(low_stock_items, key=lambda x: x.get('quantity', 0))):
            item_frame = self.create_low_stock_item_frame(item, i)
            item_frame.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
        
        # Buttons frame
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Close button
        self.close_button = ctk.CTkButton(
            self.button_frame,
            text="Close",
            font=("Roboto", 14),
            fg_color="#E0E0E0",
            text_color=self.colors["primary"],
            hover_color="#BDBDBD",
            command=self.destroy
        )
        self.close_button.grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        
        # Restock All button
        self.restock_button = ctk.CTkButton(
            self.button_frame,
            text="Restock Selected",
            font=("Roboto", 14),
            fg_color=self.colors["accent"],
            hover_color=self.colors["secondary"],
            command=self.restock_selected
        )
        self.restock_button.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        # Store selected items
        self.selected_items = {}
    
    def create_low_stock_item_frame(self, item, index):
        """Create a frame for a low stock item with a checkbox for selection"""
        frame = ctk.CTkFrame(
            self.items_frame,
            fg_color=self.colors["background"],
            border_width=1,
            border_color="#E0E0E0",
            corner_radius=8
        )
        frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Selection checkbox
        self.selected_items[item.get('name')] = tk.IntVar(value=0)
        select_checkbox = ctk.CTkCheckBox(
            frame,
            text="",
            font=("Roboto", 12),
            checkbox_width=20,
            checkbox_height=20,
            variable=self.selected_items[item.get('name')]
        )
        select_checkbox.grid(row=0, column=0, padx=5, pady=10)
        
        # Item name
        name_label = ctk.CTkLabel(
            frame,
            text=item.get('name', 'Unnamed'),
            font=("Roboto", 14),
            text_color=self.colors["primary"]
        )
        name_label.grid(row=0, column=1, padx=5, pady=10, sticky="w")
        
        # Quantity
        quantity = item.get('quantity', 0)
        quantity_color = "#FF9800" if quantity > 0 else "#FF5252"
        quantity_label = ctk.CTkLabel(
            frame,
            text=f"Qty: {quantity}",
            font=("Roboto", 14),
            text_color=quantity_color
        )
        quantity_label.grid(row=0, column=2, padx=5, pady=10, sticky="w")
        
        # Quick restock button
        restock_button = ctk.CTkButton(
            frame,
            text="Restock",
            font=("Roboto", 12),
            fg_color=self.colors["secondary"],
            hover_color="#0771c0",
            width=80,
            command=lambda item_name=item.get('name'): self.quick_restock(item_name)
        )
        restock_button.grid(row=0, column=3, padx=10, pady=10, sticky="e")
        
        return frame
    
    def quick_restock(self, item_name):
        """Quickly restock a single item"""
        # Open dialog to adjust inventory for this item
        # Find the item data
        item_data = None
        for item in self.low_stock_items:
            if item.get('name') == item_name:
                item_data = item
                break
        
        if item_data:
            inventory_dialog = InventoryDialog(self, self.colors, self.data_manager, item_data)
            self.wait_window(inventory_dialog)
    
    def restock_selected(self):
        """Open restock dialog for all selected items"""
        # Get selected items
        selected_names = [name for name, var in self.selected_items.items() if var.get() == 1]
        
        if not selected_names:
            messagebox.showinfo("Selection Required", "Please select at least one item to restock")
            return
        
        # Open bulk restock dialog
        bulk_dialog = BulkRestockDialog(self, self.colors, self.data_manager, selected_names)
        self.wait_window(bulk_dialog)


class BulkRestockDialog(ctk.CTkToplevel):
    def __init__(self, parent, colors, data_manager, item_names):
        super().__init__(parent)
        
        self.colors = colors
        self.data_manager = data_manager
        self.item_names = item_names
        
        # Configure window
        self.title("Bulk Restock")
        self.geometry("400x300")
        self.resizable(False, False)
        
        # Make it modal
        self.transient(parent)
        self.grab_set()
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        self.header = ctk.CTkLabel(
            self, 
            text=f"Restock {len(item_names)} Items",
            font=("Roboto", 18, "bold"),
            text_color=self.colors["primary"]
        )
        self.header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Item list
        items_text = ", ".join(item_names)
        if len(items_text) > 50:
            items_text = items_text[:47] + "..."
            
        self.items_label = ctk.CTkLabel(
            self,
            text=f"Items: {items_text}",
            font=("Roboto", 12),
            text_color=self.colors["primary"]
        )
        self.items_label.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")
        
        # Form container
        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.form_frame.grid_columnconfigure(1, weight=1)
        
        # Quantity to add
        self.quantity_label = ctk.CTkLabel(
            self.form_frame,
            text="Quantity to Add:",
            font=("Roboto", 14),
            text_color=self.colors["primary"]
        )
        self.quantity_label.grid(row=0, column=0, padx=5, pady=10, sticky="w")
        
        self.quantity_var = tk.StringVar(value="10")
        self.quantity_entry = ctk.CTkEntry(
            self.form_frame,
            font=("Roboto", 14),
            textvariable=self.quantity_var
        )
        self.quantity_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        # Notes
        self.notes_label = ctk.CTkLabel(
            self.form_frame,
            text="Notes:",
            font=("Roboto", 14),
            text_color=self.colors["primary"]
        )
        self.notes_label.grid(row=1, column=0, padx=5, pady=10, sticky="w")
        
        self.notes_var = tk.StringVar()
        self.notes_entry = ctk.CTkEntry(
            self.form_frame,
            font=("Roboto", 14),
            textvariable=self.notes_var,
            placeholder_text="Optional notes for this restock"
        )
        self.notes_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        
        # Buttons frame
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=3, column=0, padx=20, pady=(20, 20), sticky="ew")
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
        
        # Restock button
        self.restock_button = ctk.CTkButton(
            self.button_frame,
            text="Restock All",
            font=("Roboto", 14),
            fg_color=self.colors["accent"],
            hover_color=self.colors["secondary"],
            command=self.restock_all
        )
        self.restock_button.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
    
    def restock_all(self):
        """Restock all selected items with the same quantity"""
        try:
            quantity = int(self.quantity_var.get())
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive quantity")
            return
        
        # Update inventory for each item
        success_count = 0
        for item_name in self.item_names:
            success, _ = self.data_manager.update_inventory(item_name, quantity, True)
            if success:
                success_count += 1
        
        if success_count == len(self.item_names):
            messagebox.showinfo("Success", f"Successfully restocked all {success_count} items")
        else:
            messagebox.showinfo("Partial Success", 
                              f"Restocked {success_count} out of {len(self.item_names)} items")
        
        self.destroy()
