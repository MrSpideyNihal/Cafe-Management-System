import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
from datetime import datetime, date, timedelta
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import calendar
import os

class SalesTrackingFrame(ctk.CTkFrame):
    def __init__(self, parent, data_manager, colors):
        super().__init__(parent, fg_color=colors["background"])
        self.data_manager = data_manager
        self.colors = colors
        self.parent = parent
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)  # Sales items list takes most space
        
        # Header
        self.header = ctk.CTkLabel(
            self, 
            text="Sales Tracking", 
            font=("Roboto", 24, "bold"),
            text_color=self.colors["primary"]
        )
        self.header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Buttons frame
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # New sale button
        self.new_sale_button = ctk.CTkButton(
            self.button_frame,
            text="New Sale (Ctrl+N)",
            font=("Roboto", 12),
            fg_color=self.colors["accent"],
            hover_color=self.colors["secondary"],
            command=self.add_new_sale
        )
        self.new_sale_button.grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        
        # Today's report button
        self.today_report_button = ctk.CTkButton(
            self.button_frame,
            text="Today's Report",
            font=("Roboto", 12),
            fg_color=self.colors["secondary"],
            hover_color="#0771c0",
            command=lambda: self.show_daily_report(date.today().strftime('%Y-%m-%d'))
        )
        self.today_report_button.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        # Weekly report button
        self.weekly_report_button = ctk.CTkButton(
            self.button_frame,
            text="Weekly Report",
            font=("Roboto", 12),
            fg_color=self.colors["secondary"],
            hover_color="#0771c0",
            command=self.show_weekly_report
        )
        self.weekly_report_button.grid(row=0, column=2, padx=5, pady=10, sticky="ew")
        
        # Export button
        self.export_button = ctk.CTkButton(
            self.button_frame,
            text="Export Sales (Ctrl+E)",
            font=("Roboto", 12),
            fg_color=self.colors["primary"],
            hover_color="#1e2526",
            command=self.export_data
        )
        self.export_button.grid(row=0, column=3, padx=5, pady=10, sticky="ew")
        
        # Date selector frame
        self.date_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.date_frame.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # Date label
        self.date_label = ctk.CTkLabel(
            self.date_frame, 
            text="Select Date:", 
            font=("Roboto", 12),
            text_color=self.colors["primary"]
        )
        self.date_label.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="w")
        
        # Date picker
        today = date.today()
        self.day_var = tk.StringVar(value=str(today.day))
        self.month_var = tk.StringVar(value=str(today.month))
        self.year_var = tk.StringVar(value=str(today.year))
        
        # Create dropdown menus for date selection
        days = [str(d) for d in range(1, 32)]
        months = [str(m) for m in range(1, 13)]
        years = [str(y) for y in range(today.year - 5, today.year + 1)]
        
        self.day_menu = ctk.CTkComboBox(
            self.date_frame,
            values=days,
            variable=self.day_var,
            width=70
        )
        self.day_menu.grid(row=0, column=1, padx=5, pady=5)
        
        self.month_menu = ctk.CTkComboBox(
            self.date_frame,
            values=months,
            variable=self.month_var,
            width=70
        )
        self.month_menu.grid(row=0, column=2, padx=5, pady=5)
        
        self.year_menu = ctk.CTkComboBox(
            self.date_frame,
            values=years,
            variable=self.year_var,
            width=100
        )
        self.year_menu.grid(row=0, column=3, padx=5, pady=5)
        
        # View selected date button
        self.view_date_button = ctk.CTkButton(
            self.date_frame,
            text="View Selected Date",
            font=("Roboto", 12),
            fg_color=self.colors["secondary"],
            hover_color="#0771c0",
            command=self.show_selected_date_report
        )
        self.view_date_button.grid(row=0, column=4, padx=10, pady=5)
        
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
        self.content_frame.add("Daily Sales")
        self.content_frame.add("Sales History")
        self.content_frame.add("Reports")
        
        # Configure tab content
        self.setup_daily_sales_tab()
        self.setup_sales_history_tab()
        self.setup_reports_tab()
        
        # Load initial data
        self.refresh_data()
        
    def refresh_data(self):
        """Refresh sales data and update display"""
        # Update daily sales tab
        self.load_daily_sales()
        
        # Update sales history tab
        self.load_sales_history()
        
        # Update reports tab (will be refreshed when tab is selected)
        self.generate_reports()
    
    def setup_daily_sales_tab(self):
        """Set up the daily sales tab UI"""
        tab = self.content_frame.tab("Daily Sales")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        # Date display
        self.daily_date_label = ctk.CTkLabel(
            tab,
            text=f"Sales for {date.today().strftime('%Y-%m-%d')}",
            font=("Roboto", 16, "bold"),
            text_color=self.colors["primary"]
        )
        self.daily_date_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        # Daily sales scrollable frame
        self.daily_sales_frame = ctk.CTkScrollableFrame(
            tab,
            fg_color=self.colors["background"]
        )
        self.daily_sales_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.daily_sales_frame.grid_columnconfigure(0, weight=1)
        
        # Summary frame at bottom
        self.daily_summary_frame = ctk.CTkFrame(
            tab,
            fg_color="#E3F2FD",
            corner_radius=8
        )
        self.daily_summary_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.daily_summary_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Total sales label
        self.total_sales_label = ctk.CTkLabel(
            self.daily_summary_frame,
            text="Total Sales: ₹0.00",
            font=("Roboto", 14, "bold"),
            text_color=self.colors["primary"]
        )
        self.total_sales_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Total items label
        self.total_items_label = ctk.CTkLabel(
            self.daily_summary_frame,
            text="Total Items Sold: 0",
            font=("Roboto", 14, "bold"),
            text_color=self.colors["primary"]
        )
        self.total_items_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Total transactions label
        self.total_transactions_label = ctk.CTkLabel(
            self.daily_summary_frame,
            text="Total Transactions: 0",
            font=("Roboto", 14, "bold"),
            text_color=self.colors["primary"]
        )
        self.total_transactions_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")
    
    def setup_sales_history_tab(self):
        """Set up the sales history tab UI"""
        tab = self.content_frame.tab("Sales History")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Sales history scrollable frame
        self.sales_history_frame = ctk.CTkScrollableFrame(
            tab,
            fg_color=self.colors["background"]
        )
        self.sales_history_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.sales_history_frame.grid_columnconfigure(0, weight=1)
    
    def setup_reports_tab(self):
        """Set up the reports tab UI"""
        tab = self.content_frame.tab("Reports")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        # Reports options frame
        self.reports_options_frame = ctk.CTkFrame(
            tab,
            fg_color="transparent"
        )
        self.reports_options_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Report type selector
        self.report_type_label = ctk.CTkLabel(
            self.reports_options_frame,
            text="Report Type:",
            font=("Roboto", 14),
            text_color=self.colors["primary"]
        )
        self.report_type_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.report_type_var = tk.StringVar(value="Daily Sales")
        self.report_type_menu = ctk.CTkComboBox(
            self.reports_options_frame,
            values=["Daily Sales", "Weekly Sales", "Monthly Sales", "Item Performance"],
            variable=self.report_type_var,
            command=self.generate_reports
        )
        self.report_type_menu.grid(row=0, column=1, padx=5, pady=5)
        
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
    
    def load_daily_sales(self, target_date=None):
        """Load and display sales for a specific date"""
        if not target_date:
            target_date = date.today().strftime('%Y-%m-%d')
        
        # Update date label
        self.daily_date_label.configure(text=f"Sales for {target_date}")
        
        # Clear existing sales displays
        for widget in self.daily_sales_frame.winfo_children():
            widget.destroy()
        
        # Get sales data for the date
        sales = self.data_manager.get_sales(target_date)
        
        if not sales:
            no_sales_label = ctk.CTkLabel(
                self.daily_sales_frame,
                text=f"No sales recorded for {target_date}",
                font=("Roboto", 14),
                text_color=self.colors["primary"]
            )
            no_sales_label.grid(row=0, column=0, padx=10, pady=20)
            
            # Update summary
            self.total_sales_label.configure(text="Total Sales: ₹0.00")
            self.total_items_label.configure(text="Total Items Sold: 0")
            self.total_transactions_label.configure(text="Total Transactions: 0")
            
            return
        
        # Sort sales by timestamp (newest first)
        sales.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Display sales
        for i, sale in enumerate(sales):
            sale_frame = self.create_sale_display(sale, i)
            sale_frame.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
        
        # Calculate and display summary
        summary = self.data_manager.get_daily_sales_summary(target_date)
        self.total_sales_label.configure(text=f"Total Sales: ₹{summary['total_revenue']:.2f}")
        
        total_items = sum(summary['items_sold'].values())
        self.total_items_label.configure(text=f"Total Items Sold: {total_items}")
        
        self.total_transactions_label.configure(text=f"Total Transactions: {summary['total_transactions']}")
    
    def create_sale_display(self, sale, index):
        """Create a display frame for a single sale"""
        sale_frame = ctk.CTkFrame(
            self.daily_sales_frame,
            fg_color=self.colors["background"],
            border_width=1,
            border_color="#E0E0E0",
            corner_radius=8
        )
        sale_frame.grid_columnconfigure(0, weight=1)
        
        # Sale header
        header_frame = ctk.CTkFrame(
            sale_frame,
            fg_color="#E3F2FD",
            corner_radius=8
        )
        header_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        header_frame.grid_columnconfigure(2, weight=1)
        
        # Sale number and time
        sale_id = f"Sale #{sale.get('id', index + 1)}"
        time_str = sale.get('timestamp', 'Unknown time')
        
        sale_id_label = ctk.CTkLabel(
            header_frame,
            text=sale_id,
            font=("Roboto", 14, "bold"),
            text_color=self.colors["primary"]
        )
        sale_id_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        time_label = ctk.CTkLabel(
            header_frame,
            text=time_str,
            font=("Roboto", 12),
            text_color=self.colors["primary"]
        )
        time_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        total_label = ctk.CTkLabel(
            header_frame,
            text=f"Total: ₹{sale.get('total_amount', 0):.2f}",
            font=("Roboto", 14, "bold"),
            text_color=self.colors["accent"]
        )
        total_label.grid(row=0, column=2, padx=10, pady=5, sticky="e")
        
        # Items list
        items_frame = ctk.CTkFrame(
            sale_frame,
            fg_color="transparent"
        )
        items_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Column headers
        headers_frame = ctk.CTkFrame(
            items_frame,
            fg_color="transparent"
        )
        headers_frame.grid(row=0, column=0, padx=0, pady=(0, 5), sticky="ew")
        headers_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        item_header = ctk.CTkLabel(
            headers_frame,
            text="Item",
            font=("Roboto", 12, "bold"),
            text_color=self.colors["primary"]
        )
        item_header.grid(row=0, column=0, padx=5, sticky="w")
        
        qty_header = ctk.CTkLabel(
            headers_frame,
            text="Qty",
            font=("Roboto", 12, "bold"),
            text_color=self.colors["primary"]
        )
        qty_header.grid(row=0, column=1, padx=5, sticky="w")
        
        price_header = ctk.CTkLabel(
            headers_frame,
            text="Price",
            font=("Roboto", 12, "bold"),
            text_color=self.colors["primary"]
        )
        price_header.grid(row=0, column=2, padx=5, sticky="w")
        
        # Item rows
        for i, item in enumerate(sale.get('items', [])):
            item_name = item.get('name', 'Unknown item')
            item_qty = item.get('quantity', 1)
            item_price = item.get('price', 0) * item_qty
            
            item_row = ctk.CTkFrame(
                items_frame,
                fg_color="transparent"
            )
            item_row.grid(row=i+1, column=0, padx=0, pady=2, sticky="ew")
            item_row.grid_columnconfigure((0, 1, 2), weight=1)
            
            name_label = ctk.CTkLabel(
                item_row,
                text=item_name,
                font=("Roboto", 12),
                text_color=self.colors["primary"]
            )
            name_label.grid(row=0, column=0, padx=5, sticky="w")
            
            qty_label = ctk.CTkLabel(
                item_row,
                text=str(item_qty),
                font=("Roboto", 12),
                text_color=self.colors["primary"]
            )
            qty_label.grid(row=0, column=1, padx=5, sticky="w")
            
            price_label = ctk.CTkLabel(
                item_row,
                text=f"₹{item_price:.2f}",
                font=("Roboto", 12),
                text_color=self.colors["primary"]
            )
            price_label.grid(row=0, column=2, padx=5, sticky="w")
        
        return sale_frame
    
    def load_sales_history(self):
        """Load and display sales history"""
        # Clear existing history
        for widget in self.sales_history_frame.winfo_children():
            widget.destroy()
        
        # Get all sales data
        all_sales = self.data_manager.get_sales()
        
        if not all_sales:
            no_sales_label = ctk.CTkLabel(
                self.sales_history_frame,
                text="No sales history found",
                font=("Roboto", 14),
                text_color=self.colors["primary"]
            )
            no_sales_label.grid(row=0, column=0, padx=10, pady=20)
            return
        
        # Group sales by date
        sales_by_date = {}
        for sale in all_sales:
            sale_date = sale.get('date')
            if sale_date not in sales_by_date:
                sales_by_date[sale_date] = []
            sales_by_date[sale_date].append(sale)
        
        # Sort dates (newest first)
        sorted_dates = sorted(sales_by_date.keys(), reverse=True)
        
        # Display sales grouped by date
        row_counter = 0
        for date_str in sorted_dates:
            # Create date header
            date_frame = ctk.CTkFrame(
                self.sales_history_frame,
                fg_color=self.colors["secondary"],
                corner_radius=8
            )
            date_frame.grid(row=row_counter, column=0, padx=10, pady=(15, 5), sticky="ew")
            date_frame.grid_columnconfigure(0, weight=1)
            
            date_label = ctk.CTkLabel(
                date_frame,
                text=date_str,
                font=("Roboto", 16, "bold"),
                text_color="white"
            )
            date_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
            
            # Add a button to show full day report
            view_button = ctk.CTkButton(
                date_frame,
                text="View Full Day",
                font=("Roboto", 12),
                fg_color=self.colors["accent"],
                hover_color="#00a583",
                width=120,
                command=lambda d=date_str: self.show_daily_report(d)
            )
            view_button.grid(row=0, column=1, padx=10, pady=5, sticky="e")
            
            row_counter += 1
            
            # Create summary for this date
            daily_summary = self.data_manager.get_daily_sales_summary(date_str)
            
            summary_frame = ctk.CTkFrame(
                self.sales_history_frame,
                fg_color="#E3F2FD",
                corner_radius=8
            )
            summary_frame.grid(row=row_counter, column=0, padx=10, pady=5, sticky="ew")
            summary_frame.grid_columnconfigure((0, 1, 2), weight=1)
            
            # Revenue
            revenue_label = ctk.CTkLabel(
                summary_frame,
                text=f"Revenue: ₹{daily_summary['total_revenue']:.2f}",
                font=("Roboto", 14),
                text_color=self.colors["primary"]
            )
            revenue_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
            
            # Transactions
            trans_label = ctk.CTkLabel(
                summary_frame,
                text=f"Transactions: {daily_summary['total_transactions']}",
                font=("Roboto", 14),
                text_color=self.colors["primary"]
            )
            trans_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
            
            # Top item
            top_item = "None"
            top_qty = 0
            for item, qty in daily_summary['items_sold'].items():
                if qty > top_qty:
                    top_item = item
                    top_qty = qty
            
            top_item_label = ctk.CTkLabel(
                summary_frame,
                text=f"Top item: {top_item} ({top_qty})",
                font=("Roboto", 14),
                text_color=self.colors["primary"]
            )
            top_item_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")
            
            row_counter += 1
    
    def generate_reports(self, *args):
        """Generate and display reports based on selected type"""
        report_type = self.report_type_var.get()
        
        # Clear previous chart
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if report_type == "Daily Sales":
            self.generate_daily_sales_report(ax)
        elif report_type == "Weekly Sales":
            self.generate_weekly_sales_report(ax)
        elif report_type == "Monthly Sales":
            self.generate_monthly_sales_report(ax)
        elif report_type == "Item Performance":
            self.generate_item_performance_report(ax)
        
        # Update canvas
        self.canvas.draw()
    
    def generate_daily_sales_report(self, ax):
        """Generate report showing daily sales for the past week"""
        # Get last 7 days
        end_date = date.today()
        start_date = end_date - timedelta(days=6)
        
        # Generate date range
        date_range = []
        current_date = start_date
        while current_date <= end_date:
            date_range.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
        
        # Get sales for each day
        daily_sales = []
        for day in date_range:
            summary = self.data_manager.get_daily_sales_summary(day)
            daily_sales.append(summary['total_revenue'])
        
        # Shorter date format for x labels
        x_labels = [d.split('-')[2] + '/' + d.split('-')[1] for d in date_range]
        
        # Create bar chart
        bars = ax.bar(x_labels, daily_sales, color=self.colors["secondary"])
        
        # Add data labels on top of each bar
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 5,
                   f'₹{height:.0f}', ha='center', va='bottom')
        
        # Set chart title and labels
        ax.set_title('Daily Sales (Last 7 Days)', color=self.colors["primary"])
        ax.set_xlabel('Date', color=self.colors["primary"])
        ax.set_ylabel('Revenue (₹)', color=self.colors["primary"])
        
        # Style the chart
        ax.set_facecolor(self.colors["background"])
        self.figure.set_facecolor(self.colors["background"])
        
        # Set y axis to start at 0
        ax.set_ylim(bottom=0)
        
        # Add grid lines
        ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    def generate_weekly_sales_report(self, ax):
        """Generate report showing weekly sales for the past month"""
        # Get last 4 weeks
        end_date = date.today()
        start_date = end_date - timedelta(days=28)
        
        # Generate weekly ranges
        weeks = []
        weekly_sales = []
        
        for i in range(4):
            week_start = start_date + timedelta(days=i*7)
            week_end = week_start + timedelta(days=6)
            week_label = f"{week_start.strftime('%d/%m')}-{week_end.strftime('%d/%m')}"
            weeks.append(week_label)
            
            # Calculate total sales for the week
            week_total = 0
            current_day = week_start
            while current_day <= week_end and current_day <= end_date:
                summary = self.data_manager.get_daily_sales_summary(current_day.strftime('%Y-%m-%d'))
                week_total += summary['total_revenue']
                current_day += timedelta(days=1)
            
            weekly_sales.append(week_total)
        
        # Create bar chart
        bars = ax.bar(weeks, weekly_sales, color=self.colors["secondary"])
        
        # Add data labels on top of each bar
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 5,
                   f'₹{height:.0f}', ha='center', va='bottom')
        
        # Set chart title and labels
        ax.set_title('Weekly Sales (Last 4 Weeks)', color=self.colors["primary"])
        ax.set_xlabel('Week', color=self.colors["primary"])
        ax.set_ylabel('Revenue (₹)', color=self.colors["primary"])
        
        # Style the chart
        ax.set_facecolor(self.colors["background"])
        self.figure.set_facecolor(self.colors["background"])
        
        # Set y axis to start at 0
        ax.set_ylim(bottom=0)
        
        # Add grid lines
        ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    def generate_monthly_sales_report(self, ax):
        """Generate report showing monthly sales for the past 6 months"""
        # Get current month and past 5 months
        today = date.today()
        months = []
        monthly_sales = []
        
        for i in range(5, -1, -1):
            # Calculate month and year
            month = today.month - i
            year = today.year
            while month <= 0:
                month += 12
                year -= 1
            
            # Create month label
            month_name = calendar.month_name[month][:3]
            month_label = f"{month_name} {str(year)[2:]}"
            months.append(month_label)
            
            # Get all sales and filter by month and year
            all_sales = self.data_manager.get_sales()
            month_total = 0
            
            for sale in all_sales:
                sale_date = sale.get('date', '')
                if sale_date:
                    try:
                        sale_year = int(sale_date.split('-')[0])
                        sale_month = int(sale_date.split('-')[1])
                        
                        if sale_year == year and sale_month == month:
                            month_total += sale.get('total_amount', 0)
                    except (ValueError, IndexError):
                        continue
            
            monthly_sales.append(month_total)
        
        # Create bar chart
        bars = ax.bar(months, monthly_sales, color=self.colors["secondary"])
        
        # Add data labels on top of each bar
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 5,
                   f'₹{height:.0f}', ha='center', va='bottom')
        
        # Set chart title and labels
        ax.set_title('Monthly Sales (Last 6 Months)', color=self.colors["primary"])
        ax.set_xlabel('Month', color=self.colors["primary"])
        ax.set_ylabel('Revenue (₹)', color=self.colors["primary"])
        
        # Style the chart
        ax.set_facecolor(self.colors["background"])
        self.figure.set_facecolor(self.colors["background"])
        
        # Set y axis to start at 0
        ax.set_ylim(bottom=0)
        
        # Add grid lines
        ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    def generate_item_performance_report(self, ax):
        """Generate report showing top selling items"""
        # Get all sales
        all_sales = self.data_manager.get_sales()
        
        # Count items sold
        item_counts = {}
        for sale in all_sales:
            for item in sale.get('items', []):
                item_name = item.get('name')
                item_qty = item.get('quantity', 1)
                
                if item_name in item_counts:
                    item_counts[item_name] += item_qty
                else:
                    item_counts[item_name] = item_qty
        
        # Sort items by quantity sold (descending)
        sorted_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Take top 10 items or all if less than 10
        top_items = sorted_items[:10]
        
        # Extract names and counts
        item_names = [item[0] for item in top_items]
        item_quantities = [item[1] for item in top_items]
        
        # Create horizontal bar chart
        bars = ax.barh(item_names, item_quantities, color=self.colors["secondary"])
        
        # Add data labels next to each bar
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                   f'{width:.0f}', ha='left', va='center')
        
        # Set chart title and labels
        ax.set_title('Top Selling Items', color=self.colors["primary"])
        ax.set_xlabel('Quantity Sold', color=self.colors["primary"])
        
        # Style the chart
        ax.set_facecolor(self.colors["background"])
        self.figure.set_facecolor(self.colors["background"])
        
        # Set x axis to start at 0
        ax.set_xlim(left=0)
        
        # Add grid lines
        ax.grid(axis='x', linestyle='--', alpha=0.7)
    
    def add_new_sale(self):
        """Open dialog to add a new sale"""
        self.sale_dialog = SaleDialog(self, self.colors, self.data_manager)
        self.wait_window(self.sale_dialog)
        self.refresh_data()
    
    def show_daily_report(self, target_date):
        """Show the daily report for a specific date"""
        # Switch to Daily Sales tab
        self.content_frame.set("Daily Sales")
        
        # Load the data for that date
        self.load_daily_sales(target_date)
    
    def show_weekly_report(self):
        """Show weekly sales report"""
        # Switch to Reports tab
        self.content_frame.set("Reports")
        
        # Set report type to weekly
        self.report_type_var.set("Weekly Sales")
        
        # Generate the report
        self.generate_reports()
    
    def show_selected_date_report(self):
        """Show report for the date selected in the date picker"""
        try:
            # Get selected date
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            day = int(self.day_var.get())
            
            # Validate date
            selected_date = date(year, month, day)
            date_str = selected_date.strftime('%Y-%m-%d')
            
            # Show report for that date
            self.show_daily_report(date_str)
            
        except ValueError:
            messagebox.showerror("Invalid Date", "Please select a valid date")
    
    def export_data(self):
        """Export sales data to Excel"""
        # Ask if user wants to export all sales or just for a specific date
        options = ["All Sales", "Today's Sales", "Selected Date"]
        dialog = ExportOptionsDialog(self, "Export Options", "What sales data would you like to export?", options)
        self.wait_window(dialog)
        
        if not dialog.result:
            return  # User cancelled
        
        # Get file path for export
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Export Sales to Excel"
        )
        
        if not filepath:
            return  # User cancelled
        
        date_filter = None
        
        if dialog.result == "Today's Sales":
            date_filter = date.today().strftime('%Y-%m-%d')
        elif dialog.result == "Selected Date":
            try:
                year = int(self.year_var.get())
                month = int(self.month_var.get())
                day = int(self.day_var.get())
                date_filter = date(year, month, day).strftime('%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Invalid Date", "Please select a valid date")
                return
        
        success, message = self.data_manager.export_sales_to_excel(filepath, date_filter)
        
        if success:
            messagebox.showinfo("Export Successful", message)
        else:
            messagebox.showerror("Export Failed", message)


class SaleDialog(ctk.CTkToplevel):
    def __init__(self, parent, colors, data_manager):
        super().__init__(parent)
        
        self.colors = colors
        self.data_manager = data_manager
        self.parent = parent
        
        # Configure window
        self.title("New Sale")
        self.geometry("800x600")
        self.resizable(True, True)
        
        # Make it modal
        self.transient(parent)
        self.grab_set()
        
        # Configure grid
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        
        # Menu items frame (left side)
        self.menu_frame = ctk.CTkFrame(self, fg_color=self.colors["background"])
        self.menu_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.menu_frame.grid_columnconfigure(0, weight=1)
        self.menu_frame.grid_rowconfigure(1, weight=1)
        
        # Menu header
        self.menu_header = ctk.CTkLabel(
            self.menu_frame,
            text="Menu Items",
            font=("Roboto", 18, "bold"),
            text_color=self.colors["primary"]
        )
        self.menu_header.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Search frame
        self.search_frame = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        self.search_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
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
        
        # Menu items scrollable frame
        self.menu_items_frame = ctk.CTkScrollableFrame(
            self.menu_frame,
            fg_color=self.colors["background"]
        )
        self.menu_items_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.menu_items_frame.grid_columnconfigure(0, weight=1)
        
        # Cart frame (right side)
        self.cart_frame = ctk.CTkFrame(self, fg_color=self.colors["background"])
        self.cart_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.cart_frame.grid_columnconfigure(0, weight=1)
        self.cart_frame.grid_rowconfigure(1, weight=1)
        
        # Cart header
        self.cart_header = ctk.CTkLabel(
            self.cart_frame,
            text="Current Sale",
            font=("Roboto", 18, "bold"),
            text_color=self.colors["primary"]
        )
        self.cart_header.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Cart items scrollable frame
        self.cart_items_frame = ctk.CTkScrollableFrame(
            self.cart_frame,
            fg_color=self.colors["background"]
        )
        self.cart_items_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.cart_items_frame.grid_columnconfigure(0, weight=1)
        
        # Total and checkout frame
        self.checkout_frame = ctk.CTkFrame(
            self.cart_frame,
            fg_color="#E3F2FD",
            corner_radius=8
        )
        self.checkout_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.checkout_frame.grid_columnconfigure(0, weight=1)
        
        # Total amount
        self.total_var = tk.StringVar(value="₹0.00")
        self.total_label = ctk.CTkLabel(
            self.checkout_frame,
            text="Total:",
            font=("Roboto", 16, "bold"),
            text_color=self.colors["primary"]
        )
        self.total_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.total_amount = ctk.CTkLabel(
            self.checkout_frame,
            textvariable=self.total_var,
            font=("Roboto", 16, "bold"),
            text_color=self.colors["accent"]
        )
        self.total_amount.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        
        # Buttons
        self.buttons_frame = ctk.CTkFrame(
            self.cart_frame,
            fg_color="transparent"
        )
        self.buttons_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self.buttons_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Cancel button
        self.cancel_button = ctk.CTkButton(
            self.buttons_frame,
            text="Cancel",
            font=("Roboto", 14),
            fg_color="#E0E0E0",
            text_color=self.colors["primary"],
            hover_color="#BDBDBD",
            command=self.destroy
        )
        self.cancel_button.grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        
        # Checkout button
        self.checkout_button = ctk.CTkButton(
            self.buttons_frame,
            text="Complete Sale",
            font=("Roboto", 14),
            fg_color=self.colors["accent"],
            hover_color=self.colors["secondary"],
            command=self.complete_sale
        )
        self.checkout_button.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        # Initialize sale data
        self.cart_items = []
        self.menu_items = []
        
        # Load menu items
        self.load_menu_items()
        
        # Update the cart display
        self.update_cart_display()
    
    def load_menu_items(self):
        """Load menu items from data manager"""
        # Get menu items
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
        for widget in self.menu_items_frame.winfo_children():
            widget.destroy()
        
        # No items message
        if not items_to_display:
            no_items_label = ctk.CTkLabel(
                self.menu_items_frame, 
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
                self.menu_items_frame,
                text=category,
                font=("Roboto", 16, "bold"),
                text_color=self.colors["secondary"]
            )
            category_label.grid(row=row_counter, column=0, padx=10, pady=(15, 5), sticky="w")
            row_counter += 1
            
            # Items
            for item in category_items:
                item_frame = self.create_menu_item_button(item)
                item_frame.grid(row=row_counter, column=0, padx=10, pady=5, sticky="ew")
                row_counter += 1
    
    def create_menu_item_button(self, item):
        """Create a button for a menu item that adds it to the cart when clicked"""
        frame = ctk.CTkFrame(
            self.menu_items_frame,
            fg_color=self.colors["background"],
            border_width=1,
            border_color="#E0E0E0",
            corner_radius=8
        )
        frame.grid_columnconfigure(0, weight=3)
        frame.grid_columnconfigure(1, weight=1)
        
        # Check inventory
        inventory = self.data_manager.get_inventory()
        stock_quantity = 0
        
        for inv_item in inventory:
            if inv_item.get('name') == item.get('name'):
                stock_quantity = inv_item.get('quantity', 0)
                break
        
        # Item name and price
        name_text = item.get('name', 'Unnamed')
        price_text = f"₹{item.get('price', '0.00')}"
        
        name_label = ctk.CTkLabel(
            frame,
            text=name_text,
            font=("Roboto", 14),
            text_color=self.colors["primary"]
        )
        name_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        price_label = ctk.CTkLabel(
            frame,
            text=price_text,
            font=("Roboto", 14),
            text_color=self.colors["primary"]
        )
        price_label.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        
        # Add stock indicator
        stock_color = "#00B894" if stock_quantity > 0 else "#FF5252"
        stock_text = f"{stock_quantity} in stock" if stock_quantity > 0 else "Out of stock"
        
        stock_label = ctk.CTkLabel(
            frame,
            text=stock_text,
            font=("Roboto", 12),
            text_color=stock_color
        )
        stock_label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")
        
        # Add to cart button
        add_button = ctk.CTkButton(
            frame,
            text="+ Add",
            font=("Roboto", 12),
            fg_color=self.colors["accent"] if stock_quantity > 0 else "#E0E0E0",
            text_color="white" if stock_quantity > 0 else self.colors["primary"],
            hover_color=self.colors["secondary"] if stock_quantity > 0 else "#BDBDBD",
            width=80,
            command=lambda: self.add_to_cart(item) if stock_quantity > 0 else None
        )
        add_button.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="e")
        
        return frame
    
    def add_to_cart(self, item):
        """Add an item to the cart"""
        # Check if item is already in cart
        for cart_item in self.cart_items:
            if cart_item['id'] == item['id']:
                # Increment quantity
                cart_item['quantity'] += 1
                self.update_cart_display()
                return
        
        # Add new item to cart
        cart_item = {
            'id': item['id'],
            'name': item['name'],
            'price': item['price'],
            'quantity': 1
        }
        self.cart_items.append(cart_item)
        
        # Update cart display
        self.update_cart_display()
    
    def update_cart_display(self):
        """Update the cart display"""
        # Clear current cart display
        for widget in self.cart_items_frame.winfo_children():
            widget.destroy()
        
        # No items message
        if not self.cart_items:
            no_items_label = ctk.CTkLabel(
                self.cart_items_frame, 
                text="Cart is empty. Add items from the menu.",
                font=("Roboto", 14),
                text_color=self.colors["primary"]
            )
            no_items_label.grid(row=0, column=0, padx=20, pady=20)
            
            # Update total
            self.total_var.set("₹0.00")
            return
        
        # Display cart items
        total_amount = 0
        
        for i, item in enumerate(self.cart_items):
            item_frame = self.create_cart_item_display(item, i)
            item_frame.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
            
            # Add to total
            total_amount += item['price'] * item['quantity']
        
        # Update total
        self.total_var.set(f"₹{total_amount:.2f}")
    
    def create_cart_item_display(self, item, index):
        """Create a display for a cart item"""
        frame = ctk.CTkFrame(
            self.cart_items_frame,
            fg_color=self.colors["background"],
            border_width=1,
            border_color="#E0E0E0",
            corner_radius=8
        )
        frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Item name
        name_label = ctk.CTkLabel(
            frame,
            text=item['name'],
            font=("Roboto", 14),
            text_color=self.colors["primary"]
        )
        name_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Quantity controls
        qty_frame = ctk.CTkFrame(frame, fg_color="transparent")
        qty_frame.grid(row=0, column=1, padx=10, pady=10)
        
        # Decrease button
        decrease_button = ctk.CTkButton(
            qty_frame,
            text="-",
            font=("Roboto", 12, "bold"),
            fg_color=self.colors["secondary"],
            hover_color="#0771c0",
            width=30,
            height=30,
            command=lambda: self.update_cart_item_quantity(index, -1)
        )
        decrease_button.grid(row=0, column=0, padx=2)
        
        # Quantity label
        qty_label = ctk.CTkLabel(
            qty_frame,
            text=str(item['quantity']),
            font=("Roboto", 14),
            text_color=self.colors["primary"],
            width=30
        )
        qty_label.grid(row=0, column=1, padx=5)
        
        # Increase button
        increase_button = ctk.CTkButton(
            qty_frame,
            text="+",
            font=("Roboto", 12, "bold"),
            fg_color=self.colors["secondary"],
            hover_color="#0771c0",
            width=30,
            height=30,
            command=lambda: self.update_cart_item_quantity(index, 1)
        )
        increase_button.grid(row=0, column=2, padx=2)
        
        # Price
        price = item['price'] * item['quantity']
        price_label = ctk.CTkLabel(
            frame,
            text=f"₹{price:.2f}",
            font=("Roboto", 14),
            text_color=self.colors["primary"]
        )
        price_label.grid(row=0, column=2, padx=10, pady=10, sticky="e")
        
        # Remove button
        remove_button = ctk.CTkButton(
            frame,
            text="Remove",
            font=("Roboto", 12),
            fg_color="#E57373",
            hover_color="#C62828",
            width=80,
            command=lambda: self.remove_cart_item(index)
        )
        remove_button.grid(row=1, column=2, padx=10, pady=(0, 10), sticky="e")
        
        return frame
    
    def update_cart_item_quantity(self, index, change):
        """Update the quantity of an item in the cart"""
        self.cart_items[index]['quantity'] += change
        
        # Remove item if quantity becomes 0 or less
        if self.cart_items[index]['quantity'] <= 0:
            self.remove_cart_item(index)
        else:
            self.update_cart_display()
    
    def remove_cart_item(self, index):
        """Remove an item from the cart"""
        del self.cart_items[index]
        self.update_cart_display()
    
    def complete_sale(self):
        """Complete the sale and save it"""
        if not self.cart_items:
            messagebox.showinfo("Empty Cart", "Please add items to the cart before completing the sale.")
            return
        
        # Calculate total
        total_amount = sum(item['price'] * item['quantity'] for item in self.cart_items)
        
        # Prepare sale data
        sale_data = {
            'items': self.cart_items,
            'total_amount': total_amount,
            'date': date.today().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Save the sale
        success, message = self.data_manager.add_sale(sale_data)
        
        if success:
            messagebox.showinfo("Sale Complete", f"Sale completed successfully. Total: ₹{total_amount:.2f}")
            self.destroy()
        else:
            messagebox.showerror("Error", message)


class ExportOptionsDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message, options):
        super().__init__(parent)
        
        self.title(title)
        self.geometry("400x250")
        self.resizable(False, False)
        
        # Make it modal
        self.transient(parent)
        self.grab_set()
        
        # Message
        self.message_label = ctk.CTkLabel(
            self,
            text=message,
            font=("Roboto", 14)
        )
        self.message_label.pack(padx=20, pady=20)
        
        # Store result
        self.result = None
        
        # Create option buttons
        for option in options:
            button = ctk.CTkButton(
                self,
                text=option,
                font=("Roboto", 12),
                command=lambda o=option: self.select_option(o)
            )
            button.pack(padx=20, pady=5, fill="x")
        
        # Cancel button
        cancel_button = ctk.CTkButton(
            self,
            text="Cancel",
            font=("Roboto", 12),
            fg_color="#E0E0E0",
            text_color="#2D3436",
            hover_color="#BDBDBD",
            command=self.destroy
        )
        cancel_button.pack(padx=20, pady=15, fill="x")
    
    def select_option(self, option):
        """Set result and close the dialog"""
        self.result = option
        self.destroy()
