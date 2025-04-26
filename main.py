import os
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import time

from menu_management import MenuManagementFrame
from sales_tracking import SalesTrackingFrame
from inventory_management import InventoryManagementFrame
from quick_sales import QuickSaleFrame
from data_manager import DataManager
from utils import create_data_directory

# Set appearance mode and default color theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class CafeManagementSystem(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Create data directory if it doesn't exist
        create_data_directory()
        
        # Initialize data manager
        self.data_manager = DataManager()
        
        # Set up window
        self.title("Cafe Management System")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        
        # Define colors based on style guide
        self.colors = {
            "primary": "#2D3436",  # charcoal
            "secondary": "#0984E3",  # bright blue
            "accent": "#00B894",  # mint
            "background": "#F5F6FA",  # light grey
            "text": "#2D3436"  # dark grey
        }
        
        # Configure font
        self.default_font = ("Roboto", 12)
        self.header_font = ("Roboto", 16, "bold")
        
        # Configure the grid layout (2x1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create navigation frame
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=self.colors["primary"])
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(6, weight=1)
        
        # Add logo/title to navigation frame
        self.logo_label = ctk.CTkLabel(
            self.navigation_frame, 
            text="Cafe Management", 
            font=("Roboto", 20, "bold"),
            text_color="white"
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Create navigation buttons
        self.nav_button_menu = ctk.CTkButton(
            self.navigation_frame,
            corner_radius=0,
            height=40,
            border_spacing=10,
            text="Menu Management",
            fg_color="transparent",
            text_color="white",
            hover_color=self.colors["secondary"],
            anchor="w",
            command=self.show_menu_frame
        )
        self.nav_button_menu.grid(row=1, column=0, sticky="ew")
        
        self.nav_button_sales = ctk.CTkButton(
            self.navigation_frame,
            corner_radius=0,
            height=40,
            border_spacing=10,
            text="Sales Tracking",
            fg_color="transparent",
            text_color="white",
            hover_color=self.colors["secondary"],
            anchor="w",
            command=self.show_sales_frame
        )
        self.nav_button_sales.grid(row=2, column=0, sticky="ew")
        
        self.nav_button_inventory = ctk.CTkButton(
            self.navigation_frame,
            corner_radius=0,
            height=40,
            border_spacing=10,
            text="Inventory Management",
            fg_color="transparent",
            text_color="white",
            hover_color=self.colors["secondary"],
            anchor="w",
            command=self.show_inventory_frame
        )
        self.nav_button_inventory.grid(row=3, column=0, sticky="ew")
        
        # Add Quick Sale button with highlight
        self.nav_button_quick_sale = ctk.CTkButton(
            self.navigation_frame,
            corner_radius=0,
            height=50,  # Slightly taller
            border_spacing=10,
            text="⚡ Quick Sale (Ctrl+Q)",
            fg_color=self.colors["accent"],  # Use accent color
            text_color="white",
            hover_color=self.colors["secondary"],
            anchor="w",
            font=("Roboto", 13, "bold"),  # Bold font
            command=self.show_quick_sale_frame
        )
        self.nav_button_quick_sale.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        
        # Add keyboard shortcut info
        self.shortcut_label = ctk.CTkLabel(
            self.navigation_frame,
            text="Keyboard Shortcuts:",
            font=("Roboto", 12, "bold"),
            text_color="white"
        )
        self.shortcut_label.grid(row=5, column=0, padx=20, pady=(40, 5), sticky="w")
        
        self.shortcuts_text = """
        Ctrl+M: Menu Management
        Ctrl+S: Sales Tracking
        Ctrl+I: Inventory Management
        Ctrl+Q: Quick Sale
        Ctrl+N: Add New Item
        Ctrl+E: Export Data
        """
        self.shortcuts_info = ctk.CTkLabel(
            self.navigation_frame,
            text=self.shortcuts_text,
            font=("Roboto", 10),
            text_color="white",
            justify="left"
        )
        self.shortcuts_info.grid(row=6, column=0, padx=20, pady=5, sticky="w")
        
        # Create main content frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=self.colors["background"])
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Create different frames for each section
        self.menu_frame = MenuManagementFrame(self.main_frame, self.data_manager, self.colors)
        self.sales_frame = SalesTrackingFrame(self.main_frame, self.data_manager, self.colors)
        self.inventory_frame = InventoryManagementFrame(self.main_frame, self.data_manager, self.colors)
        self.quick_sale_frame = QuickSaleFrame(self.main_frame, self.data_manager, self.colors)
        
        # Start with menu frame visible
        self.show_menu_frame()
        
        # Bind keyboard shortcuts
        self.bind("<Control-m>", lambda event: self.show_menu_frame())
        self.bind("<Control-s>", lambda event: self.show_sales_frame())
        self.bind("<Control-i>", lambda event: self.show_inventory_frame())
        self.bind("<Control-q>", lambda event: self.show_quick_sale_frame())
        self.bind("<Control-n>", lambda event: self.current_frame.add_new_item())
        self.bind("<Control-e>", lambda event: self.current_frame.export_data())
        
        # Track current frame for keyboard shortcuts
        self.current_frame = self.menu_frame
        
    def show_menu_frame(self):
        self.sales_frame.grid_forget()
        self.inventory_frame.grid_forget()
        self.quick_sale_frame.grid_forget()
        self.menu_frame.grid(row=0, column=0, sticky="nsew")
        self.menu_frame.refresh_data()
        self.current_frame = self.menu_frame
        self.select_frame_by_name("menu")
        
    def show_sales_frame(self):
        self.menu_frame.grid_forget()
        self.inventory_frame.grid_forget()
        self.quick_sale_frame.grid_forget()
        self.sales_frame.grid(row=0, column=0, sticky="nsew")
        self.sales_frame.refresh_data()
        self.current_frame = self.sales_frame
        self.select_frame_by_name("sales")
        
    def show_inventory_frame(self):
        self.menu_frame.grid_forget()
        self.sales_frame.grid_forget()
        self.quick_sale_frame.grid_forget()
        self.inventory_frame.grid(row=0, column=0, sticky="nsew")
        self.inventory_frame.refresh_data()
        self.current_frame = self.inventory_frame
        self.select_frame_by_name("inventory")
        
    def show_quick_sale_frame(self):
        self.menu_frame.grid_forget()
        self.sales_frame.grid_forget()
        self.inventory_frame.grid_forget()
        self.quick_sale_frame.grid(row=0, column=0, sticky="nsew")
        self.quick_sale_frame.refresh_data()
        self.current_frame = self.quick_sale_frame
        self.select_frame_by_name("quick_sale")
        
    def select_frame_by_name(self, name):
        # Reset regular buttons
        self.nav_button_menu.configure(fg_color="transparent")
        self.nav_button_sales.configure(fg_color="transparent")
        self.nav_button_inventory.configure(fg_color="transparent")
        
        # Set active button color
        if name == "menu":
            self.nav_button_menu.configure(fg_color=self.colors["secondary"])
            # Make quick sale button return to accent color when not selected
            self.nav_button_quick_sale.configure(fg_color=self.colors["accent"])
        elif name == "sales":
            self.nav_button_sales.configure(fg_color=self.colors["secondary"])
            # Make quick sale button return to accent color when not selected
            self.nav_button_quick_sale.configure(fg_color=self.colors["accent"])
        elif name == "inventory":
            self.nav_button_inventory.configure(fg_color=self.colors["secondary"])
            # Make quick sale button return to accent color when not selected
            self.nav_button_quick_sale.configure(fg_color=self.colors["accent"])
        elif name == "quick_sale":
            # Highlight more strongly when active
            self.nav_button_quick_sale.configure(fg_color="#008c70")  # Darker shade of accent
    
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()

if __name__ == "__main__":
    app = CafeManagementSystem()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
