import os
import pandas as pd
from datetime import datetime
from tkinter import filedialog, messagebox

class ExportManager:
    def __init__(self, data_manager):
        """Initialize the export manager with a data manager instance"""
        self.data_manager = data_manager
    
    def export_menu_to_excel(self):
        """Export menu data to Excel file"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Export Menu to Excel"
        )
        
        if not filepath:
            return False, "Export cancelled"
        
        try:
            menu_items = self.data_manager.get_menu_items()
            
            if not menu_items:
                return False, "No menu items to export"
            
            # Create DataFrame from menu items
            df = pd.DataFrame(menu_items)
            
            # Reorder and select columns
            columns_order = ['name', 'category', 'price', 'description', 'shortcut', 'created_at', 'updated_at']
            available_columns = [col for col in columns_order if col in df.columns]
            
            df = df[available_columns]
            
            # Rename columns for better readability
            column_names = {
                'name': 'Name',
                'category': 'Category',
                'price': 'Price (₹)',
                'description': 'Description',
                'shortcut': 'Keyboard Shortcut',
                'created_at': 'Created Date',
                'updated_at': 'Last Updated'
            }
            
            df.rename(columns={col: column_names.get(col, col) for col in df.columns}, inplace=True)
            
            # Write to Excel
            df.to_excel(filepath, index=False, sheet_name='Menu Items')
            
            return True, f"Menu exported successfully to {filepath}"
        
        except Exception as e:
            return False, f"Export failed: {str(e)}"
    
    def export_sales_to_excel(self, date_filter=None):
        """Export sales data to Excel file"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Export Sales to Excel"
        )
        
        if not filepath:
            return False, "Export cancelled"
        
        try:
            sales = self.data_manager.get_sales(date_filter)
            
            if not sales:
                return False, f"No sales data to export{' for selected date' if date_filter else ''}"
            
            # Create DataFrame for sales transactions
            sales_df = pd.DataFrame(sales)
            
            # Add exported time
            export_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Create Excel writer to work with multiple sheets
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Process sales data for transactions sheet
                if 'items' in sales_df.columns:
                    # Save the items column before dropping it
                    items_data = sales_df['items'].copy()
                    sales_df = sales_df.drop('items', axis=1)
                
                # Rename columns for better readability
                column_names = {
                    'id': 'Sale ID',
                    'timestamp': 'Date & Time',
                    'date': 'Date',
                    'total_amount': 'Total Amount (₹)'
                }
                
                sales_df.rename(columns={col: column_names.get(col, col) for col in sales_df.columns}, inplace=True)
                
                # Write transactions sheet
                sales_df.to_excel(writer, index=False, sheet_name='Transactions')
                
                # Create items sheet with detailed sales
                items_rows = []
                for i, sale in enumerate(sales):
                    sale_id = sale.get('id', i)
                    timestamp = sale.get('timestamp', '')
                    
                    for item in sale.get('items', []):
                        items_rows.append({
                            'Sale ID': sale_id,
                            'Date & Time': timestamp,
                            'Item Name': item.get('name', ''),
                            'Quantity': item.get('quantity', 0),
                            'Unit Price (₹)': item.get('price', 0),
                            'Total Price (₹)': item.get('quantity', 0) * item.get('price', 0)
                        })
                
                if items_rows:
                    items_df = pd.DataFrame(items_rows)
                    items_df.to_excel(writer, index=False, sheet_name='Items Sold')
                
                # Create summary sheet if date filter is applied
                if date_filter:
                    summary = self.data_manager.get_daily_sales_summary(date_filter)
                    
                    # Format summary data
                    summary_data = {
                        'Metric': ['Date', 'Total Revenue (₹)', 'Total Transactions'],
                        'Value': [
                            summary.get('date', ''),
                            summary.get('total_revenue', 0),
                            summary.get('total_transactions', 0)
                        ]
                    }
                    
                    # Add items breakdown
                    for item, qty in summary.get('items_sold', {}).items():
                        summary_data['Metric'].append(f'Item: {item}')
                        summary_data['Value'].append(qty)
                    
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, index=False, sheet_name='Summary')
                
                # Add export metadata
                metadata = pd.DataFrame({
                    'Information': ['Export Date', 'Date Filter', 'Total Sales', 'Total Amount'],
                    'Value': [
                        export_time,
                        date_filter if date_filter else 'All dates',
                        len(sales),
                        sales_df['Total Amount (₹)'].sum() if 'Total Amount (₹)' in sales_df.columns else 0
                    ]
                })
                metadata.to_excel(writer, index=False, sheet_name='Metadata')
            
            return True, f"Sales data exported successfully to {filepath}"
        
        except Exception as e:
            return False, f"Export failed: {str(e)}"
    
    def export_inventory_to_excel(self):
        """Export inventory data to Excel file"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Export Inventory to Excel"
        )
        
        if not filepath:
            return False, "Export cancelled"
        
        try:
            inventory = self.data_manager.get_inventory()
            
            if not inventory:
                return False, "No inventory data to export"
            
            # Get menu items for price information
            menu_items = self.data_manager.get_menu_items()
            price_lookup = {item.get('name'): item.get('price', 0) for item in menu_items}
            
            # Create DataFrame
            df = pd.DataFrame(inventory)
            
            # Add value column
            df['price'] = df['name'].map(price_lookup)
            df['value'] = df['quantity'] * df['price']
            
            # Reorder columns
            columns_order = ['name', 'quantity', 'price', 'value', 'last_updated']
            available_columns = [col for col in columns_order if col in df.columns]
            df = df[available_columns]
            
            # Rename columns for better readability
            column_names = {
                'name': 'Item Name',
                'quantity': 'Quantity',
                'price': 'Unit Price (₹)',
                'value': 'Total Value (₹)',
                'last_updated': 'Last Updated'
            }
            
            df.rename(columns={col: column_names.get(col, col) for col in df.columns}, inplace=True)
            
            # Add summary information
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Inventory')
                
                # Create summary sheet
                summary_data = {
                    'Metric': [
                        'Total Inventory Items',
                        'Total Quantity',
                        'Total Value (₹)',
                        'Low Stock Items (≤5)',
                        'Out of Stock Items (0)'
                    ],
                    'Value': [
                        len(df),
                        df['Quantity'].sum(),
                        df['Total Value (₹)'].sum(),
                        len(df[df['Quantity'] <= 5]),
                        len(df[df['Quantity'] == 0])
                    ]
                }
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, index=False, sheet_name='Summary')
                
                # Add export metadata
                metadata = pd.DataFrame({
                    'Information': ['Export Date', 'Total Items'],
                    'Value': [
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        len(inventory)
                    ]
                })
                metadata.to_excel(writer, index=False, sheet_name='Metadata')
            
            return True, f"Inventory exported successfully to {filepath}"
        
        except Exception as e:
            return False, f"Export failed: {str(e)}"
    
    def generate_daily_report(self, date_filter=None):
        """Generate and export a daily report"""
        if not date_filter:
            date_filter = datetime.now().strftime('%Y-%m-%d')
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=f"Daily_Report_{date_filter}",
            title="Export Daily Report"
        )
        
        if not filepath:
            return False, "Export cancelled"
        
        try:
            # Get daily sales summary
            summary = self.data_manager.get_daily_sales_summary(date_filter)
            
            # Get sales transactions for the day
            sales = self.data_manager.get_sales(date_filter)
            
            # Create Excel writer for multiple sheets
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Summary sheet
                summary_data = {
                    'Metric': ['Date', 'Total Revenue (₹)', 'Total Transactions'],
                    'Value': [
                        summary.get('date', ''),
                        summary.get('total_revenue', 0),
                        summary.get('total_transactions', 0)
                    ]
                }
                
                # Add items breakdown to summary
                for item, qty in summary.get('items_sold', {}).items():
                    summary_data['Metric'].append(f'Item: {item}')
                    summary_data['Value'].append(qty)
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, index=False, sheet_name='Summary')
                
                # Transactions sheet
                if sales:
                    sales_df = pd.DataFrame(sales)
                    
                    # Process sales data
                    if 'items' in sales_df.columns:
                        # Save the items column before dropping it
                        items_data = sales_df['items'].copy()
                        sales_df = sales_df.drop('items', axis=1)
                    
                    # Rename columns for better readability
                    column_names = {
                        'id': 'Sale ID',
                        'timestamp': 'Date & Time',
                        'date': 'Date',
                        'total_amount': 'Total Amount (₹)'
                    }
                    
                    sales_df.rename(columns={col: column_names.get(col, col) for col in sales_df.columns}, inplace=True)
                    
                    # Write transactions sheet
                    sales_df.to_excel(writer, index=False, sheet_name='Transactions')
                    
                    # Items sheet with detailed sales
                    items_rows = []
                    for i, sale in enumerate(sales):
                        sale_id = sale.get('id', i)
                        timestamp = sale.get('timestamp', '')
                        
                        for item in sale.get('items', []):
                            items_rows.append({
                                'Sale ID': sale_id,
                                'Date & Time': timestamp,
                                'Item Name': item.get('name', ''),
                                'Quantity': item.get('quantity', 0),
                                'Unit Price (₹)': item.get('price', 0),
                                'Total Price (₹)': item.get('quantity', 0) * item.get('price', 0)
                            })
                    
                    if items_rows:
                        items_df = pd.DataFrame(items_rows)
                        items_df.to_excel(writer, index=False, sheet_name='Items Sold')
                
                # Add export metadata
                metadata = pd.DataFrame({
                    'Information': ['Report Date', 'Export Date', 'Total Sales', 'Total Revenue'],
                    'Value': [
                        date_filter,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        summary.get('total_transactions', 0),
                        summary.get('total_revenue', 0)
                    ]
                })
                metadata.to_excel(writer, index=False, sheet_name='Metadata')
            
            return True, f"Daily report exported successfully to {filepath}"
        
        except Exception as e:
            return False, f"Export failed: {str(e)}"
    
    def generate_inventory_alert_report(self):
        """Generate and export an inventory alert report for low stock items"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile="Inventory_Alert_Report",
            title="Export Inventory Alert Report"
        )
        
        if not filepath:
            return False, "Export cancelled"
        
        try:
            inventory = self.data_manager.get_inventory()
            
            if not inventory:
                return False, "No inventory data to export"
            
            # Filter low stock items (quantity <= 5)
            low_stock_items = [item for item in inventory if item.get('quantity', 0) <= 5]
            
            if not low_stock_items:
                return False, "No low stock items found"
            
            # Get menu items for price information
            menu_items = self.data_manager.get_menu_items()
            price_lookup = {item.get('name'): item.get('price', 0) for item in menu_items}
            
            # Create DataFrame
            df = pd.DataFrame(low_stock_items)
            
            # Sort by quantity (ascending)
            df = df.sort_values(by='quantity')
            
            # Add value column
            df['price'] = df['name'].map(price_lookup)
            
            # Add status column
            df['status'] = df['quantity'].apply(lambda q: 'Out of Stock' if q == 0 else 'Low Stock')
            
            # Reorder columns
            columns_order = ['name', 'quantity', 'status', 'price', 'last_updated']
            available_columns = [col for col in columns_order if col in df.columns]
            df = df[available_columns]
            
            # Rename columns for better readability
            column_names = {
                'name': 'Item Name',
                'quantity': 'Quantity',
                'status': 'Status',
                'price': 'Unit Price (₹)',
                'last_updated': 'Last Updated'
            }
            
            df.rename(columns={col: column_names.get(col, col) for col in df.columns}, inplace=True)
            
            # Write to Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Low Stock Items')
                
                # Create summary sheet
                summary_data = {
                    'Metric': [
                        'Report Date',
                        'Total Low Stock Items',
                        'Items with Quantity > 0',
                        'Out of Stock Items (0)'
                    ],
                    'Value': [
                        datetime.now().strftime('%Y-%m-%d'),
                        len(df),
                        len(df[df['Quantity'] > 0]),
                        len(df[df['Quantity'] == 0])
                    ]
                }
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, index=False, sheet_name='Summary')
            
            return True, f"Inventory alert report exported successfully to {filepath}"
        
        except Exception as e:
            return False, f"Export failed: {str(e)}"
